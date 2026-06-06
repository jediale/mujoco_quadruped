# 30 minutes

# make it stand

# make it walk forward

# 4/20/26 - figured out the ranges and behaviors, 

"""
open-loop control demo

force u(t) = amp*sin(2*pi*freq*t) depends only on time,
not on cart/pole state. 

What to expect: The cart will slide and the pole will swing, then the pole will
fall. That is expected because open-loop does not try to balance. Re-run to see it again,
or press R in the viewer to reset. Press S for script (sinusoid), G to try GUI
control (if the viewer shows actuator sliders in the right panel).

The point of this script is to check that:
The sim runs,
The cart motor responds to data.ctrl[0],
Motion looks reasonable (no explosion or jitter).
"""
import os
import time
import warnings

# On Linux Wayland, GLFW may warn about window position; viewer still works.
warnings.filterwarnings("ignore", message=".*Wayland.*window position.*")

import numpy as np
import mujoco
import mujoco.viewer

_XML_PATH = os.path.join(os.path.dirname(__file__), "scene_mjx.xml")
model = mujoco.MjModel.from_xml_path(_XML_PATH)
data = mujoco.MjData(model)

action_repeat = 10 # hold action for this many physics steps
# in tutorial, we set to 0

# I'm gonna make the legs all oscillate in phase sinusoidally
# amp = 0.0
amp_u = 0       # force amplitude (N)
amp_v = 1
amp_w = 0.65
freq_u = 0      # sinusoid frequency (Hz)
freq_v = 1.2
freq_w = 1.2
phase_u = 0
phase_v = 0
phase_w = 0
bias_u = 0
bias_v = 1.5
bias_w = -1.3
chill_u = 0
chill_v = 1/3
chill_w = 1
physics_dt = model.opt.timestep  # simulation step size (ie 0.002 s)
control_dt = physics_dt * action_repeat  # time between control updates

# Shared state for key callback: 'script' = sinusoid, 'gui' = don't set ctrl (try viewer sliders)
state = {"mode": "script"}


def key_callback(keycode):
    # 82 = R, 83 = S, 71 = G (ASCII)
    if keycode == 82:  # R: reset
        mujoco.mj_resetData(model, data)
    elif keycode == 83:  # S: script control (sinusoid)
        state["mode"] = "script"
    elif keycode == 71:  # G: GUI control
        state["mode"] = "gui"


def set_fixed_camera(viewer):
    viewer.cam.type = mujoco.mjtCamera.mjCAMERA_FREE
    viewer.cam.azimuth = 90.0   # side view so cart sliding (along x) is clearly visible
    viewer.cam.elevation = -15.0
    viewer.cam.distance = 2.8
    viewer.cam.lookat[:] = [0.0, 0.0, 0.4]


with mujoco.viewer.launch_passive(model, data, key_callback=key_callback) as viewer:
    set_fixed_camera(viewer)
    step = 0
    last_sync = time.perf_counter()
    while viewer.is_running():
        if state["mode"] == "script" and step % action_repeat == 0:

            # sinusoids

            # goes the full range of the hip
            u = amp_u * np.sin(2 * np.pi * freq_u * data.time + phase_u) + bias_u
            
            # goes the full range of the thigh
            v_ph = amp_v * np.sin(2 * np.pi * freq_v * data.time + phase_v) + bias_v
            v_0 = amp_v * np.sin(2 * np.pi * freq_v * data.time) + bias_v
            v_p2 = amp_v * np.sin(2 * np.pi * freq_v * data.time + np.pi/2) + bias_v
            v_p = amp_v * np.sin(2 * np.pi * freq_v * data.time + np.pi) + bias_v
            v_3p2 = amp_v * np.sin(2 * np.pi * freq_v * data.time + 3*np.pi/2) + bias_v

            # goes the full range of the calf
            w_ph = amp_w * np.sin(2*np.pi*freq_w*data.time + phase_w) + bias_w
            w_0 = amp_w * np.sin(2*np.pi*freq_w*data.time) + bias_w
            w_p2 = amp_w * np.sin(2*np.pi*freq_w*data.time + np.pi/2) + bias_w
            w_p = amp_w * np.sin(2*np.pi*freq_w*data.time + np.pi) + bias_w
            w_3p2 = amp_w * np.sin(2*np.pi*freq_w*data.time + 3*np.pi/2) + bias_w

            
            # data.ctrl[i] to program a limb

            # front left
            data.ctrl[0] = 0.2
            data.ctrl[1] = chill_v*v_p
            data.ctrl[2] = chill_w*w_3p2

            # front right
            data.ctrl[3] = -0.2
            data.ctrl[4] = chill_v*v_0
            data.ctrl[5] = chill_w*w_p2

            # back left
            data.ctrl[6] = 0.2
            data.ctrl[7] = chill_v*v_0
            data.ctrl[8] = chill_w*w_p2

            # back right
            data.ctrl[9] = -0.2
            data.ctrl[10] = chill_v*v_p
            data.ctrl[11] = chill_w*w_3p2


            # print(int(data.time*1000))

            # print(data)
        # in gui mode don't sest ctrl, instead use the viewer's right panel with actuator sliders
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

