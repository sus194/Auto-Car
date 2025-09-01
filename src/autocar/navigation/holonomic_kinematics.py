import numpy as np
from ..config import WHEEL_BASE_X_M, WHEEL_BASE_Y_M, WHEEL_RADIUS_M, MAX_WHEEL_RPS

# Mecanum/omni 4-wheel inverse kinematics:
# [w_fl, w_fr, w_rl, w_rr]^T = (1/R) * J @ [vx, vy, omega]^T
L = WHEEL_BASE_X_M + WHEEL_BASE_Y_M
K = np.array([
    [1, -1, -L],
    [1,  1,  L],
    [1,  1, -L],
    [1, -1,  L],
], dtype=float) / max(1e-6, WHEEL_RADIUS_M)

def body_to_wheel_rps(vx, vy, omega):
    """Converts body velocity (vx, vy, omega) to wheel speeds in RPS."""
    vel = np.array([vy, vx, omega], dtype=float)  # axis mapping per robot frame
    wheel_rad_s = K @ vel
    wheel_rps = wheel_rad_s / (2 * np.pi)
    wheel_rps = np.clip(wheel_rps, -MAX_WHEEL_RPS, MAX_WHEEL_RPS)
    return wheel_rps.tolist()
