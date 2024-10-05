# Variables
MONGO_DOCKER_IMAGE = mongo
MONGO_CONTAINER_NAME = mongodb
MONGO_HOST_PORT = 27017
MONGO_DATA_DIR = ./data

RABBIT_DOCKER_IMAGE = rabbitmq:management 
RABBIT_CONTAINER_NAME = rabbitmq 
RABBIT_HOST_PORT = 5672
RABBIT_UI_PORT = 15672

# Pull MongoDB Docker image
.PHONY: pull-mongodb
pull-mongodb:
	docker pull $(MONGO_DOCKER_IMAGE)

# Run MongoDB container with data persistence
.PHONY: run-mongodb
run-mongodb:
	mkdir -p $(MONGO_DATA_DIR)
	docker run -d -p $(MONGO_HOST_PORT):27017 --name $(MONGO_CONTAINER_NAME) -v $(MONGO_DATA_DIR):/data/db $(MONGO_DOCKER_IMAGE)

# Stop MongoDB container
.PHONY: stop-mongodb
stop-mongodb:
	docker stop $(MONGO_CONTAINER_NAME)

# Start MongoDB container if it's already created
.PHONY: start-mongodb
start-mongodb:
	docker start $(MONGO_CONTAINER_NAME)

# Remove MongoDB container
.PHONY: remove-mongodb
remove-mongodb:
	docker rm -f $(MONGO_CONTAINER_NAME)

# Connect to MongoDB shell inside the container
.PHONY: shell-mongodb
shell-mongodb:
	docker exec -it $(MONGO_CONTAINER_NAME) mongosh 

# Check if MongoDB container is running
.PHONY: status-mongodb
status-mongodb:
	docker ps --filter name=$(MONGO_CONTAINER_NAME)

# Clean up data directory
.PHONY: clean-data
clean-data:
	rm -rf $(MONGO_DATA_DIR)

# Pull RabbitMQ:Management Docker Image
.PHONY: pull-rabbitmq
pull-rabbitmq:
	docker pull $(RABBIT_DOCKER_IMAGE) 

# Run RabbitMQ:Management container
.PHONY: run-rabbitmq
run-rabbitmq:
	docker run -d --hostname rbbtmq --name $(RABBIT_CONTAINER_NAME) -p $(RABBIT_HOST_PORT):5672 -p $(RABBIT_UI_PORT):15672 $(RABBIT_DOCKER_IMAGE) 

# Stop RabbitMQ container
.PHONY: stop-rabbitmq
stop-rabbitmq:
	docker stop $(RABBIT_CONTAINER_NAME)

# Start RabbitMQ container if it's already created
.PHONY: start-rabbitmq
start-rabbitmq:
	docker start $(RABBIT_CONTAINER_NAME)

# Remove RabbitMQ container
.PHONY: remove-rabbitmq
remove-rabbitmq:
	docker rm -f $(RABBIT_CONTAINER_NAME)

# Connect to RabbitMQ shell inside the container
.PHONY: shell-rabbitmq
shell-rabbitmq:
	docker exec -it $(RABBIT_CONTAINER_NAME) /bin/bash

# Check if RabbitMQ container is running
.PHONY: status-rabbitmq
status-rabbitmq:
	docker ps --filter name=$(RABBIT_CONTAINER_NAME)

# Run crawler alpha
.PHONY: crawl-alpha
crawl-alpha:
	cd scrapers && PYTHONPATH=$(pwd) python -m scrapy crawl alpha

# Run crawlers
.PHONY: crawl
crawl: crawl-alpha
	@echo "Starting all Scrapy spiders..."
	$(MAKE) crawl-alpha
	@echo "All scrapers have been run."

# Run API
.PHONY: api
api:
	@echo "Starting the server..."
	@echo "Listening on port 8000"
	@uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4