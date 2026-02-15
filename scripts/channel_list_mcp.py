#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import threading
import queue
import time

CMD = ["npx", "-y", "slack-mcp-server@latest", "--transport", "stdio"]
TOKEN = os.environ.get("SLACK_MCP_XOXB_TOKEN")
if not TOKEN:
    sys.stderr.write("SLACK_MCP_XOXB_TOKEN is required\n")
    sys.exit(1)

env = os.environ.copy()
env.setdefault("SLACK_MCP_ADD_MESSAGE_TOOL", "true")

def enqueue(stream, q):
    for line in stream:
        q.put(line.rstrip())
    stream.close()

proc = subprocess.Popen(
    CMD,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    env=env,
)

stdout_queue = queue.Queue()
stderr_queue = queue.Queue()
threading.Thread(target=enqueue, args=(proc.stdout, stdout_queue), daemon=True).start()
threading.Thread(target=enqueue, args=(proc.stderr, stderr_queue), daemon=True).start()

def send(msg_id, method, params):
    payload = json.dumps({"jsonrpc": "2.0", "id": msg_id, "method": method, "params": params})
    proc.stdin.write(payload + "\n")
    proc.stdin.flush()

def wait_for(msg_id, timeout=30):
    deadline = time.time() + timeout
    while time.time() < deadline:
        # stderr logging
        try:
            err_line = stderr_queue.get_nowait()
            print(err_line, file=sys.stderr)
        except queue.Empty:
            pass
        try:
            line = stdout_queue.get(timeout=0.5)
        except queue.Empty:
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
        if data.get("id") == msg_id:
            return data
    raise TimeoutError(f"No response for id {msg_id}")

try:
    send(1, "initialize", {"capabilities": {}})
    init_resp = wait_for(1)
    if "error" in init_resp:
        raise RuntimeError(init_resp)

    attempts = 0
    while True:
        attempts += 1
        send(2, "tools/call", {
            "name": "channels_list",
            "arguments": {"channel_types": "public_channel,private_channel,mpim,im", "limit": 200}
        })
        tool_resp = wait_for(2)
        if "error" in tool_resp:
            msg = tool_resp["error"].get("message", "")
            if "cache" in msg and attempts < 5:
                time.sleep(2)
                continue
            raise RuntimeError(tool_resp)
        print(json.dumps(tool_resp.get("result", {}), ensure_ascii=False, indent=2))
        break
finally:
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
