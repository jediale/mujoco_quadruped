# to be run with _read_quadruped_joint_1.py

import asyncio
import json
import moteus
import moteus_pi3hat
import websockets
from datetime import datetime

controller = None

async def initialize_motor():
    """Setup motor 1"""
    global controller
    
    transport = moteus_pi3hat.Pi3HatRouter(
        servo_bus_map={
            1: [1],
        }, 
    )

    controller = moteus.Controller(id=1, transport=transport)

    print("Stopping motor 1...")
    try:
        await asyncio.wait_for(controller.set_stop(), timeout=3.0)
        print("Motor 1 stopped")
    except Exception as e:
        print(f"ERROR: {e}")
    
    await asyncio.sleep(1.0)
    print("Motor 1 ready")

async def read_motor_position():
    """Read current position from motor 1"""
    try:
        state = await asyncio.wait_for(
            controller.set_position(position=float('nan'), query=True),
            timeout=1.0
        )
        return state.values[moteus.Register.POSITION]
    except Exception as e:
        print(f"Read error: {type(e).__name__}")
        return 0.0

async def handle_client(websocket):
    """Stream motor 1 position to laptop"""
    print("Laptop connected")
    try:
        while True:
            position = await read_motor_position()
            
            response = {
                'motor_position': position,
                'timestamp': datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(response))
            await asyncio.sleep(0.1)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Laptop disconnected")

async def websocket_server():
    """Start WebSocket server"""
    async with websockets.serve(handle_client, "localhost", 8765):
        print("WebSocket server running on ws://localhost:8765")
        await asyncio.Future()

async def main():
    print("Initializing motor 1...")
    await initialize_motor()
    
    print("Starting WebSocket server...")
    await websocket_server()

if __name__ == '__main__':
    asyncio.run(main())