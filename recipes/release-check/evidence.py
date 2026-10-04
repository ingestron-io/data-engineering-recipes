"""Bind an offline test record to the files reviewed for release."""
import hashlib
from pathlib import Path

def manifest(directory):
    root = Path(directory)
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file() and "__pycache__" not in p.parts}

def verify(directory, approved):
    actual = manifest(directory)
    if actual != approved:
        raise ValueError("Files changed since review; run checks and approve again")
    return True
