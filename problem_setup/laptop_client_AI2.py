# to be run with the associate pi script - note variables are changing

import asyncio
import websockets
import json
from pynput import keyboard
import os
import time
import warnings
warnings.filterwarnings("ignore", message=".*Wayland.*window position.*")
import mujoco
import mujoco.viewer

_XML_PATH = os.path.join(os.path.dirname(__file__), "scene_mjx.xml")
model = mujoco.MjModel.from_xml_path(_XML_PATH)
mj_data = mujoco.MjData(model)

action_repeat = 10
physics_dt = model.opt.timestep
control_dt = physics_dt * action_repeat

mj_state = {"mode": "script"}

packet = [0,0,0,0,0,0,0,0,0,0,0,0] 
state = "manual"
latest_response = None

async def send_loop():
    global latest_response
    uri = "ws://localhost:8765"

    # simulator first
    with mujoco.viewer.launch_passive(model, mj_data) as viewer:
        try:
            async with websockets.connect(uri) as ws:
                # main loop
                while viewer.is_running():

                    # sends the data over
                    data = {'packet': packet, 'state': state}
                    await ws.send(json.dumps(data))
                    
                    # asks for a response (this is where I would update the mujoco)
                    try:
                        response = await asyncio.wait_for(ws.recv(), timeout=0.5)
                        latest_response = json.loads(response)
                        print(f"\n✓ Server response: {latest_response['timestamp']}")
                        print(f"  Motor positions: {[round(p, 2) for p in latest_response['motor_positions']]}")

                        # mujoco stuff
                        hardware_positions = latest_response['motor_positions']
                        for i in range(12):
                            mj_data.ctrl[i] = hardware_positions[i]

                        # mujoco.mj_step(model, mj_data)
                        # viewer.sync()

                        # step += 1
                        # if step % action_repeat == 0:
                        #     now = time.perf_counter()
                        #     elapsed = now - last_sync
                        #     if elapsed < control_dt:
                        #         await asyncio.sleep(control_dt - elapsed)
                        #     last_sync = time.perf_counter()

                        for _ in range(action_repeat):
                            mujoco.mj_step(model, mj_data)
                        
                        # 5. Sync GUI visualizer
                        viewer.sync()


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