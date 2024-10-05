import asyncio
import websockets

async def websocket_client():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            print(f"Received: {message}")

if __name__ == "__main__":
    asyncio.run(websocket_client())
