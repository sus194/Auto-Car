import argparse
import threading
import time
from flask import Flask, render_template, Response
from flask_socketio import SocketIO, emit
import numpy as np

from . import config
from .hardware.motor_driver import MotorDriver
from .hardware.camera import Camera
from .hardware.encoder import EncoderReader
from .controller.teleop import TeleopController
from .controller.autonav import AutoNavigator
from .navigation.holonomic_kinematics import body_to_wheel_rps
from .controller.pid import PID
from .utils.video_stream import gen_mjpeg
from .utils.ota_update import apply_git_pull
from .telemetry.logger import Logger

# --- App Initialization ---
app = Flask(__name__, template_folder="dashboards/templates", static_folder="dashboards/static")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# --- Global State & Modules ---
is_sim = False
camera = None
motor_driver = MotorDriver()
teleop = TeleopController()
autonav = AutoNavigator()
logger = Logger()
state = {'is_autonomous': False, 'target_vel': config.Velocity(0, 0, 0)}

# --- Web Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route(config.VIDEO_ROUTE)
def video_feed():
    if camera:
        return Response(gen_mjpeg(camera, config.FPS),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    return "Camera not available."

# --- WebSocket Events ---
@socketio.on('connect')
def on_connect():
    print("Dashboard connected")

@socketio.on('disconnect')
def on_disconnect():
    print("Dashboard disconnected")
    state['target_vel'] = config.Velocity(0, 0, 0)  # Safety stop

@socketio.on('axes')
def on_axes(data):
    """Handle tele-op commands from keyboard or gamepad."""
    if not state['is_autonomous']:
        vel = teleop.set_from_axes(data['ax'], data['ay'], data['rot'], data.get('turbo', False))
        vel.vx *= data.get('speed', 1.0)
        vel.vy *= data.get('speed', 1.0)
        state['target_vel'] = vel

@socketio.on('brake')
def on_brake(data):
    """Handle brake command."""
    state['target_vel'] = config.Velocity(0, 0, 0)
    motor_driver.brake()

@socketio.on('auton')
def on_auton(data):
    """Toggle autonomous mode."""
    state['is_autonomous'] = data.get('enabled', False)
    if not state['is_autonomous']:
        state['target_vel'] = config.Velocity(0, 0, 0)
    print(f"Autonomous mode: {'ON' if state['is_autonomous'] else 'OFF'}")

@socketio.on('goal')
def on_goal(data):
    """Set autonomous navigation goal."""
    if data['x'] >= 0:
        autonav.set_goal(data['x'], data['y'])
        print(f"New goal set: ({data['x']}, {data['y']})")
    else:
        autonav.set_goal(None, None)  # Clear goal
        print("Goal cleared")

@socketio.on('pid')
def on_pid(data):
    """Handle PID gain updates from dashboard (for demo)."""
    kp, ki, kd = data['kp'], data['ki'], data['kd']
    print(f"Received new PID gains: Kp={kp}, Ki={ki}, Kd={kd}")
    emit('pid_ack', {'ok': True})

@socketio.on('ota')
def on_ota(data):
    """Handle Over-The-Air update request."""
    print("OTA update requested...")
    result = apply_git_pull()
    emit('ota_response', {'log': result})
    print(result)

# --- Control Loop Thread ---
def control_loop():
    """Main control loop running in a background thread."""
    while True:
        if state['is_autonomous']:
            # Autonomous mode: get velocity from the navigator
            state['target_vel'] = autonav.step()
        
        # Get target body velocity (vx, vy, omega)
        vel = state['target_vel']
        
        # Convert body velocity to target wheel speeds (rotations per second)
        target_wheel_rps = body_to_wheel_rps(vel.vx, vel.vy, vel.omega)
        
        # Map RPS to motor duty cycles (open-loop baseline)
        duties = [rps / config.MAX_WHEEL_RPS for rps in target_wheel_rps]
        
        # Set motor duties
        motor_driver.set_duties(duties)
        
        # Log telemetry data
        logger.write(vel.vx, vel.vy, vel.omega, target_wheel_rps)
        
        # Loop at ~50 Hz
        time.sleep(0.02)

# --- Main Entry Point ---
def main():
    global is_sim, camera
    parser = argparse.ArgumentParser(description="AutoCar Main Control")
    parser.add_argument('--sim', action='store_true', help="Run in simulation mode (no GPIO)")
    parser.add_argument('--host', type=str, default=config.HOST, help="Host address to bind to")
    parser.add_argument('--port', type=int, default=config.PORT, help="Port to run the web server on")
    parser.add_argument('--camera', type=int, default=0, help="Camera index for OpenCV")
    args = parser.parse_args()
    is_sim = args.sim

    # --- Hardware Initialization ---
    try:
        motor_driver.init(config.PWM_PINS, config.DIR_PINS)
        print("Motor driver initialized.")

        camera = Camera()
        camera.init(width=config.FRAME_WIDTH, height=config.FRAME_HEIGHT, fps=config.FPS,
                    use_picamera2=config.USE_PICAMERA2 and not is_sim, index=args.camera)
        print(f"Camera initialized using backend: {camera.backend}")
        
        # Start control loop in a background thread
        control_thread = threading.Thread(target=control_loop, daemon=True)
        control_thread.start()
        print("Control loop started.")

        # Start Flask-SocketIO server
        print(f"Starting dashboard at http://{args.host}:{args.port}")
        socketio.run(app, host=args.host, port=args.port)

    except KeyboardInterrupt:
        print("\nCaught Ctrl+C. Shutting down...")
    finally:
        motor_driver.close()
        if camera:
            camera.close()
        print("Cleanup complete. Exiting.")

if __name__ == '__main__':
    main()
