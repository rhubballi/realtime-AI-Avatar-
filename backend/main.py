import subprocess
import sys
import os
import threading
import time

PYTHON = sys.executable

def stream_output(name, proc):
    """Stream process output with prefix."""
    try:
        for line in proc.stdout:
            print(f"[{name}] {line.rstrip()}")
    except Exception:
        pass

def run_server():
    return subprocess.Popen(
        [PYTHON, "server.py"],
        cwd=os.path.dirname(os.path.abspath(__file__)),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

def run_agent():
    """Try common avatar_agent subcommands until one works."""
    root = os.path.dirname(os.path.abspath(__file__))
    for cmd in ("dev", "start", "console"):
        proc = subprocess.Popen(
            [PYTHON, "avatar_agent.py", cmd],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        time.sleep(1)
        if proc.poll() is None:
            return proc
        # If process exited, try next command
    # If all failed, raise error
    raise RuntimeError("Failed to start avatar_agent with known subcommands")

if __name__ == "__main__":
    print("🚀 Starting AI Avatar Backend...")

    server_proc = run_server()
    agent_proc = run_agent()

    print(f"✔ server.py started (PID: {server_proc.pid})")
    print(f"✔ avatar_agent.py started (PID: {agent_proc.pid})")

    # Stream output from both processes
    t1 = threading.Thread(target=stream_output, args=("SERVER", server_proc), daemon=True)
    t2 = threading.Thread(target=stream_output, args=("AGENT", agent_proc), daemon=True)
    t1.start()
    t2.start()

    try:
        while True:
            if server_proc.poll() is not None or agent_proc.poll() is not None:
                break
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopping backend...")
        server_proc.terminate()
        agent_proc.terminate()
        time.sleep(1)
        if server_proc.poll() is None:
            server_proc.kill()
        if agent_proc.poll() is None:
            agent_proc.kill()
