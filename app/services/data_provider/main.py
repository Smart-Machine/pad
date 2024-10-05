import asyncio
import websockets
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

app = FastAPI()

# Store the latest data received from the external service
latest_data = {}

# Dictionary to store WebSocket clients
connected_clients = []

# Function to fetch data from external service via WebSocket
async def fetch_data_from_external_service():
    uri = "ws://0.0.0.0:8765"  # Replace with the actual WebSocket URL of the external service
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to external service at {uri}")
            while True:
                data = await websocket.recv()  # Receive data from the external service
                latest_data['data'] = data  # Store the latest data
                print(f"Received from external service: {data}")
                
                # Send data to all connected WebSocket clients
                for client in connected_clients:
                    await client.send_text(latest_data['data'])
    except websockets.ConnectionClosedError as e:
        print(f"Connection to external service closed with error: {e}")

# FastAPI route to start WebSocket session with the external service
@app.post("/session")
async def start_session():
    # Start the WebSocket client in the background to fetch data from external service
    asyncio.create_task(fetch_data_from_external_service())
    return JSONResponse(content={"message": "Session started successfully"})

# WebSocket connection handler for clients connecting to the microservice
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    print("New client connected")
    
    try:
        while True:
            # Keep the connection open; the data will be pushed to clients automatically
            await asyncio.sleep(1)  # Just to prevent tight looping
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        print("Client disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
