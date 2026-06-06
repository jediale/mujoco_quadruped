# lock down in design - what observation/state 
# (for the multi-layer perceptron, first neuron) is
# available to you. what model would be best?

# Gated recurrent unit (P.I.N.N.)

# MLP is good to start with with hidden layers, enough to cover
# dimensionality of the problem. 


# OG function (way too simple)
"""
policy architecture options for Stable-Baselines3 PPO.

provides MLPPolicySmall and MLPPolicyLarge:
- MLPPolicySmall: 2 hidden layers, 64 units (faster, less capacity)
- MLPPolicyLarge: 3 hidden layers, 256 units (slower, more capacity)

can invoke the policies from train_rl.py by passing policy_kwargs=MLPPolicySmall or policy_kwargs=MLPPolicyLarge.
"""


# READ
# SB3 MlpPolicy uses net_arch: dict(pi=[...], vf=[...]) for actor and critic
# See https://stable-baselines3.readthedocs.io/en/master/modules/ppo.html#ppo-policy

# MLPPolicySmall: Dict[str, Any] = {
#     "net_arch": dict(pi=[64, 64], vf=[64, 64]),
# }

# MLPPolicyLarge: Dict[str, Any] = {
#     "net_arch": dict(pi=[256, 256, 256], vf=[256, 256, 256]),
# }

# POLICY_REGISTRY = {
#     "small": MLPPolicySmall,
#     "large": MLPPolicyLarge,
# }


# end OG function

# 4/20/26 - added new dimensions / options, s m and l

from typing import Dict, Any

# Updated registry with better sized policies for 12-DOF
MLPPolicySmall: Dict[str, Any] = {
    "net_arch": dict(pi=[128, 128], vf=[128, 128]),  # ~35K params
}

MLPPolicyLarge: Dict[str, Any] = {
    "net_arch": dict(pi=[256, 256], vf=[256, 256]),  # ~140K params
}

# Optional: Medium for experimmentation
MLPPolicyMedium: Dict[str, Any] = {
    "net_arch": dict(pi=[128, 64], vf=[128, 64]),    # ~20K params
}

POLICY_REGISTRY = {
    "small": MLPPolicySmall,
    "medium": MLPPolicyMedium,
    "large": MLPPolicyLarge,
}

def get_policy_kwargs(name: str) -> Dict[str, Any]:
    # Get policy_kwargs by name. name in ('small', 'large').
    if name not in POLICY_REGISTRY:
        raise ValueError(f"Unknown policy '{name}'. Choose from: {list(POLICY_REGISTRY)}")
    return POLICY_REGISTRY[name]

