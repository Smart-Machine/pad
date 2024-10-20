package monitor

import (
	"log"
	"sync/atomic"
	"time"
)

const criticalLoad = 60

var RequestCount int64

func raiseAlert(serviceName string, load int64) {
	log.Printf("ALERT: Service %s is under critical load! %d requests/second\n", serviceName, load)
}

func MonitorServiceLoad(serviceName string) {
	// Reset the request count every second
	ticker := time.NewTicker(1 * time.Second)

	go func() {
		for range ticker.C {
			// Get the current request count
			currentCount := atomic.LoadInt64(&RequestCount)

			// Check if the load exceeds the critical threshold
			if currentCount >= criticalLoad {
				raiseAlert(serviceName, currentCount)
			}

			// Reset the request count for the next second
			atomic.StoreInt64(&RequestCount, 0)
		}
	}()
}
