import hashlib

def hash_content(content: str) -> str:
    """Create a SHA-256 hash of string content."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()
