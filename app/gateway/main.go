package main

import (
	"log"
	"net/http"
	"time"

	"context"

	"github.com/go-redis/redis/v8"
	"github.com/gorilla/mux"
	"github.com/hashicorp/consul/api"
	"golang.org/x/time/rate"
)

var (
	// Set rate limit to 5 requests per second with a burst of 10
	rateLimiter = rate.NewLimiter(5, 10)
	redisClient *redis.Client
)

func main() {
	// Initialize the Redis client for caching
	initRedis()

	// Initialize Consul client for service discovery
	consulClient := initConsul()

	// Initialize the router
	router := mux.NewRouter()

	// Apply middleware for rate limiting and caching
	router.Use(rateLimitMiddleware)

	// Define routes
	router.HandleFunc("/service1", loadBalanceHandler(consulClient, "service1")).Methods("GET")
	router.HandleFunc("/service2", loadBalanceHandler(consulClient, "service2")).Methods("GET")

	// Start the server
	log.Println("API Gateway is running on :8080")
	if err := http.ListenAndServe(":8080", router); err != nil {
		log.Fatalf("Error starting server: %s", err)
	}
}

func initRedis() {
	redisClient = redis.NewClient(&redis.Options{
		Addr: "localhost:6379", // Redis server address
		DB:   0,                // Default DB
	})
}

func initConsul() *api.Client {
	consulConfig := api.DefaultConfig()
	client, err := api.NewClient(consulConfig)
	if err != nil {
		log.Fatalf("Error initializing Consul: %s", err)
	}
	return client
}

// Rate limiting middleware
func rateLimitMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if !rateLimiter.Allow() {
			http.Error(w, "Too Many Requests", http.StatusTooManyRequests)
			return
		}
		next.ServeHTTP(w, r)
	})
}

// Load balancing and service discovery handler
func loadBalanceHandler(client *api.Client, serviceName string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		// Discover services
		services, _, err := client.Health().Service(serviceName, "", true, nil)
		if err != nil || len(services) == 0 {
			http.Error(w, "Service unavailable", http.StatusServiceUnavailable)
			return
		}

		// Implement load balancing (e.g., round-robin)
		target := services[0].Service.Address + ":" + string(services[0].Service.Port)

		// Implement caching logic
		cacheKey := r.RequestURI
		cachedResponse, err := redisClient.Get(context.Background(), cacheKey).Result()
		if err == redis.Nil {
			// If cache miss, forward request to target service
			resp, err := http.Get("http://" + target + r.RequestURI)
			if err != nil {
				http.Error(w, "Service Error", http.StatusServiceUnavailable)
				return
			}
			defer resp.Body.Close()

			// Cache the response
			redisClient.Set(context.Background(), cacheKey, resp.Body, time.Minute*10)

			// Write response to client
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(resp.StatusCode)
			w.Write([]byte("Forwarded response"))
		} else if err != nil {
			http.Error(w, "Cache Error", http.StatusInternalServerError)
			return
		} else {
			// Return cached response
			w.Write([]byte(cachedResponse))
		}
	}
}
