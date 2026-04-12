from collections import deque
import json
import os
from datetime import datetime

# In-memory storage for fast access
MEMORY = deque(maxlen=200)  # Fire limit

# File-based persistent storage
MEMORY_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'memory_store.json')

def _load_memory_from_file():
    """Load memory from file on startup"""
    try:
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Load into memory deque (keep most recent 200)
                for entry in data[-200:]:
                    MEMORY.append(entry)
                print(f"Loaded {len(data)} entries from persistent storage")
    except Exception as e:
        print(f"Warning: Could not load memory from file: {e}")

def _save_memory_to_file():
    """Save memory to file for persistence"""
    try:
        # Ensure data directory exists
        os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
        
        # Save all memory entries to file
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(list(MEMORY), f, indent=2, ensure_ascii=False)
        print(f"Saved {len(MEMORY)} entries to persistent storage")
    except Exception as e:
        print(f"Warning: Could not save memory to file: {e}")

def save(entry):
    """Save entry to both memory and file"""
    # Add timestamp if not present
    if 'timestamp' not in entry:
        entry['timestamp'] = datetime.now().isoformat()
    
    MEMORY.append(entry)
    _save_memory_to_file()

def get_success():
    """Get successful entries (score >= 10)"""
    return [m for m in MEMORY if m.get("score", 0) >= 10]

def get_recent(n=10):
    """Get most recent n entries"""
    return list(MEMORY)[-n:]

def get_all():
    """Get all memory entries"""
    return list(MEMORY)

def clear_memory():
    """Clear all memory (both in-memory and file)"""
    MEMORY.clear()
    try:
        if os.path.exists(MEMORY_FILE):
            os.remove(MEMORY_FILE)
            print("Memory file cleared")
    except Exception as e:
        print(f"Warning: Could not clear memory file: {e}")

# Load existing memory on module import
_load_memory_from_file()
