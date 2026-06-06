# basically says how long the episodes should be, sets limits, truncation / termination

# OG:

# gymnasium environment wrapping the same cart-pole model used in open_loop.py.

# Loads cartpole.xml and reuses the same stepping logic (mj_step). 

# Observation: [cart_position, cart_velocity, pole_angle, pole_angular_velocity]
# Action: continuous force on cart (same as data.ctrl[0] in open_loop.py).

# 4/20/26 - for me, the observation should be the position of the centers of the parts of the quadruped and the velocities - I want everything fixed and velocities at 0
# the action space is going to be all of the joints (wow)

# I made the min height 0 because in the first test run of training it was ending after one episode, so it wasn't really training at all

# I had to also fix the quaternion (w x y z) which was checking the z rotation and not w

import os
import numpy as np
import mujoco
import gymnasium as gym
from gymnasium import spaces

# XML_PATH = os.environ.get("MUJOCO_CARTPOLE_XML", os.path.join(os.path.dirname(__file__), "cartpole.xml"))
XML_PATH = os.path.join(os.path.dirname(__file__), "scene_mjx.xml")

DEFAULT_MAX_EPISODE_STEPS = 500
DEFAULT_ACTION_REPEAT = 10
DEFAULT_INITIAL_STATE_NOISE = 0.02   # rad/s for angle, m/s for velocity, m for position

# Termination: quadruped body position too low? just for standing
# DEFAULT_POLE_ANGLE_LIMIT = np.pi / 2   # 90°

DEFAULT_QUAD_MIN_HEIGHT = 0 # (m)
# Quadruped position bounds (m) ,  should match cartpole.xml slide range (-2, 2)
DEFAULT_QUAD_X_MIN = -1
DEFAULT_QUAD_X_MAX = 1
DEFAULT_QUAD_Y_MIN = -1
DEFAULT_QUAD_Y_MAX = 1


def get_policy_state(data: mujoco.MjData) -> np.ndarray:
    """
    State for the policy (what goes into the neural network).
    
    ONLY joint positions and velocities.
    Sim2Real ready - measurable on real robot.
    
    Args:
        data: mujoco.MjData object
    
    Returns:
        np.ndarray of shape (24,)
        [joint_pos_0...11, joint_vel_0...11]
    """
    joint_positions = data.qpos[7:]    # 12 DOF
    joint_velocities = data.qvel[6:]   # 12 DOF
    
    return np.concatenate([joint_positions, joint_velocities]).astype(np.float32)
 
 
def get_episode_info(data: mujoco.MjData) -> dict:
    """
    Episode information for rewards, termination, and logging.
    
    NOT visible to policy, used only for:
    - Reward function calculation
    - Episode termination checks
    - Performance metrics / logging
    
    Args:
        data: mujoco.MjData object
    
    Returns:
        dict with keys:
        - time: float
        - base_position: (3,) [x, y, z]
        - base_linear_velocity: (3,) [vx, vy, vz]
        - base_orientation: (4,) [qx, qy, qz, qw]
        - base_angular_velocity: (3,) [wx, wy, wz]
        - base_height: float (z component)
        - foot_contact: (4,) binary [FL, FR, RL, RR]
        - joint_positions: (12,)
        - joint_velocities: (12,)
        - energy: float (control effort)
    """
    # Base state
    base_pos = data.qpos[0:3]
    base_quat = data.qpos[3:7]
    base_lin_vel = data.qvel[0:3]
    base_ang_vel = data.qvel[3:6]
    
    # Joint state
    joint_pos = data.qpos[7:]
    joint_vel = data.qvel[6:]
    
    # Foot contact
    foot_contact = np.zeros(4, dtype=np.float32)
    foot_indices = [4, 7, 10, 13]  # FL, FR, RL, RR calf bodies
    for i, foot_idx in enumerate(foot_indices):
        vertical_force = np.abs(data.cfrc_ext[foot_idx, 2])
        foot_contact[i] = 1.0 if vertical_force > 0.01 else 0.0
    
    # Energy (control effort)
    control_effort = np.sum(np.square(data.ctrl))
    
    return {
        "time": float(data.time),
        "base_position": base_pos.copy(),
        "base_linear_velocity": base_lin_vel.copy(),
        "base_orientation": base_quat.copy(),
        "base_angular_velocity": base_ang_vel.copy(),
        "base_height": float(base_pos[2]),
        "foot_contact": foot_contact.copy(),
        "joint_positions": joint_pos.copy(),
        "joint_velocities": joint_vel.copy(),
        "energy": float(control_effort),
    }


class CartPoleRLEnv(gym.Env):
    # gym env with the same physics as open_loop.py; used for RL training and policy playback.

    metadata = {"render_modes": []}


    def __init__(
        self,
        xml_path: str = XML_PATH,
        max_episode_steps: int = DEFAULT_MAX_EPISODE_STEPS,
        action_repeat: int = DEFAULT_ACTION_REPEAT,
        initial_state_noise: float = DEFAULT_INITIAL_STATE_NOISE,
        quad_min_height: float = DEFAULT_QUAD_MIN_HEIGHT,
        quad_x_min: float = DEFAULT_QUAD_X_MIN,
        quad_x_max: float = DEFAULT_QUAD_X_MAX,
        quad_y_min: float = DEFAULT_QUAD_Y_MIN,
        quad_y_max: float = DEFAULT_QUAD_Y_MAX,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._xml_path = xml_path
        self._max_episode_steps = max_episode_steps
        self._action_repeat = action_repeat
        self._initial_state_noise = initial_state_noise
        self.quad_min_height = quad_min_height
        self.quad_x_min = quad_x_min
        self.quad_x_max = quad_x_max
        self.quad_y_min = quad_y_min
        self.quad_y_max = quad_y_max

        # load the model
        self.model = mujoco.MjModel.from_xml_path(xml_path)
        self.data = mujoco.MjData(self.model)
        self._physics_dt = float(self.model.opt.timestep)

        # setting limits on what the action can be
        # Action space: 12 joint angles
        # Hip: [-1.0, 1.0], Thigh: [-1.5, 2.5], Calf: [-2.6, 0.0]
        self.action_space = spaces.Box(
            low=np.array([-1.0, -1.5, -2.6] * 4, dtype=np.float32),
            high=np.array([1.0, 2.5, 0.0] * 4, dtype=np.float32),
            dtype=np.float32,
        )

        # Observation space: 24 dims (joint pos + vel)
        self.observation_space = spaces.Box(
            low=np.concatenate([
                np.array([-1.0, -1.5, -2.6] * 4),  # Joint positions (bounded)
                [-np.inf] * 12,                     # Joint velocities (unbounded)
            ]).astype(np.float32),
            high=np.concatenate([
                np.array([1.0, 2.5, 0.0] * 4),     # Joint positions (bounded)
                [np.inf] * 12,                      # Joint velocities (unbounded)
            ]).astype(np.float32),
            dtype=np.float32,
        )


        # # Same action as open_loop: continuous force on cart (ctrl[0])
        # self.action_space = spaces.Box(
        #     low=np.array([-10.0], dtype=np.float32),
        #     high=np.array([10.0], dtype=np.float32),
        #     dtype=np.float32,
        # )
        # # Observation: cart_position, cart_velocity, pole_angle, pole_angular_velocity
        # self.observation_space = spaces.Box(
        #     low=np.array([cart_x_min, -np.inf, -np.pi, -np.inf], dtype=np.float32),
        #     high=np.array([cart_x_max, np.inf, np.pi, np.inf], dtype=np.float32),
        #     dtype=np.float32,
        # )

        self._step_count = 0

    def _get_obs(self) -> np.ndarray:
        """Return policy observation (24 dims: joint pos + vel)."""
        return get_policy_state(self.data)
    
    # determines the ending
    def _is_terminated(self) -> bool:
        """Check termination conditions for quadruped."""
        episode_info = get_episode_info(self.data)
        
        # 1. Height check (fell over)
        if episode_info["base_height"] < self.quad_min_height:
            return True
        
        # 2. Orientation check (rolled/pitched too much)
        quat = episode_info["base_orientation"]
        if quat[0] < 0.7:
            return True
        
        # 3. Position bounds (x and y)
        base_pos = episode_info["base_position"]
        if base_pos[0] < self.quad_x_min or base_pos[0] > self.quad_x_max:
            return True
        if base_pos[1] < self.quad_y_min or base_pos[1] > self.quad_y_max:
            return True
        
        return False


    def _is_truncated(self) -> bool:
        return self._step_count >= self._max_episode_steps

    def reset(self, seed=None, options=None):
        """Reset episode to initial state."""
        super().reset(seed=seed)
        mujoco.mj_resetData(self.model, self.data)
        
        # Add noise to initial joint positions
        if self._initial_state_noise > 0 and self.np_random is not None:
            for i in range(7, 19):  # All 12 joint positions
                self.data.qpos[i] += self.np_random.uniform(
                    -self._initial_state_noise, 
                    self._initial_state_noise
                )
        
        self._step_count = 0
        return self._get_obs(), {}

    def step(self, action):
        """
        Step the environment with action.
        
        Args:
            action: (12,) array of joint targets
        
        Returns:
            obs: (24,) observation
            reward: float (0.0 - use RewardWrapper to add actual rewards)
            terminated: bool
            truncated: bool
            info: dict with episode info
        """
        # Clip action to valid ranges
        action = np.clip(action, self.action_space.low, self.action_space.high)
        
        # Hold action for action_repeat steps
        for _ in range(self._action_repeat):
            self.data.ctrl[:] = action
            mujoco.mj_step(self.model, self.data)
            self._step_count += 1
            if self._is_terminated() or self._is_truncated():
                break
 
        # Get observation
        obs = self._get_obs()
        
        # Check termination/truncation
        terminated = self._is_terminated()
        truncated = self._is_truncated()
        
        # Info dict for logging
        episode_info = get_episode_info(self.data)
        info = {
            "base_height": episode_info["base_height"],
            "base_position": episode_info["base_position"],
            "base_linear_velocity": episode_info["base_linear_velocity"],
            "foot_contact": episode_info["foot_contact"],
        }
        
        # Base env returns 0 reward; use RewardWrapper to add actual rewards
        return obs, 0.0, terminated, truncated, info

    def get_model_and_data(self):
        return self.model, self.data


class RewardWrapper(gym.Wrapper):
    # Wraps CartPoleRLEnv and computes reward using reward_functions.py
    # Adds reward_dictionary to info so training can log component breakdown

    def __init__(self, env: gym.Env):
        super().__init__(env)
        import sys
        _dir = os.path.dirname(os.path.abspath(__file__))
        if _dir not in sys.path:
            sys.path.insert(0, _dir)
        import _reward_functions as rf
        self._rf = rf

    def step(self, action):
        obs, _, terminated, truncated, info = self.env.step(action)
        # total_reward, reward_dict = self._rf.reward_from_obs_action(
        #     obs, action, terminated=terminated
        # )
        total_reward, reward_dict = self._rf.reward_standing(obs, action, get_episode_info(self.env.data), terminated, self._rf.get_reward_weights())
    
        info["reward_dict"] = reward_dict
        return obs, total_reward, terminated, truncated, info
