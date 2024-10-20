package main

import (
	"fmt"
	"gateway-consul/circuitbreaker"
	"gateway-consul/constants"
	"gateway-consul/loadbalancer"
	"gateway-consul/monitor"
	"gateway-consul/redisclient"
	"gateway-consul/servicediscoveryclient"
	"io"
	"log"
	"net"
	"net/http"
	"strings"
	"sync/atomic"
	"time"
)

var httpClient = &http.Client{
	Timeout: 10 * time.Second, // Set the timeout duration (5 seconds in this case)
}

func handleRequest(w http.ResponseWriter, r *http.Request) {
	clientIP := r.RemoteAddr

	// Rate limit check
	if !redisclient.RateLimit(clientIP, constants.RateLimitPerMinute, time.Minute) {
		http.Error(w, "Rate limit exceeded. Try again later.", http.StatusTooManyRequests)
		return
	}

	// Increment the request count
	atomic.AddInt64(&monitor.RequestCount, 1)

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
	cachedResponse, isCached := redisclient.GetCachedResponse(cacheKey)
	if isCached {
		log.Printf("Cache hit for %s\n", r.URL.Path)
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(cachedResponse))
		return
	}

	log.Printf("Cache miss for %s\n", r.URL.Path)

	// Discover the target service using Consul
	services, err := servicediscoveryclient.DiscoverService(serviceName)
	if err != nil || len(services) == 0 {
		http.Error(w, "Service discovery failed", http.StatusServiceUnavailable)
		return
	}

	target := loadbalancer.GetNextService(services)
	proxyURL := fmt.Sprintf("http://%s%s", target, r.URL.Path)

	// Retry logic: number of retries before failing
	retries := 0

	var lastError error

	for retries < constants.MaxRetries {
		_, err = circuitbreaker.CB.Execute(func() (interface{}, error) {
			// Forward the request to the microservice
			resp, err := httpClient.Get(proxyURL)
			if err != nil {
				return nil, err
			}
			defer resp.Body.Close()

			// Copy the response back to the client
			body, err := io.ReadAll(resp.Body)
			if err != nil {
				return nil, err
			}

			// Cache the response with a TTL of 60 seconds
			redisclient.CacheResponse(cacheKey, string(body), constants.CacheTTL)

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

		log.Printf("Retrying request (%d/%d) for %s due to error: %v\n", retries, constants.MaxRetries, serviceName, err)
	}

	// After retries, return error if still failing
	if lastError != nil {
		log.Printf("Failed after %d retries: %v\n", retries, lastError)
		http.Error(w, "Service is currently unavailable after retries", http.StatusServiceUnavailable)
	}
}

func main() {
	redisclient.InitRedis()
	circuitbreaker.InitCircuitBreaker()

	monitor.MonitorServiceLoad("python-microservice")

	http.HandleFunc("/", handleRequest)
	log.Println("API Gateway running on port 8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
