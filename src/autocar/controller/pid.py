import time

class PID:
    def __init__(self, kp, ki, kd, i_limit=1.0, out_limit=1.0):
        self.kp, self.ki, self.kd = kp, ki, kd
        self.i_limit = i_limit
        self.out_limit = out_limit
        self._i = 0.0
        self._prev_err = 0.0
        self._tprev = None

    def reset(self):
        self._i = 0.0
        self._prev_err = 0.0
        self._tprev = None

    def update(self, target, measured):
        t = time.time()
        if self._tprev is None:
            self._tprev = t
        dt = max(1e-3, t - self._tprev)
        self._tprev = t

        err = target - measured
        self._i += err * dt
        self._i = max(-self.i_limit, min(self.i_limit, self._i))
        d = (err - self._prev_err) / dt
        self._prev_err = err

        out = self.kp * err + self.ki * self._i + self.kd * d
        out = max(-self.out_limit, min(self.out_limit, out))
        return out
