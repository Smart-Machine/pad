package redisclient

import (
	"context"

	"github.com/go-redis/redis/v8"
)

var rdb *redis.Client
var ctx = context.Background()

func InitRedis() {
	rdb = redis.NewClient(&redis.Options{
		Addr: "redis:6379", // Redis is running in Docker
	})
}
