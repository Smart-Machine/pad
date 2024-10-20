from fastapi import FastAPI
import socket
import uvicorn
from consul import Consul

app = FastAPI()
consul = Consul()

def register_with_consul():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    service_id = f"python-microservice-{ip_address}"

    consul = Consul(host="consul", port=8500)

    consul.agent.service.register(
        "python-microservice",
        service_id=service_id,
        address=ip_address,
        port=8000,
        check={
            "http": f"http://{ip_address}:8000/health",
            "interval": "10s"
        }
    )

@app.get("/service1/data")
async def get_data():
    # import time
    # time.sleep(10)
    return {"message": "Hello from Python Microservice"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    register_with_consul()
    uvicorn.run(app, host="0.0.0.0", port=8000)
