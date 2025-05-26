import os
from pathlib import Path
from typing import Optional
import requests

DATA_DIR = Path("data/raw")
DATA_DIR.mkdir(parents=True, exist_ok=True)

def fetch_csv(url: str, filename: Optional[str] = None) -> Path:
    """Download a CSV from a URL and cache it under data/raw."""
    if filename is None:
        filename = os.path.basename(url)
    path = DATA_DIR / filename
    if path.exists():
        return path
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    path.write_bytes(resp.content)
    return path
