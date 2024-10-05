import asyncio
import websockets
import json
import random

# Create a simple function that will simulate real-time data
async def data_provider(websocket, path):
    try:
        while True:
            # Simulating some data, for example, stock price updates
            data = {
                'stock': 'AAPL',
                'price': round(random.uniform(150, 200), 2),
                'timestamp': asyncio.get_event_loop().time()
            }
            await websocket.send(json.dumps(data))  # Send data to the client
            await asyncio.sleep(1)  # Wait for 1 second before sending the next update
    except websockets.ConnectionClosedOK:
        print("Connection closed normally.")
    except websockets.ConnectionClosedError as e:
        print(f"Connection closed with error: {e}")

# Start the WebSocket server
async def start_server():
    async with websockets.serve(data_provider, "0.0.0.0", 8765):
        print("WebSocket server started on ws://0.0.0.0:8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(start_server())
