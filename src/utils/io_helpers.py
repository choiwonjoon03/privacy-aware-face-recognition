# src/utils/io_helpers.py
from pathlib import Path
from typing import Dict, List
import csv
import os

from dotenv import load_dotenv

def ensure_parent_dir(path_str: str) -> None:
    Path(path_str).parent.mkdir(parents=True, exist_ok=True)

def save_csv(rows: List[Dict], fieldnames: List[str], out_path: str) -> None:
    ensure_parent_dir(out_path)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

def load_env() -> Dict[str, str]:
    load_dotenv()  # loads .env if present
    return {
        "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID", ""),
        "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY", ""),
        "AWS_REGION": os.getenv("AWS_REGION", "us-east-1"),
        "FACEPP_API_KEY": os.getenv("FACEPP_API_KEY", ""),
        "FACEPP_API_SECRET": os.getenv("FACEPP_API_SECRET", ""),
    }

