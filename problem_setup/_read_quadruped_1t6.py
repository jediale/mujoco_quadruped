import asyncio
import websockets
import json
import os
import time
import warnings

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
actual_motor_positions = [0.0]*6

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

async def websocket_loop():
    """Receive motor positions from pi"""
    global actual_motor_positions
    uri = "ws://localhost:8765"
    
    while True:
        try:
            async with websockets.connect(uri) as ws:
                print("Connected to pi")
                while True:
                    try:
                        response = await asyncio.wait_for(ws.recv(), timeout=1.0)
                        response_data = json.loads(response)
                        
                        motor_pos = response_data['motor_positions']
                        actual_motor_positions = [
                            motor_pos.get(i+1, 0.0) for i in range(6)
                        ]
                        
                    except asyncio.TimeoutError:
                        pass
                    except Exception as e:
                        print(f"Error: {e}")
                        break
                    
                    await asyncio.sleep(0.01)
        except Exception as e:
            print(f"Connection error: {e}")
            await asyncio.sleep(1.0)

def run_mujoco():
    """MuJoCo simulation loop"""
    global actual_motor_positions
    
    with mujoco.viewer.launch_passive(model, data, key_callback=key_callback) as viewer:
        set_fixed_camera(viewer)
        step = 0
        last_sync = time.perf_counter()
        
        while viewer.is_running():
            if state["mode"] == "script" and step % action_repeat == 0:
                # Apply received motor positions to first 6 actuators
                data.ctrl[:6] = actual_motor_positions
                data.ctrl[6:12] = [0.0]*6
            
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
    ws_task = asyncio.create_task(websocket_loop())
    
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, run_mujoco)
    
    ws_task.cancel()

if __name__ == "__main__":
    asyncio.run(main_async())