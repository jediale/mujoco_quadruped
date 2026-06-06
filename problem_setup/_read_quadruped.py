import asyncio
import websockets
import json
import os
import time
import warnings
from pynput import keyboard

warnings.filterwarnings("ignore", message=".*Wayland.*window position.*")

import mujoco
import mujoco.viewer

_XML_PATH = os.path.join(os.path.dirname(__file__), "scene_mjx.xml")
model = mujoco.MjModel.from_xml_path(_XML_PATH)
data = mujoco.MjData(model)

action_repeat = 10
physics_dt = model.opt.timestep
control_dt = physics_dt * action_repeat

state = {"mode": "script"}

# SEPARATE VARIABLES
command_positions = [0.0]*12  # What we SEND to pi
actual_motor_positions = [0.0]*12  # What we RECEIVE from pi

def key_callback(keycode):
    if keycode == 82:  # R: reset
        mujoco.mj_resetData(model, data)
    elif keycode == 83:  # S: script control
        state["mode"] = "script"
    elif keycode == 71:  # G: GUI control
        state["mode"] = "gui"

def set_fixed_camera(viewer):
    viewer.cam.type = mujoco.mjtCamera.mjCAMERA_FREE
    viewer.cam.azimuth = 90.0
    viewer.cam.elevation = -15.0
    viewer.cam.distance = 2.8
    viewer.cam.lookat[:] = [0.0, 0.0, 0.4]

async def get_initial_positions():
    """Query pi for initial motor positions"""
    global command_positions
    uri = "ws://localhost:8765"
    try:
        async with websockets.connect(uri) as ws:
            data = {'packet': [0]*12, 'state': 'still'}
            await ws.send(json.dumps(data))
            
            response = await asyncio.wait_for(ws.recv(), timeout=1.0)
            response_data = json.loads(response)
            
            motor_pos = response_data['motor_positions']
            command_positions = [
                motor_pos.get(i+1, 0.0) for i in range(12)
            ]
            print(f"Initial positions: {[round(p, 2) for p in command_positions]}")
            
    except Exception as e:
        print(f"Error getting initial positions: {e}")

async def websocket_loop():
    """Continuously send/receive motor data"""
    global command_positions, actual_motor_positions
    uri = "ws://localhost:8765"
    
    while True:
        try:
            async with websockets.connect(uri) as ws:
                print("Connected to pi server")
                while True:
                    # SEND command positions TO pi
                    data = {'packet': command_positions, 'state': 'still'}
                    await ws.send(json.dumps(data))
                    
                    try:
                        # RECEIVE actual positions FROM pi
                        response = await asyncio.wait_for(ws.recv(), timeout=1.0)
                        response_data = json.loads(response)
                        
                        motor_pos = response_data['motor_positions']
                        actual_motor_positions = [
                            motor_pos.get(i+1, 0.0) for i in range(12)
                        ]
                        
                    except asyncio.TimeoutError:
                        pass
                    except Exception as e:
                        print(f"Recv error: {e}")
                        break
                    
                    await asyncio.sleep(0.05)
        except Exception as e:
            print(f"Connection error: {e}")
            await asyncio.sleep(1.0)

def on_press(key):
    """Keyboard control"""
    global command_positions
    
    try:
        if key.char == "1":
            command_positions[0] += 0.1
        elif key.char == "2":
            command_positions[1] += 0.1
        elif key.char == "3":
            command_positions[2] += 0.1
        elif key.char == "4":
            command_positions[3] += 0.1
        elif key.char == "5":
            command_positions[4] += 0.1
        elif key.char == "6":
            command_positions[5] += 0.1
        elif key.char == "7":
            command_positions[6] += 0.1
        elif key.char == "8":
            command_positions[7] += 0.1
        elif key.char == "9":
            command_positions[8] += 0.1
        elif key.char == "0":
            command_positions[9] += 0.1
        elif key.char == "-":
            command_positions[10] += 0.1
        elif key.char == "=":
            command_positions[11] += 0.1
        elif key.char == "q":
            command_positions[0] -= 0.1
        elif key.char == "w":
            command_positions[1] -= 0.1
        elif key.char == "e":
            command_positions[2] -= 0.1
        elif key.char == "r":
            command_positions[3] -= 0.1
        elif key.char == "t":
            command_positions[4] -= 0.1
        elif key.char == "y":
            command_positions[5] -= 0.1
        elif key.char == "u":
            command_positions[6] -= 0.1
        elif key.char == "i":
            command_positions[7] -= 0.1
        elif key.char == "o":
            command_positions[8] -= 0.1
        elif key.char == "p":
            command_positions[9] -= 0.1
        elif key.char == "[":
            command_positions[10] -= 0.1
        elif key.char == "]":
            command_positions[11] -= 0.1
        
        print(f"Command: {[round(p, 2) for p in command_positions]}")
        
    except AttributeError:
        pass

def on_release(key):
    if key == keyboard.Key.esc:
        print("ESC pressed - exiting")
        return False

def run_mujoco():
    """MuJoCo simulation loop"""
    global actual_motor_positions
    
    with mujoco.viewer.launch_passive(model, data, key_callback=key_callback) as viewer:
        set_fixed_camera(viewer)
        step = 0
        last_sync = time.perf_counter()
        
        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            while viewer.is_running():
                if state["mode"] == "script" and step % action_repeat == 0:
                    # Apply ACTUAL motor positions from pi to simulation
                    data.ctrl[:] = actual_motor_positions
                
                mujoco.mj_step(model, data)
                viewer.sync()
                set_fixed_camera(viewer)
                step += 1
                
                if step % action_repeat == 0:
                    now = time.perf_counter()
                    elapsed = now - last_sync
                    if elapsed < control_dt:
                        time.sleep(control_dt - elapsed)
                    last_sync = time.perf_counter()

async def main_async():
    print("Querying initial motor positions...")
    await get_initial_positions()
    
    # Start websocket loop
    ws_task = asyncio.create_task(websocket_loop())
    
    # Run MuJoCo in executor
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, run_mujoco)
    
    ws_task.cancel()

if __name__ == "__main__":
    asyncio.run(main_async())