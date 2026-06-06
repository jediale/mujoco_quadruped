

# I don't want it to fall over...

# z-coordinate of the torso

# OG one:

"""
Modular reward components for the cart-pole RL environment.

Each component is computed separately so you can:
- Understand what drives the policy
- Tune weights via reward_dashboard.py
- Debug reward shaping

Total reward = w_balance * balance + w_upright * upright + w_center * center
               - w_velocity * velocity_penalty - w_control * control_penalty
(+ optional termination_penalty when episode ends early)

Weights are adjustable dynamically (e.g. from sliders in reward_dashboard.py).
"""

import numpy as np
from typing import Dict, Any, Optional

DEFAULT_WEIGHTS = {
    "w_upright": 2.0,
    "w_lin_vel": 1.0,
    "w_ang_vel": 0.1,
    "w_contact": 0.5,
    "w_height": 0.5,
    "w_control": 0.01,
    "w_action": 0.05,
    "w_falling": 5.0,
}

# Current weights (can be updated live by reward_dashboard or train_rl)
_reward_weights: Dict[str, float] = dict(DEFAULT_WEIGHTS)

def set_reward_weights(weights: Dict[str, float]) -> None:
    # updates from sliders
    global _reward_weights
    for k, v in weights.items():
        if k in _reward_weights:
            _reward_weights[k] = float(v)


def get_reward_weights() -> Dict[str, float]:
    return dict(_reward_weights)


# def compute_reward_components(
#     cart_position: float,
#     cart_velocity: float,
#     pole_angle: float,
#     pole_angular_velocity: float,
#     action: np.ndarray,
#     terminated: bool = False,
# ) -> Dict[str, float]:
#     #computes each reward component from state and action and returns a dictionary of component names to scalar values.
    
#     # Balance: reward for pole being upright (cos(angle) near 1)
#     balance_reward = np.cos(pole_angle)

#     # Upright: same idea, often same as balance; can be scaled differently
#     upright_reward = np.cos(pole_angle)

#     # Cart near center (x=0)
#     cart_center_reward = 1.0 - 0.5 * min(1.0, abs(cart_position) / 2.0)

#     # Velocity penalty (discourage fast motion; optional)
#     velocity_penalty = cart_velocity ** 2 + 0.1 * (pole_angular_velocity ** 2)

#     # Control penalty (discourage large forces)
#     control_penalty = float(action[0] ** 2) if action is not None else 0.0

#     # Termination penalty (optional, when episode ends early)
#     termination_penalty = 1.0 if terminated else 0.0

#     return {
#         "balance": float(balance_reward),
#         "upright": float(upright_reward),
#         "center": float(cart_center_reward),
#         "velocity_penalty": float(velocity_penalty),
#         "control_penalty": float(control_penalty),
#         "termination_penalty": float(termination_penalty),
#     }


# def compute_total_reward(
#     reward_dict: Dict[str, float],
#     weights: Optional[Dict[str, float]] = None,
# ) -> float:
#     # combine components using configurable weights.
#     # total = w_balance*balance + w_upright*upright + w_center*center
#     #        - w_velocity*velocity_penalty - w_control*control_penalty
#     #        - w_termination*termination_penalty
#     w = weights if weights is not None else get_reward_weights()
#     total = (
#         w.get("w_balance", 1.0) * reward_dict["balance"]
#         + w.get("w_upright", 1.0) * reward_dict["upright"]
#         + w.get("w_center", 0.5) * reward_dict["center"]
#         - w.get("w_velocity", 0.01) * reward_dict["velocity_penalty"]
#         - w.get("w_control", 0.001) * reward_dict["control_penalty"]
#         - w.get("w_termination", 0.0) * reward_dict["termination_penalty"]
#     )
#     return float(total)


def reward_standing(_obs: np.ndarray, action: np.ndarray, episode_info: dict, terminated: bool, reward_dict: Dict[str, float],) -> float:
    """
    Compute reward for standing still task.
    
    Args:
        obs: (24,) observation [joint_pos_0...11, joint_vel_0...11]
        action: (12,) action (joint targets)
        episode_info: dict from get_episode_info()
        terminated: bool, True if episode ended
    
    Returns:
        float reward for this step
    """
    reward = 0.0
    
    # ========================================================================
    # 1. UPRIGHT BONUS (most important for standing)
    # ========================================================================
    # Base orientation as quaternion [qx, qy, qz, qw]
    # qw = 1.0 means upright (no rotation)
    # qw = 0.0 means 180° rotation (upside down)
    quat = episode_info["base_orientation"]
    qw = quat[3]
    
    # Smooth bonus that peaks at qw = 1.0
    # At qw = 1.0 (upright): reward = 1.0
    # At qw = 0.5 (45° tilt): reward = 0.25
    # At qw = 0.0 (90° tilt): reward = 0.0
    upright_reward = qw ** 2  # Square makes it more sensitive near upright
    reward += reward_dict["w_upright"] * upright_reward  # Weight: 2.0
    
    # ========================================================================
    # 2. STILLNESS BONUS (stay in place)
    # ========================================================================
    # Penalize movement (want zero velocity)
    base_lin_vel = episode_info["base_linear_velocity"]
    base_ang_vel = episode_info["base_angular_velocity"]
    
    lin_vel_magnitude = np.linalg.norm(base_lin_vel)  # m/s
    ang_vel_magnitude = np.linalg.norm(base_ang_vel)  # rad/s
    
    # Penalize linear movement more than angular (we really want to stay still)
    reward -= reward_dict["w_lin_vel"] * lin_vel_magnitude   # Linear vel penalty
    reward -= reward_dict["w_ang_vel"] * ang_vel_magnitude   # Angular vel penalty (less strict)
    
    # ========================================================================
    # 3. CONTACT BONUS (all feet on ground = stability)
    # ========================================================================
    foot_contact = episode_info["foot_contact"]  # [FL, FR, RL, RR]
    num_feet_in_contact = np.sum(foot_contact)
    
    # Heavy bonus for all 4 feet in contact
    # 4 feet: +0.5
    # 3 feet: +0.375
    # 2 feet: +0.25
    # 1 foot: +0.125
    # 0 feet: 0.0
    contact_reward = reward_dict["w_contact"] * (num_feet_in_contact / 4.0)
    reward += contact_reward

    # bonus: height
    # In reward_standing(), add after contact reward:
    base_height = episode_info["base_height"]
    height_reward = base_height / 0.3  # Normalize to ~0.3m standing height
    reward += reward_dict["w_height"] * height_reward
    
    # ========================================================================
    # 4. ENERGY EFFICIENCY (minimize control effort)
    # ========================================================================
    control_effort = episode_info["energy"]  # sum of squared control values
    reward -= reward_dict["w_control"] * control_effort
    
    # ========================================================================
    # 5. SMOOTH ACTIONS (penalize jitter/oscillation)
    # ========================================================================
    # High action magnitude = jerky movements
    action_magnitude = np.linalg.norm(action)
    reward -= reward_dict["w_action"] * action_magnitude
    
    # ========================================================================
    # 6. FALLING PENALTY (strong negative signal)
    # ========================================================================
    if terminated:
        reward -= reward_dict["w_falling"]
    
    return float(reward), reward_dict