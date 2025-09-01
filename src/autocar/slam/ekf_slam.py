import numpy as np

class EKFSLAM:
    """Minimal landmark-based EKF SLAM skeleton."""
    def __init__(self):
        self.x = np.zeros((3, 1))  # [x, y, theta]
        self.P = np.eye(3) * 1e-3
        self.landmarks = {}  # id -> index in state vector

    def predict(self, v, omega, dt, Q=np.diag([1e-3, 1e-3, 1e-3])):
        x, y, th = self.x.flatten()[:3]
        if abs(omega) < 1e-6:
            x += v * np.cos(th) * dt
            y += v * np.sin(th) * dt
        else:
            radius = v / omega
            x += radius * (np.sin(th + omega * dt) - np.sin(th))
            y += radius * (-np.cos(th + omega * dt) + np.cos(th))
        th = (th + omega * dt + np.pi) % (2 * np.pi) - np.pi
        self.x[:3, 0] = [x, y, th]
        self.P[:3, :3] += Q

    def update_landmark(self, lm_id, z, R=np.diag([1e-2, 1e-2])):
        if lm_id not in self.landmarks:
            idx = 3 + 2 * len(self.landmarks)
            self.landmarks[lm_id] = idx
            if self.x.shape[0] < idx + 2:
                nx = np.zeros((idx + 2, 1))
                nx[:self.x.shape[0], 0] = self.x[:, 0]
                self.x = nx
                nP = np.eye(idx + 2) * 1e-3
                nP[:self.P.shape[0], :self.P.shape[1]] = self.P
                self.P = nP
            r, b = z
            xr, yr, th = self.x[0, 0], self.x[1, 0], self.x[2, 0]
            self.x[idx:idx+2, 0] = [xr + r * np.cos(th + b), yr + r * np.sin(th + b)]
        # Full EKF update omitted for brevity.
