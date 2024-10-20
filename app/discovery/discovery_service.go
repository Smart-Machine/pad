package main

import (
	"fmt"
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/hashicorp/consul/api"
)

var consulClient *api.Client

func initConsul() {
	config := api.DefaultConfig()
	var err error
	consulClient, err = api.NewClient(config)
	if err != nil {
		log.Fatalf("Error creating Consul client: %v", err)
	}
}

func getService(c *gin.Context) {
	serviceName := c.Param("service")
	services, _, err := consulClient.Health().Service(serviceName, "", true, nil)
	if err != nil || len(services) == 0 {
		c.JSON(http.StatusNotFound, gin.H{"error": "service not found"})
		return
	}

	var serviceAddresses []string
	for _, service := range services {
		address := fmt.Sprintf("%s:%d", service.Service.Address, service.Service.Port)
		serviceAddresses = append(serviceAddresses, address)
	}
	c.JSON(http.StatusOK, gin.H{"services": serviceAddresses})
}

func main() {
	initConsul()
	router := gin.Default()
	router.GET("/service/:service", getService)
	router.Run(":8081")
}
