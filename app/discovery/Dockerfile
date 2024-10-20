# Build Stage
FROM golang:1.20-alpine as builder

WORKDIR /app

COPY . .

RUN go mod tidy 

RUN go build -o discovery_service .

# Final Stage
FROM alpine:latest

WORKDIR /app

COPY --from=builder /app/discovery_service /app/discovery_service

EXPOSE 8081

CMD ["./discovery_service"]
