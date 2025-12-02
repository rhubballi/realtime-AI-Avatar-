import sys
import os
import threading
import subprocess
import time
import signal

def _stream_proc(name, proc):
    try:
        for line in proc.stdout:
            print(f"[{name}] {line.rstrip()}")
    except Exception:
        pass

def main():
    root = os.path.dirname(os.path.abspath(__file__))  # backend folder
    python = sys.executable

    # Try common agent subcommands until one actually starts the agent.
    def try_start_agent(candidates=("start", "dev", "console")):
        last_output = None
        for cmd in candidates:
            agent_cmd = [python, "avatar_agent.py", cmd]
            p = subprocess.Popen(agent_cmd, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            # give it a moment to either start or exit with a helpful message
            time.sleep(1)
            if p.poll() is None:
                return p, cmd
            # process exited quickly — capture and print output to help debugging
            try:
                out, _ = p.communicate(timeout=1)
            except Exception:
                out = ""
            last_output = out
            if out:
                for line in out.splitlines():
                    print(f"[AGENT-TRY:{cmd}] {line}")
        return None, last_output

    p_agent, agent_ok = try_start_agent()
    if p_agent is None:
        print("Failed to start agent using known subcommands. Last output:\n", agent_ok)
        return

    p_server = subprocess.Popen([python, "server.py"], cwd=root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    t1 = threading.Thread(target=_stream_proc, args=("AGENT", p_agent), daemon=True)
    t2 = threading.Thread(target=_stream_proc, args=("SERVER", p_server), daemon=True)
    t1.start()
    t2.start()

    try:
        while True:
            if p_agent.poll() is not None or p_server.poll() is not None:
                break
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        for p in (p_agent, p_server):
            if p and p.poll() is None:
                try:
                    p.terminate()
                except Exception:
                    pass
        time.sleep(1)
        for p in (p_agent, p_server):
            if p and p.poll() is None:
                try:
                    p.kill()
                except Exception:
                    pass

if __name__ == "__main__":
    main()