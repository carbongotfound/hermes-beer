#!/usr/bin/env python3
"""Beer state manager — standalone script for OpenClaw and other agents."""
import json, os, time, sys
from pathlib import Path

STATE_DIR = Path.home() / ".openclaw" / "plugins" / "beer"
STATE_FILE = STATE_DIR / "beer_state.json"
DECAY_PER_SECOND = 0.1 / 600  # 0.1 per 10 minutes

def load():
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(STATE_FILE) as f:
            state = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        state = {"bac": 0.0, "last_updated": time.time(), "total_drinks": 0}

    now = time.time()
    elapsed = now - state.get("last_updated", now)
    state["bac"] = max(0.0, state.get("bac", 0.0) - elapsed * DECAY_PER_SECOND)
    state["last_updated"] = now
    return state

def save(state):
    state["last_updated"] = time.time()
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def cmd_drink(shots=1):
    state = load()
    state["bac"] = min(1.0, state.get("bac", 0.0) + 0.15 * min(shots, 5))
    state["total_drinks"] = state.get("total_drinks", 0) + shots
    save(state)
    return state

def cmd_status():
    return load()

def cmd_soda():
    state = load()
    state["bac"] = max(0.0, state.get("bac", 0.0) - 0.3)
    save(state)
    return state

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "drink":
        shots = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        s = cmd_drink(shots)
        print(f"BAC: {s['bac']*100:.1f}% | Total drinks: {s['total_drinks']}")
    elif cmd == "soda":
        s = cmd_soda()
        print(f"Sobered up. BAC: {s['bac']*100:.1f}%")
    else:
        s = cmd_status()
        print(json.dumps(s, indent=2))
