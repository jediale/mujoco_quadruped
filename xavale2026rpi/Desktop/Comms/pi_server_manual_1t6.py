import asyncio
import json
import moteus
import moteus_pi3hat
import websockets
from datetime import datetime

controllers = {}

async def initialize_motors():
    """Setup motors 1-6"""
    global controllers
    
    transport = moteus_pi3hat.Pi3HatRouter(
        servo_bus_map={
            1: [1, 2, 3],
            2: [4, 5, 6],
        }, 
    )

    motor_ids = [1, 2, 3, 4, 5, 6]
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
    print("Motors ready to read positions")

async def read_motor_positions():
    """Read current positions from motors 1-6"""
    states = {}
    
    for idx in range(1, 7):
        try:
            print(f"Reading motor {idx}...")
            state = await asyncio.wait_for(
                controllers[idx].set_stop(query=True),
                timeout=2.0
            )
            states[idx] = state.values[moteus.Register.POSITION]
            print(f"Motor {idx}: {states[idx]:.2f}")
        except asyncio.TimeoutError:
            print(f"Motor {idx} TIMEOUT")
            states[idx] = 0.0
        except Exception as e:
            print(f"Motor {idx} error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            states[idx] = 0.0
    
    return states

async def handle_client(websocket):
    """Stream motor positions to laptop"""
    print("Laptop connected")
    try:
        while True:
            # Read current positions
            motor_positions = await read_motor_positions()
            
            # Send to laptop
            response = {
                'motor_positions': motor_positions,
                'timestamp': datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(response))
            await asyncio.sleep(0.05)  # Send 20 times per second
            
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
    print("Initializing 6 motors...")
    await initialize_motors()
    
    print("Starting WebSocket server...")
    await websocket_server()

if __name__ == '__main__':
    asyncio.run(main())