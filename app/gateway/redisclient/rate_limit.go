package redisclient

import (
	"fmt"
	"log"
	"time"

	"github.com/go-redis/redis/v8"
)

func RateLimit(clientIP string, limit int, window time.Duration) bool {
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
