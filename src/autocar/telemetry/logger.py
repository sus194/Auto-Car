import time, csv, pathlib

class Logger:
    def __init__(self, path="telemetry.csv"):
        self.path = pathlib.Path(path)
        self._fh = self.path.open("a", newline="")
        self._w = csv.writer(self._fh)
        if self.path.stat().st_size == 0:
            self._w.writerow(["ts", "vx_cmd", "vy_cmd", "omega_cmd", "w_fl", "w_fr", "w_rl", "w_rr"])

    def write(self, vx, vy, omega, wheels):
        self._w.writerow([time.time(), vx, vy, omega, *wheels])
        self._fh.flush()
