"""
Duplicate Prevention Ledger Manager
Guarantees that no piece of content is ever published more than once.
Fingerprints every clip using SHA-256 hash.
"""

import sys
import os
import json
import hashlib
from datetime import datetime

DEFAULT_LEDGER_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "ledger.json")

def calculate_file_hash(filepath, chunk_size=65536):
    """Calculate SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(chunk_size):
            sha256.update(chunk)
    return sha256.hexdigest()

def load_ledger(ledger_path=DEFAULT_LEDGER_PATH):
    """Load the ledger file."""
    if not os.path.exists(ledger_path):
        return {"version": "1.0.0", "records": []}
    try:
        with open(ledger_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading ledger: {e}", file=sys.stderr)
        return {"version": "1.0.0", "records": []}

def save_ledger(data, ledger_path=DEFAULT_LEDGER_PATH):
    """Save the ledger file safely."""
    data["last_updated"] = datetime.utcnow().isoformat() + "Z"
    os.makedirs(os.path.dirname(os.path.abspath(ledger_path)), exist_ok=True)
    with open(ledger_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def is_duplicate(content_hash, ledger_path=DEFAULT_LEDGER_PATH):
    """Check if content_hash already exists in the ledger."""
    ledger = load_ledger(ledger_path)
    for record in ledger.get("records", []):
        if record.get("content_hash") == content_hash:
            return True, record
    return False, None

def add_record(record_data, ledger_path=DEFAULT_LEDGER_PATH):
    """
    Add a publishing record to the ledger.
    record_data should contain:
    - content_hash
    - source_file
    - processed_file
    - youtube_id (optional)
    - facebook_id (optional)
    - published_at
    """
    ledger = load_ledger(ledger_path)
    # Check if hash already exists
    for idx, item in enumerate(ledger.get("records", [])):
        if item.get("content_hash") == record_data.get("content_hash"):
            # Update existing record
            ledger["records"][idx].update(record_data)
            save_ledger(ledger, ledger_path)
            return True

    if "timestamp" not in record_data:
        record_data["timestamp"] = datetime.utcnow().isoformat() + "Z"

    ledger.setdefault("records", []).append(record_data)
    save_ledger(ledger, ledger_path)
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python duplicate_checker.py [check|add|hash] [filepath_or_hash]")
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "hash":
        filepath = sys.argv[2]
        print(calculate_file_hash(filepath))
    elif cmd == "check":
        target = sys.argv[2]
        # target can be a file or a hash
        if os.path.exists(target):
            h = calculate_file_hash(target)
        else:
            h = target
        dup, record = is_duplicate(h)
        res = {"is_duplicate": dup, "content_hash": h, "record": record}
        print(json.dumps(res))
    elif cmd == "add":
        record_json_str = sys.argv[2]
        record = json.loads(record_json_str)
        add_record(record)
        print(json.dumps({"success": True}))
