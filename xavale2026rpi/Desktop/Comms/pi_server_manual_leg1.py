import asyncio
import json
import moteus
import moteus_pi3hat
import websockets
from datetime import datetime

controllers = {}

async def initialize_motors():
    """Setup motors 1-3"""
    global controllers
    
    transport = moteus_pi3hat.Pi3HatRouter(
        servo_bus_map={
            1: [1, 2, 3],
        }, 
    )

    motor_ids = [1, 2, 3]
    controllers = {mid: moteus.Controller(id=mid, transport=transport) for mid in motor_ids}

    print("Stopping all motors...")
    for mid in motor_ids:
        try:
            await asyncio.wait_for(controllers[mid].set_stop(), timeout=3.0)
            print(f"Motor {mid} stopped")
            await asyncio.sleep(0.2)
        except Exception as e:
            print(f"ERROR: Motor {mid}: {e}")
    
    await asyncio.sleep(1.0)
    print("Motors ready")

async def read_motor_positions():
    """Read current positions from motors 1-3"""
    states = {}
    
    for idx in [1, 2, 3]:
        try:
            state = await asyncio.wait_for(
                controllers[idx].set_position(position=float('nan'), query=True),
                timeout=1.0
            )
            states[idx] = state.values[moteus.Register.POSITION]
        except Exception as e:
            print(f"Motor {idx} read error")
            states[idx] = 0.0
        await asyncio.sleep(0.05)
    
    return states

async def handle_client(websocket):
    """Stream motor positions to laptop"""
    print("Laptop connected")
    try:
        while True:
            motor_positions = await read_motor_positions()
            
            response = {
                'motor_positions': motor_positions,
                'timestamp': datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(response))
            await asyncio.sleep(0.05)
            
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
    print("Initializing motors 1-3...")
    await initialize_motors()
    
    print("Starting WebSocket server...")
    await websocket_server()

if __name__ == '__main__':
    asyncio.run(main())