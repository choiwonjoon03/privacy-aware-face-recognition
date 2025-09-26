import argparse
import os
import csv
from pathlib import Path

import torch
import numpy as np
from PIL import Image
from torchvision import transforms
from facenet_pytorch import InceptionResnetV1

from src.utils.filename_cleaner import clean_filename
from src.utils.bucketer import bucket_from_p

# ---------- helpers ----------
def load_image(path: str, size: int = 160) -> torch.Tensor:
    """Load an image file and convert to normalized CHW tensor for FaceNet."""
    img = Image.open(path).convert("RGB")
    t = transforms.Compose([
        transforms.Resize((size, size)),
        transforms.ToTensor(),  # [0,1]
        transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),  # [-1,1]
    ])
    return t(img)

def cosine_similarity(a: torch.Tensor, b: torch.Tensor) -> float:
    a = a / (a.norm(p=2) + 1e-8)
    b = b / (b.norm(p=2) + 1e-8)
    return float((a * b).sum().item())

def cosine_to_percent(cos: float) -> float:
    # Map [-1,1] -> [0,100]; matches examples like cos=0.725 -> 86.25%
    return (cos + 1.0) * 50.0

# ---------- main ----------
def main():
    parser = argparse.ArgumentParser(description="FaceNet similarity compare (source vs folder).")
    parser.add_argument("--folder", required=True, help="Folder containing variant images.")
    parser.add_argument("--source", required=True, help="Source image filename (inside folder).")
    parser.add_argument("--outfile", default="facenet_results.csv", help="Output CSV path.")
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = InceptionResnetV1(pretrained="vggface2").eval().to(device)

    folder = Path(args.folder)
    src_path = folder / args.source
    if not src_path.exists():
        raise FileNotFoundError(f"Source not found: {src_path}")

    # embed source
    with torch.no_grad():
        src_img = load_image(str(src_path)).unsqueeze(0).to(device)  # 1x3x160x160
        src_emb = model(src_img).squeeze(0)  # 512-dim

    # iterate targets
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    rows = []
    for p in sorted(folder.iterdir()):
        if not p.is_file() or p.name == args.source:
            continue
        if p.suffix.lower() not in exts:
            continue

        try:
            with torch.no_grad():
                img = load_image(str(p)).unsqueeze(0).to(device)
                emb = model(img).squeeze(0)
            cos = cosine_similarity(src_emb, emb)
            perc = cosine_to_percent(cos)
            rows.append({
                "filename": clean_filename(p.name),
                "cosine": round(cos, 3),
                "p": round(perc, 1),
                "bucket": bucket_from_p(perc),
            })
        except Exception as e:
            # skip problematic files but keep running
            print(f"[WARN] failed: {p.name} ({e})")

    # sort by percent desc
    rows.sort(key=lambda r: r["p"], reverse=True)

    # ensure output dir exists
    out_path = Path(args.outfile)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # write csv
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["filename", "cosine", "p", "bucket"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"[OK] saved: {out_path} ({len(rows)} rows)")

if __name__ == "__main__":
    main()
