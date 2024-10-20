#!/bin/bash

# Number of requests to send
total_requests=1000
# URL of the API Gateway (adjust this if necessary)
url="http://localhost:8080/service1/data"

# Send multiple requests in parallel
for i in $(seq 1 $total_requests); do
  curl -s -o /dev/null $url &
done

# Wait for all requests to finish
wait

echo "Sent $total_requests requests to $url"
