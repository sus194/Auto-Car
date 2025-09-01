import time
import threading
import numpy as np
import cv2

try:
    from picamera2 import Picamera2
    _HAS_PICAMERA2 = True
except Exception:
    _HAS_PICAMERA2 = False

class Camera:
    def init(self, width=640, height=480, fps=24, use_picamera2=False, index=0):
        self.width, self.height, self.fps = width, height, fps
        self._lock = threading.Lock()
        self._frame = None
        self._stopped = False

        if use_picamera2 and _HAS_PICAMERA2:
            self.cam = Picamera2()
            cfg = self.cam.create_still_configuration(main={"size": (width, height)})
            self.cam.configure(cfg)
            self.cam.start()
            self.backend = "picamera2"
        else:
            self.cap = cv2.VideoCapture(index)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.cap.set(cv2.CAP_PROP_FPS, fps)
            self.backend = "opencv"

        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def _loop(self):
        period = 1.0 / max(1, self.fps)
        while not self._stopped:
            if self.backend == "picamera2":
                frame = self.cam.capture_array()
            else:
                ok, frame = self.cap.read()
                if not ok:
                    time.sleep(0.05)
                    continue
            with self._lock:
                self._frame = frame
            time.sleep(period * 0.5)

    def read(self):
        with self._lock:
            return None if self._frame is None else self._frame.copy()

    def close(self):
        self._stopped = True
        if hasattr(self, 'thread'):
            self.thread.join(timeout=1)
        if self.backend == "opencv":
            self.cap.release()
        elif self.backend == "picamera2":
            self.cam.stop()
