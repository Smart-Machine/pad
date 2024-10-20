package circuitbreaker

import (
	"log"

	"gateway-consul/constants"

	"github.com/sony/gobreaker"
)

var CB *gobreaker.CircuitBreaker

func InitCircuitBreaker() {
	settings := gobreaker.Settings{
		Name:        "API Gateway Circuit Breaker",
		MaxRequests: constants.MaxRetries,
		Interval:    10 * 1e9, // 60 sec (default)
		Timeout:     5 * 1e9,  // 30 sec (default)
		ReadyToTrip: func(counts gobreaker.Counts) bool {
			log.Printf("Consecutive failures: %d\n", counts.ConsecutiveFailures)
			return counts.ConsecutiveFailures > 3
		},
		OnStateChange: func(name string, from gobreaker.State, to gobreaker.State) {
			log.Printf("Circuit breaker state change: %s -> %s\n", from.String(), to.String())
		},
	}

	CB = gobreaker.NewCircuitBreaker(settings)
}
