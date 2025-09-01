import time
from typing import List

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    _HAS_GPIO = True
except Exception:
    _HAS_GPIO = False

class MotorDriver:
    """4-wheel omni/mecanum driver. Duty [-1,1] per wheel in order: FL, FR, RL, RR"""
    def init(self, pwm_pins: List[int], dir_pins: List[int], pwm_freq: int = 20000):
        self.pwm_pins = pwm_pins
        self.dir_pins = dir_pins
        self.pwm_freq = pwm_freq
        self._sim_state = [0.0, 0.0, 0.0, 0.0]

        if _HAS_GPIO:
            for p in (*pwm_pins, *dir_pins):
                GPIO.setup(p, GPIO.OUT)
            self._pwms = []
            for p in pwm_pins:
                pwm = GPIO.PWM(p, pwm_freq)
                pwm.start(0)
                self._pwms.append(pwm)
        else:
            print("[MotorDriver] GPIO not available -> SIM mode")

    def set_duties(self, duties: List[float]):
        duties = [max(-1.0, min(1.0, d)) for d in duties]
        if _HAS_GPIO:
            for i, d in enumerate(duties):
                direction = GPIO.HIGH if d >= 0 else GPIO.LOW
                GPIO.output(self.dir_pins[i], direction)
                self._pwms[i].ChangeDutyCycle(abs(d) * 100.0)
        else:
            self._sim_state = duties
            print(f"[MotorDriver/SIM] duties={[f'{d:.2f}' for d in duties]}")

    def brake(self):
        if _HAS_GPIO:
            for pwm in getattr(self, "_pwms", []):
                pwm.ChangeDutyCycle(0.0)
        else:
            self._sim_state = [0.0]*4
            print("[MotorDriver/SIM] brake")

    def close(self):
        if _HAS_GPIO:
            print("Cleaning up GPIO...")
            for pwm in getattr(self, "_pwms", []):
                pwm.stop()
            GPIO.cleanup()
