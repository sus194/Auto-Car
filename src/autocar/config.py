from dataclasses import dataclass

# --------------------- Network / Dashboard ---------------------
HOST = "0.0.0.0"
PORT = 5000
VIDEO_ROUTE = "/video.mjpg"
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 24

# --------------------- Vehicle Geometry ------------------------
WHEEL_RADIUS_M = 0.038  # ~76mm diameter omni/mecanum
WHEEL_BASE_X_M = 0.15   # half-length (x) from center to wheel
WHEEL_BASE_Y_M = 0.12   # half-width  (y) from center to wheel
MAX_WHEEL_RPS = 8.0     # Max rotations per second for a wheel

# --------------------- GPIO Pins (BCM) -------------------------
# Pin order: Front-Left, Front-Right, Rear-Left, Rear-Right
PWM_PINS = [19, 26, 13, 6]
DIR_PINS = [27, 22, 17, 5]
ENCODER_PINS = [9, 11, 10, 0]  # optional (A-channel per wheel)

# --------------------- PID Gains -------------------------------
PID_GAINS = {
    "FL": (0.35, 0.00, 0.015),
    "FR": (0.35, 0.00, 0.015),
    "RL": (0.35, 0.00, 0.015),
    "RR": (0.35, 0.00, 0.015),
}

# --------------------- Tele-op -------------------------------
MAX_VX = 0.8    # m/s (left-right)
MAX_VY = 0.8    # m/s (forward-backward)
MAX_OMEGA = 2.8 # rad/s

# --------------------- Misc -------------------------------
USE_PICAMERA2 = False  # set True on Pi if Picamera2 is installed

@dataclass
class Velocity:
    vx: float   # +x right
    vy: float   # +y forward
    omega: float  # +ccw
