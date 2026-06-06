
"""
Inspect your MuJoCo model to find body indices, joint names, etc.
Fixed version with proper API handling.
"""

import mujoco
import os

def inspect_model(xml_path: str):
    """Print detailed info about MuJoCo model structure."""
    model = mujoco.MjModel.from_xml_path(xml_path)
    data = mujoco.MjData(model)
    
    print("=" * 80)
    print(f"Model: {xml_path}")
    print("=" * 80)
    
    # Bodies
    print("\nBODIES:")
    print("-" * 80)
    for i in range(model.nbody):
        body_name = model.body(i).name
        print(f"  [{i}] {body_name}")
    
    # Joints (DOFs)
    print("\nJOINTS:")
    print("-" * 80)
    for i in range(model.njnt):
        jnt = model.jnt(i)
        # Handle bodyid as array
        body_id = int(jnt.bodyid[0]) if hasattr(jnt.bodyid, '__len__') else int(jnt.bodyid)
        body_name = model.body(body_id).name
        print(f"  [{i}] {jnt.name:20s} | Body: {body_name:15s} | Type: {jnt.type}")
    
    # Actuators
    print("\nACTUATORS (Controls):")
    print("-" * 80)
    for i in range(model.nu):
        act = model.actuator(i)
        jnt_id = int(act.trnid[0])
        jnt_name = model.jnt(jnt_id).name
        print(f"  [{i}] {act.name:20s} | Joint: {jnt_name:15s}")
    
    # Sensors (if any)
    print(f"\nSENSORS: {model.nsensor}")
    print("-" * 80)
    if model.nsensor > 0:
        for i in range(model.nsensor):
            sensor = model.sensor(i)
            print(f"  [{i}] {sensor.name}")
    
    # Summary
    print("\nSUMMARY:")
    print("-" * 80)
    print(f"  Total bodies:   {model.nbody}")
    print(f"  Total joints:   {model.njnt}")
    print(f"  Total DOFs:     {model.nq} (positions), {model.nv} (velocities)")
    print(f"  Total controls: {model.nu}")
    print(f"  Timestep:       {model.opt.timestep} s")
    
    # Sample data shapes
    print("\nDATA SHAPES:")
    print("-" * 80)
    print(f"  data.qpos:      {data.qpos.shape}  (joint positions)")
    print(f"  data.qvel:      {data.qvel.shape}  (joint velocities)")
    print(f"  data.ctrl:      {data.ctrl.shape}  (control inputs)")
    print(f"  data.xpos:      {data.xpos.shape}  (body positions)")
    print(f"  data.xquat:     {data.xquat.shape} (body orientations)")
    print(f"  data.cfrc_ext:  {data.cfrc_ext.shape} (contact forces)")
    print(f"  data.sensordata: {data.sensordata.shape} (sensor outputs)")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    xml_path = os.path.join(os.path.dirname(__file__), "scene_mjx.xml")
    
    try:
        inspect_model(xml_path)
    except FileNotFoundError:
        print(f"Error: Could not find {xml_path}")
        print("Update the xml_path variable to point to your scene file.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()