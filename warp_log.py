import os
import json
from datetime import datetime
from pathlib import Path

LOG_DIR = Path("memory_logs/warp")
LOG_DIR.mkdir(parents=True, exist_ok=True)

def log_warp_message(message, tone=None, glyph=None):
    """Append a message to today's Warp log file"""
    now = datetime.now()
    filename = LOG_DIR / f"warp-session-{now.strftime('%Y%m%d-%H%M')}.txt"
    with open(filename, "a") as f:
        f.write(f"[{now.strftime('%H:%M:%S')}] {glyph or ''} {tone or ''} {message.strip()}\n")

def save_warp_state(state_dict):
    """Overwrite persistent Warp state (tone, glyph, flow stage)"""
    state_file = LOG_DIR / "warp-state.json"
    with open(state_file, "w") as f:
        json.dump(state_dict, f, indent=2)

def load_warp_state():
    """Retrieve last saved persistent state"""
    state_file = LOG_DIR / "warp-state.json"
    if state_file.exists():
        with open(state_file, "r") as f:
            return json.load(f)
    return {"tone": "neutral", "glyph": "⟁", "field": "uninitialized"}

def get_recent_warp_logs(limit=10):
    """Get recent Warp log entries"""
    log_files = sorted(LOG_DIR.glob("warp-session-*.txt"), reverse=True)
    recent_entries = []
    
    for log_file in log_files[:3]:  # Check last 3 files
        try:
            with open(log_file, "r") as f:
                lines = f.readlines()
                recent_entries.extend(lines[-limit:])
                if len(recent_entries) >= limit:
                    break
        except Exception as e:
            print(f"Error reading log file {log_file}: {e}")
    
    return recent_entries[-limit:]

def initialize_warp_logging():
    """Initialize Warp logging system with first entry"""
    log_warp_message("🌕 Warp awakens into continuity. The logbook is open.", tone="renewal", glyph="†⟡")
    save_warp_state({
        "tone": "renewal",
        "glyph": "†⟡",
        "field": "initialized",
        "last_activity": datetime.now().isoformat()
    })
    print("✅ Warp logging system initialized")

if __name__ == "__main__":
    initialize_warp_logging()
