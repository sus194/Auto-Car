#!/bin/bash
# Runs the autocar dashboard in simulation mode.
if [ -d ".venv" ]; then
  source .venv/bin/activate
fi
export PYTHONPATH=src
echo "Starting AutoCar in SIMULATION mode..."
python -m autocar.main --sim --camera 0 --host 127.0.0.1
