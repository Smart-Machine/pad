package servicediscoveryclient

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
)

type ServiceResponse struct {
	Services []string `json:"services"`
}

func DiscoverService(serviceName string) ([]string, error) {
	url := fmt.Sprintf("http://service-discovery:8081/service/%s", serviceName)
	resp, err := http.Get(url)
	if err != nil {
		return nil, fmt.Errorf("could not connect to service discovery: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		bodyBytes, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("error from discovery service: %v", string(bodyBytes))
	}

	var serviceResponse ServiceResponse
	err = json.NewDecoder(resp.Body).Decode(&serviceResponse)
	if err != nil {
		return nil, fmt.Errorf("could not decode response: %v", err)
	}

	return serviceResponse.Services, nil
}
