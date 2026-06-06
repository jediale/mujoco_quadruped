import asyncio
import websockets
import json
from pynput import keyboard

packet = [0,0,0,0,0,0,0,0,0,0,0,0] 
state = "still"
latest_response = None

async def get_initial_positions():
    """Query pi for initial motor positions"""
    global packet
    uri = "ws://localhost:8765"
    try:
        async with websockets.connect(uri) as ws:
            data = {'packet': [0]*12, 'state': 'still'}
            await ws.send(json.dumps(data))
            
            response = await asyncio.wait_for(ws.recv(), timeout=1.0)
            response_data = json.loads(response)
            
            motor_pos = response_data['motor_positions']
            packet = [
                motor_pos.get(i+1, 0.0) for i in range(12)
            ]
            print(f"Initial positions: {[round(p, 2) for p in packet]}")
            
            if any(p is None for p in packet):
                print("WARNING: Some motors returned None - manually verify positions!")
            
    except Exception as e:
        print(f"Error getting initial positions: {e}")

async def send_loop():
    global latest_response
    uri = "ws://localhost:8765"
    
    while True:
        try:
            async with websockets.connect(uri) as ws:
                print("Connected to server")
                while True:
                    data = {'packet': packet, 'state': state}
                    await ws.send(json.dumps(data))
                    
                    try:
                        response = await asyncio.wait_for(ws.recv(), timeout=1.0)
                        latest_response = json.loads(response)
                        
                        motor_pos = latest_response['motor_positions']
                        print(f"\n✓ Server response")
                        print(f"  Motors:  1={motor_pos.get(1, 0):.2f}  2={motor_pos.get(2, 0):.2f}  3={motor_pos.get(3, 0):.2f}")
                        print(f"           4={motor_pos.get(4, 0):.2f}  5={motor_pos.get(5, 0):.2f}  6={motor_pos.get(6, 0):.2f}")
                        print(f"           7={motor_pos.get(7, 0):.2f}  8={motor_pos.get(8, 0):.2f}  9={motor_pos.get(9, 0):.2f}")
                        print(f"          10={motor_pos.get(10, 0):.2f} 11={motor_pos.get(11, 0):.2f} 12={motor_pos.get(12, 0):.2f}")
                        
                    except asyncio.TimeoutError:
                        print("Server timeout")
                    except Exception as e:
                        print(f"Recv error: {e}")
                        break
                    
                    await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Connection error: {e}")
            await asyncio.sleep(1.0)

def on_press(key):
    global state
    
    try:
        if key.char == "1":
            packet[0] = packet[0] + 0.1
        elif key.char == "2":
            packet[1] = packet[1] + 0.1
        elif key.char == "3":
            packet[2] = packet[2] + 0.1
        elif key.char == "4":
            packet[3] = packet[3] + 0.1
        elif key.char == "5":
            packet[4] = packet[4] + 0.1
        elif key.char == "6":
            packet[5] = packet[5] + 0.1
        elif key.char == "7":
            packet[6] = packet[6] + 0.1
        elif key.char == "8":
            packet[7] = packet[7] + 0.1
        elif key.char == "9":
            packet[8] = packet[8] + 0.1
        elif key.char == "0":
            packet[9] = packet[9] + 0.1
        elif key.char == "-":
            packet[10] = packet[10] + 0.1
        elif key.char == "=":
            packet[11] = packet[11] + 0.1
        elif key.char == "q":
            packet[0] = packet[0] - 0.1
        elif key.char == "w":
            packet[1] = packet[1] - 0.1
        elif key.char == "e":
            packet[2] = packet[2] - 0.1
        elif key.char == "r":
            packet[3] = packet[3] - 0.1
        elif key.char == "t":
            packet[4] = packet[4] - 0.1
        elif key.char == "y":
            packet[5] = packet[5] - 0.1
        elif key.char == "u":
            packet[6] = packet[6] - 0.1
        elif key.char == "i":
            packet[7] = packet[7] - 0.1
        elif key.char == "o":
            packet[8] = packet[8] - 0.1
        elif key.char == "p":
            packet[9] = packet[9] - 0.1
        elif key.char == "[":
            packet[10] = packet[10] - 0.1
        elif key.char == "]":
            packet[11] = packet[11] - 0.1
        
        if key.char == "j":
            state = "left"
        elif key.char == "m":
            state = "back"
        elif key.char == "l":
            state = "right"
        elif key.char == "k":
            state = "forward"
        elif key.char == ",":
            state = "still"
        
        print(f"Packet: {[round(p, 2) for p in packet]}, State: {state}")
        
    except AttributeError:
        pass

def on_release(key):
    if key == keyboard.Key.esc:
        print("ESC pressed - exiting")
        return False

async def main_async():
    print("Querying initial motor positions...")
    await get_initial_positions()
    
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        await send_loop()

if __name__ == "__main__":
    asyncio.run(main_async())