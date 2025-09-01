from dataclasses import dataclass
from ..config import Velocity, MAX_VX, MAX_VY, MAX_OMEGA

@dataclass
class TeleopState:
    turbo: float = 1.0  # 1.0..2.0

class TeleopController:
    def __init__(self):
        self.state = TeleopState()
        self.vel = Velocity(0.0, 0.0, 0.0)

    def set_from_axes(self, ax_x: float, ax_y: float, ax_rot: float, turbo=False):
        scale = 2.0 if turbo else 1.0
        self.vel = Velocity(
            vx=max(-MAX_VX, min(MAX_VX, ax_x * MAX_VX * scale)),
            vy=max(-MAX_VY, min(MAX_VY, -ax_y * MAX_VY * scale)),  # invert Y
            omega=max(-MAX_OMEGA, min(MAX_OMEGA, ax_rot * MAX_OMEGA * scale)),
        )
        return self.vel

    def set_zero(self):
        self.vel = Velocity(0.0, 0.0, 0.0)
        return self.vel
