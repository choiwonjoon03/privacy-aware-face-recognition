import os
import re

UUID_LIKE = re.compile(r"[_-]?[a-f0-9]{8}[-_]?(?:[a-f0-9]{4}[-_]?){3}[a-f0-9]{12}", re.IGNORECASE)
HASH_LIKE = re.compile(r"[a-f0-9]{6,32}$", re.IGNORECASE)

def clean_filename(name: str) -> str:
    """
    Keep meaningful prefix + extension; strip trailing UUID/hash-like tails.
    Examples:
      'kpopdemonhunters_v5_600_ba41dfa2-6...jpg' -> 'kpopdemonhunters_v5_600.jpg'
      'semi_ghibili_123abc.png' -> 'semi_ghibili.png'
    """
    base = os.path.basename(name)
    root, ext = os.path.splitext(base)

    # remove common uuid/hash tails
    parts = re.split(r"[\s._-]+", root)
    cleaned = []
    for i, p in enumerate(parts):
        if UUID_LIKE.fullmatch(p) or HASH_LIKE.fullmatch(p):
            break
        cleaned.append(p)
    new_root = "_".join(cleaned) if cleaned else root
    return f"{new_root}{ext}"
