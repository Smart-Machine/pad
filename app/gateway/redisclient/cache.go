package redisclient

import (
	"log"
	"time"

	"github.com/go-redis/redis/v8"
)

// Cache responses in Redis with a given expiration
func CacheResponse(key string, value string, expiration time.Duration) {
	err := rdb.Set(ctx, key, value, expiration).Err()
	if err != nil {
		log.Printf("Failed to cache response: %v\n", err)
	}
}

// Get cached response from Redis
func GetCachedResponse(key string) (string, bool) {
	val, err := rdb.Get(ctx, key).Result()
	if err == redis.Nil {
		return "", false // Cache miss
	} else if err != nil {
		log.Printf("Failed to get cache: %v\n", err)
		return "", false
	}
	return val, true // Cache hit
}
