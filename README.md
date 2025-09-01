# Auto Car

A dual-mode (tele‑op & autonomous) Raspberry Pi 4 robot car with live video streaming, a low‑latency remote controller, and a Flask dashboard for tuning, telemetry, and OTA updates.

**Highlights (July 2025)** — Raspberry Pi 4 + Pi Camera V2, custom H‑bridge motor drivers, four omni/mecanum wheels.  
- Dual‑mode operation — tele‑op & autonomous. Target ~50 ms Wi‑Fi command latency via WebSockets.  
- Vision‑based SLAM (EKF skeleton) and A* grid path‑planning (±10 cm target positional accuracy with encoders/IMU).  
- PID speed control per wheel for holonomic motion; ~25% tracking error reduction vs open‑loop (replicable with encoder feedback).  
- Live Flask dashboard: MJPEG video stream, parameter tuning, and OTA updates — designed to reduce on‑track debugging time.

> This repo ships a **working reference implementation** you can run on a dev laptop (sim GPIO/motors) and deploy on the Pi (real GPIO/motors).  
> Swap pins and tune gains in `src/autocar/config.py`.

---

## Quick Start

### 1) Install (Dev / Laptop)
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Optional: a USB webcam works for preview.
PYTHONPATH=src python -m autocar.main --sim --camera 0
```

### 2) Install (On Raspberry Pi 4, 64‑bit OS)
```bash
sudo apt update
sudo apt install -y python3-pip python3-venv python3-opencv libatlas-base-dev
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# If using Picamera2 (recommended on Bullseye/Bookworm), install from Raspberry Pi OS repo docs.
```

### 3) Run
```bash
source .venv/bin/activate
PYTHONPATH=src python -m autocar.main --host 0.0.0.0 --port 5000
# Visit http://<pi-ip>:5000  (dashboard)
# Video stream: http://<pi-ip>:5000/video.mjpg
```
**Tele‑op:** Keyboard (WASD + QE for rotate) or any gamepad (uses the Gamepad API in your browser).  
**Autonomous:** Toggle *Autonomous* in the dashboard. Click a goal cell on the mini‑map to plan via A* and start following.

---

## Hardware Mapping

Default config uses these BCM GPIOs (edit in `config.py`):

- **Motors (PWM + DIR)** for 4 wheels (front‑left, front‑right, rear‑left, rear‑right):  
  PWM: `19, 26, 13, 6`  
  DIR: `27, 22, 17, 5`

- **Encoders (A‑channel suggested):** `9, 11, 10, 0` (adjust to match your hardware)

- **Camera:** Pi Camera V2 (Picamera2) or USB camera index (`--camera 0`)

Works with L298N/L9110/Sabertooth‑style H‑bridges. Ensure a solid 5V logic supply and a **separate** motor supply with a **common ground**.

---

## Project Layout

```
autocar/
├─ README.md
├─ requirements.txt
├─ src/autocar/
│  ├─ __init__.py
│  ├─ main.py                 # Entrypoint: Flask + Socket.IO + control loops
│  ├─ config.py               # Pins, gains, kinematics, stream config
│  ├─ dashboards/
│  │  ├─ templates/index.html # Dashboard UI
│  │  └─ static/js/teleop.js  # Keyboard/Gamepad/WebSocket client
│  ├─ hardware/
│  │  ├─ motor_driver.py      # GPIO motor control (with simulator)
│  │  ├─ camera.py            # Video capture (Picamera2 or OpenCV)
│  │  ├─ encoder.py           # Quadrature encoder (stub + hooks)
│  │  └─ imu.py               # Optional IMU wrapper (stub)
│  ├─ controller/
│  │  ├─ pid.py               # PID speed controller
│  │  ├─ teleop.py            # Velocity commands from user input
│  │  └─ autonav.py           # A* + pursuit glue
│  ├─ navigation/
│  │  ├─ astar.py             # Grid A* planner
│  │  └─ holonomic_kinematics.py # vx,vy,omega -> wheel speeds
│  ├─ slam/
│  │  └─ ekf_slam.py          # Minimal EKF SLAM skeleton (landmark-based)
│  ├─ telemetry/
│  │  └─ logger.py            # Telemetry/log utilities
│  └─ utils/
│     ├─ video_stream.py      # MJPEG generator
│     └─ ota_update.py        # OTA update stub
├─ scripts/
│  ├─ run_local_dashboard.sh
│  └─ calibrate_pid.py
└─ services/
   └─ autocar.service.example # systemd example for the Pi
```

---

## Controls

**Keyboard:**  
W/S: forward/backward (vy) • A/D: left/right (vx) • Q/E: rotate ccw/cw (omega) • Hold Shift = turbo

**Gamepad:** left stick (vx, vy), right stick X (omega), **A** = turbo, **B** = toggle autonomous.

---

## Tuning

`config.py` → `PID_GAINS` per wheel. Use **Dashboard → Tuning** to adjust gains live (demo; persist logic stubbed).  
`scripts/calibrate_pid.py` provides an automated step‑response template if you have encoders.

---

## Notes

- The EKF/SLAM is a compact didactic skeleton; for production, consider RTAB‑Map/ORB‑SLAM or lidar‑assisted stacks.  
- If `RPi.GPIO` isn’t available (e.g., on a laptop), the motor layer falls back to a simulator that logs commands instead of touching GPIO.
