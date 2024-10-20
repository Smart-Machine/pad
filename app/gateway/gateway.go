package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net"
	"net/http"
	"strings"
	"sync/atomic"
	"time"

	"github.com/go-redis/redis/v8"
	"github.com/sony/gobreaker"
)

const maxRetries = 3
const rateLimitPerMinute = 10
const criticalLoad = 60
const cacheTTL = 60 * time.Second

var (
	index        uint64
	requestCount int64
	rdb          *redis.Client
	cb           *gobreaker.CircuitBreaker
	ctx          = context.Background()
	httpClient   = &http.Client{
		Timeout: 5 * time.Second, // Set the timeout duration (5 seconds in this case)
	}
)

type ServiceResponse struct {
	Services []string `json:"services"`
}

func initRedis() {
	rdb = redis.NewClient(&redis.Options{
		Addr: "redis:6379", // Redis is running in Docker
	})
}

func initCircuitBreaker() {
	settings := gobreaker.Settings{
		Name:        "API Gateway Circuit Breaker",
		MaxRequests: maxRetries,
		Interval:    10 * 1e9, // 60 sec
		Timeout:     5 * 1e9,  // 30 sec
		ReadyToTrip: func(counts gobreaker.Counts) bool {
			log.Printf("Consecutive failures: %d\n", counts.ConsecutiveFailures)
			return counts.ConsecutiveFailures > 3
		},
		OnStateChange: func(name string, from gobreaker.State, to gobreaker.State) {
			log.Printf("Circuit breaker state change: %s -> %s\n", from.String(), to.String())
		},
	}

	cb = gobreaker.NewCircuitBreaker(settings)
}

func raiseAlert(serviceName string, load int64) {
	log.Printf("ALERT: Service %s is under critical load! %d requests/second\n", serviceName, load)
}

func monitorServiceLoad(serviceName string) {
	// Reset the request count every second
	ticker := time.NewTicker(1 * time.Second)

	go func() {
		for range ticker.C {
			// Get the current request count
			currentCount := atomic.LoadInt64(&requestCount)

			// Check if the load exceeds the critical threshold
			if currentCount >= criticalLoad {
				raiseAlert(serviceName, currentCount)
			}

			// Reset the request count for the next second
			atomic.StoreInt64(&requestCount, 0)
		}
	}()
}

func rateLimit(clientIP string, limit int, window time.Duration) bool {
	key := fmt.Sprintf("rate-limit:%s", clientIP)
	count, err := rdb.Get(ctx, key).Int()

	if err == redis.Nil {
		// Key doesn't exist, create it with initial value and expiration
		rdb.Set(ctx, key, 1, window)
		return true
	}

	if err != nil {
		log.Printf("Error accessing Redis: %v", err)
		return false
	}

	if count >= limit {
		// Rate limit exceeded
		return false
	}

	// Increment the counter
	rdb.Incr(ctx, key)
	return true
}

// Cache responses in Redis with a given expiration
func cacheResponse(key string, value string, expiration time.Duration) {
	err := rdb.Set(ctx, key, value, expiration).Err()
	if err != nil {
		log.Printf("Failed to cache response: %v\n", err)
	}
}

// Get cached response from Redis
func getCachedResponse(key string) (string, bool) {
	val, err := rdb.Get(ctx, key).Result()
	if err == redis.Nil {
		return "", false // Cache miss
	} else if err != nil {
		log.Printf("Failed to get cache: %v\n", err)
		return "", false
	}
	return val, true // Cache hit
}

func discoverService(serviceName string) ([]string, error) {
	url := fmt.Sprintf("http://service-discovery:8081/service/%s", serviceName)
	resp, err := http.Get(url)
	if err != nil {
		return nil, fmt.Errorf("could not connect to service discovery: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		bodyBytes, _ := ioutil.ReadAll(resp.Body)
		return nil, fmt.Errorf("error from discovery service: %v", string(bodyBytes))
	}

	var serviceResponse ServiceResponse
	err = json.NewDecoder(resp.Body).Decode(&serviceResponse)
	if err != nil {
		return nil, fmt.Errorf("could not decode response: %v", err)
	}

	return serviceResponse.Services, nil
}

func getNextService(services []string) string {
	nextIndex := atomic.AddUint64(&index, 1)
	return services[nextIndex%uint64(len(services))]
}

func handleRequest(w http.ResponseWriter, r *http.Request) {
	clientIP := r.RemoteAddr

	// Rate limit check
	if !rateLimit(clientIP, rateLimitPerMinute, time.Minute) {
		http.Error(w, "Rate limit exceeded. Try again later.", http.StatusTooManyRequests)
		return
	}

	// Increment the request count
	atomic.AddInt64(&requestCount, 1)

	// Determine which service to forward to based on the path
	var serviceName string

	if strings.HasPrefix(r.URL.Path, "/service1/") {
		serviceName = "python-microservice"
	} else if strings.HasPrefix(r.URL.Path, "/service2/") {
		serviceName = "python-service2"
	} else {
		http.Error(w, "Service not found", http.StatusNotFound)
		return
	}

	// Create a cache key based on the URL path
	cacheKey := fmt.Sprintf("cache:%s", r.URL.Path)

	// Check cache first
	cachedResponse, isCached := getCachedResponse(cacheKey)
	if isCached {
		log.Printf("Cache hit for %s\n", r.URL.Path)
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(cachedResponse))
		return
	}

	log.Printf("Cache miss for %s\n", r.URL.Path)

	// Discover the target service using Consul
	services, err := discoverService(serviceName)
	if err != nil || len(services) == 0 {
		http.Error(w, "Service discovery failed", http.StatusServiceUnavailable)
		return
	}

	target := getNextService(services)
	proxyURL := fmt.Sprintf("http://%s%s", target, r.URL.Path)

	// Retry logic: number of retries before failing
	retries := 0

	var lastError error

	for retries < maxRetries {
		_, err = cb.Execute(func() (interface{}, error) {
			// Forward the request to the microservice
			resp, err := httpClient.Get(proxyURL)
			if err != nil {
				return nil, err
			}
			defer resp.Body.Close()

			// Copy the response back to the client
			body, err := ioutil.ReadAll(resp.Body)
			if err != nil {
				return nil, err
			}

			// Cache the response with a TTL of 60 seconds
			cacheResponse(cacheKey, string(body), cacheTTL)

			// Return the response to the client
			w.WriteHeader(resp.StatusCode)
			w.Write(body)

			return nil, nil
		})

		if err == nil {
			// If the request succeeds, break out of the retry loop
			return
		}

		// If the request fails, increment the retry counter and retry
		retries++
		lastError = err

		// Check if it's a timeout error
		if nErr, ok := err.(net.Error); ok && nErr.Timeout() {
			log.Printf("Request to %s timed out: %v\n", proxyURL, err)
			http.Error(w, "Request timed out", http.StatusGatewayTimeout)
			return
		}

		log.Printf("Retrying request (%d/%d) for %s due to error: %v\n", retries, maxRetries, serviceName, err)
	}

	// After retries, return error if still failing
	if lastError != nil {
		log.Printf("Failed after %d retries: %v\n", retries, lastError)
		http.Error(w, "Service is currently unavailable after retries", http.StatusServiceUnavailable)
	}
}

func main() {
	initRedis()
	initCircuitBreaker()

	monitorServiceLoad("python-microservice")

	http.HandleFunc("/", handleRequest)
	log.Println("API Gateway running on port 8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
