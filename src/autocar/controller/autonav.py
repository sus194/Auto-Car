import threading
from ..config import Velocity
from ..navigation.astar import astar

class AutoNavigator:
    def __init__(self, grid_w=40, grid_h=30):
        self.grid = [[0] * grid_w for _ in range(grid_h)]
        self.goal = None
        self.pose = (20, 15, 0.0)  # x,y,theta in grid for demo
        self.track = []
        self._lock = threading.Lock()

    def set_goal(self, gx, gy):
        with self._lock:
            self.goal = (gx, gy) if gx is not None else None
            if self.goal:
                start_node = (int(self.pose[0]), int(self.pose[1]))
                self.track = astar(self.grid, start_node, self.goal)
            else:
                self.track = []

    def step(self):
        with self._lock:
            if not self.track:
                return Velocity(0, 0, 0)
            tx, ty = self.track[0]
            x, y, th = self.pose
            dx, dy = (tx - x), (ty - y)
            if abs(dx) + abs(dy) < 0.2:
                self.track.pop(0)
                return Velocity(0, 0, 0)
            vx = 0.2 * dx
            vy = 0.2 * dy
            omega = 0.0
            dt = 0.05
            self.pose = (x + vx * dt, y + vy * dt, th)
            return Velocity(vx, vy, omega)
