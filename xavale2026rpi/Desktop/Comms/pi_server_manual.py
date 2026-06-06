import asyncio
import math
import json
import moteus
import moteus_pi3hat
import websockets
from datetime import datetime

controllers = {}
starting_positions = {}
latest_packet = [0]*12
latest_state = "still"

async def initialize_motors():
    """Setup all 12 motors across 4 buses"""
    global controllers, starting_positions
    
    transport = moteus_pi3hat.Pi3HatRouter(
        servo_bus_map={
            1: [1, 2, 3],
            2: [4, 5, 6],
            3: [7, 8, 9],
            4: [10, 11, 12]
        }, 
    )

    motor_ids = list(range(1, 13))
    controllers = {mid: moteus.Controller(id=mid, transport=transport) for mid in motor_ids}

    print("Stopping all motors...")
    for mid in motor_ids:
        try:
            await asyncio.wait_for(controllers[mid].set_stop(), timeout=3.0)
            print(f"Motor {mid} stopped")
            await asyncio.sleep(0.2)
        except Exception as e:
            print(f"ERROR stopping motor {mid}: {e}")
    
    await asyncio.sleep(1.0)

    print("Querying starting positions...")
    for mid in motor_ids:
        try:
            state = await asyncio.wait_for(
                controllers[mid].set_position(position=math.nan, query=True),
                timeout=3.0
            )
            starting_positions[mid] = state.values[moteus.Register.POSITION]
            print(f"Motor {mid}: {starting_positions[mid]:.2f}")
            await asyncio.sleep(0.2)
        except Exception as e:
            print(f"ERROR querying motor {mid}: {e}")
            starting_positions[mid] = 0.0

async def command_motors(packet):
    """Command all 12 motors based on packet values"""
    states = {}
    
    for idx in range(1, 13):
        if idx-1 < len(packet):
            try:
                command_offset = packet[idx-1] * 1.0
                
                state = await asyncio.wait_for(
                    controllers[idx].set_position(
                        position=starting_positions[idx] + command_offset,
                        velocity=math.nan,
                        maximum_torque=1.0,
                        query=True
                    ),
                    timeout=2.0
                )
                states[idx] = state.values[moteus.Register.POSITION]
            except asyncio.TimeoutError:
                print(f"Motor {idx} command timeout")
                states[idx] = starting_positions[idx]
            except Exception as e:
                print(f"Motor {idx} error: {e}")
                states[idx] = starting_positions[idx]
    
    return states

async def handle_client(websocket):
    """Handle incoming connections from laptop"""
    print("Laptop connected")
    try:
        async for message in websocket:
            global latest_packet, latest_state
            
            data = json.loads(message)
            latest_packet = data.get('packet', [0]*12)
            latest_state = data.get('state', 'still')
            
            print(f"Received - Packet: {[round(p, 2) for p in latest_packet]}, State: {latest_state}")
            
            motor_positions = await command_motors(latest_packet)
            
            response = {
                'status': 'ok',
                'timestamp': datetime.now().isoformat(),
                'received_packet': latest_packet,
                'received_state': latest_state,
                'motor_positions': motor_positions,
                'server_time': asyncio.get_event_loop().time()
            }
            
            await websocket.send(json.dumps(response))
            print(f"Sent response with motor positions")
            
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
    print("Initializing 12 motors...")
    await initialize_motors()
    
    print("Starting WebSocket server...")
    await websocket_server()

if __name__ == '__main__':
    asyncio.run(main())