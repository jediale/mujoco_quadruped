import asyncio
import websockets
import json
from pynput import keyboard

packet = [0,0,0,0,0,0,0,0,0,0,0,0] 
state = "manual"
latest_response = None

async def send_loop():
    global latest_response
    uri = "ws://localhost:8765"
    try:
        async with websockets.connect(uri) as ws:
            while True:
                data = {'packet': packet, 'state': state}
                await ws.send(json.dumps(data))
                
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=0.5)
                    latest_response = json.loads(response)
                    print(f"\n✓ Server response: {latest_response['timestamp']}")
                    print(f"  Motor positions: {[round(p, 2) for p in latest_response['motor_positions']]}")
                except asyncio.TimeoutError:
                    print("No response from server")
                
                await asyncio.sleep(0.1)
    except Exception as e:
        print(f"Connection error: {e}")

def on_press(key):
    global state
    
    try:

        # so basically, default will be manual mode (z) vs state mode (x)
        if state == "manual":
            if key.char == "1":
                packet[0] = packet[0] + 1
            elif key.char == "2":
                packet[1] = packet[1] + 1
            elif key.char == "3":
                packet[2] = packet[2] + 1
            elif key.char == "4":
                packet[3] = packet[3] + 1
            elif key.char == "5":
                packet[4] = packet[4] + 1
            elif key.char == "6":
                packet[5] = packet[5] + 1
            elif key.char == "7":
                packet[6] = packet[6] + 1
            elif key.char == "8":
                packet[7] = packet[7] + 1
            elif key.char == "9":
                packet[8] = packet[8] + 1
            elif key.char == "0":
                packet[9] = packet[9] + 1
            elif key.char == "-":
                packet[10] = packet[10] + 1
            elif key.char == "=":
                packet[11] = packet[11] + 1
            elif key.char == "q":
                packet[0] = packet[0] - 1
            elif key.char == "w":
                packet[1] = packet[1] - 1
            elif key.char == "e":
                packet[2] = packet[2] - 1
            elif key.char == "r":
                packet[3] = packet[3] - 1
            elif key.char == "t":
                packet[4] = packet[4] - 1
            elif key.char == "y":
                packet[5] = packet[5] - 1
            elif key.char == "u":
                packet[6] = packet[6] - 1
            elif key.char == "i":
                packet[7] = packet[7] - 1
            elif key.char == "o":
                packet[8] = packet[8] - 1
            elif key.char == "p":
                packet[9] = packet[9] - 1
            elif key.char == "[":
                packet[10] = packet[10] - 1
            elif key.char == "]":
                packet[11] = packet[11] - 1
            elif key.char == "x":
                state = "still"
        else:
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
            elif key.char == "z":
                state = "manual"
        
        print(f"Packet: {packet}, State: {state}")
        
    except AttributeError:
        pass

def on_release(key):
    if key == keyboard.Key.esc:
        print("ESC pressed - exiting")
        return False

async def main_async():
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        await send_loop()

if __name__ == "__main__":
    asyncio.run(main_async())