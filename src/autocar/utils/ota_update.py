import subprocess
import shlex

def apply_git_pull():
    """Runs 'git pull' and returns the output or error."""
    try:
        cmd = "git pull"
        out = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT, timeout=30)
        return out.decode("utf-8", "ignore")
    except Exception as e:
        return f"OTA failed: {e}"
