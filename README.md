# Real-Time Stock Price Tracker
---
Real-Time Stock Price Tracker, code name `Lizards`, it is a platform where users can track stock prices in real-time. One microservice manages WebSocket connections to provide real-time updates, and the other microservice fetches stock data from external APIs. 

### Application Suitability
---
* Scalability
Real-time stock data requires high throughput, which can vary depending on the number of users and the volume of trades. 
Microservices allow individual services to scale independently based on demand.

* Separation of Concerns
Each component of the application, such as stock price fetching, user notifications, data caching, and analytics, 
can be handled by separate microservices. This isolation of functionality ensures better code maintainability and 
allows for independent development.

* Performance Optimization
Real-time systems demand low-latency responses, especially when handling fast-moving stock prices. 
Microservices enable you to use the best-suited technologies for each part of the application, like WebSockets for real-time 
communication, without affecting other components.

* Fault Isolation and Resilience
If a service that handles historical data fails, it won’t necessarily impact the real-time stock price stream, 
as each service operates independently. This leads to better fault tolerance and resilience in the system.

* Flexible Deployment
Services like data aggregation, notifications, and real-time updates can be deployed and updated independently, 
allowing for faster iteration and continuous integration without downtime for the entire system.

### Service Boundaries
---
![Architecture Overview](media/lab1-pad.drawio.png)

* **Data Ingestion Microservice** -- gathering data about the stock prices from the web, or free APIs. 
* **Data Processing Microservice** -- cleaning and structuring the data.
* **Data Provider Microservice** -- creating a websocket connection with the client for quick updates.   

### Technology Stack 
---
#### Gateway
The following points will be the primary responsibility of the API Gateway:

* **Request Routing** - the routing will be done in pair with the Service Discovery;
* **Load Balancing** - balance the load across multiple instances of a microservice;
* **Rate Limiting** - limit the number of requests a client can make to prevent abuse; 
* **Caching** - store responses from microservices temporarily to reduce latency and improve performance for frequently requested data.

For this reason, Golang was chosen. The build-in libraries, with a great coroutine schedule that offers "cheap" green threads, is the best pick for this kind of tasks.

#### Service Discovery 
Following the same logic, and due to the constrains of the laboratory work, Golang is chosen, as the development language of it.

#### Microservices
Due to the vast number of available libraries, and the nature of the deployment, Python is chosen. For each microservice the following frameworks will be used:

* **Data Ingestion Microservice:** scrapy, pymongo, FastAPI, Playwright, grpcio, pika, prometheus_client; 
* **Data Processing Microservice** schema, grpcio, prometheus_client, pytest; 
* **Data Provider Microservice** FastAPI, websockets, SQLAlchemy, pika, prometheus_client; 

### Data Management
---
#### Workflow
When a client runs the application a websocket connect is created to facilitate real-time data updates from the `Data Provider Microservice`. This microservice is taking data from the `PostgreSQL` database, where all the data is well structured. This database is read-only for the previously mentioned microservice. The updates in the databases will be performed by a worker from within the `Data Provider Microservice`. That worker will be the consumer of the `RabbitMQ` queue.  

The producer is the `Data Ingestion Microservice`. It consists primarly of the following parts:
1. **Ingestion** - a collection of scrapers or data miners are getting data from the web, about the current stocks prices;
2. **Storing** - all the found raw data will be stored in the `MongoDB`. 
3. **Transforming** - a step performed by the `Data Processing Microservice`, where the raw data from the web is converted based on a scheme and validated before being send back;
4. **Producing** - the transformed data is send via a worker to the queue, it being the producer of the queue. 

#### Contracts

**Service Discovery**




