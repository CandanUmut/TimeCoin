import hashlib
import json

def generate_hash(data):
    """Generate a SHA-256 hash for the given data."""
    data_string = json.dumps(data, sort_keys=True)
    return hashlib.sha256(data_string.encode()).hexdigest()
