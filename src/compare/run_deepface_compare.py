# src/compare/run_deepface_compare.py
import argparse
from pathlib import Path
import numpy as np

from deepface import DeepFace

from src.utils.filename_cleaner import clean_filename
from src.utils.bucketer import bucket_from_p
from src.utils.io_helpers import save_csv

# ---------- helpers ----------
def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    a = a / (np.linalg.norm(a) + 1e-8)
    b = b / (np.linalg.norm(b) + 1e-8)
    return float((a * b).sum())

def cosine_to_percent(cos: float) -> float:
    # map [-1,1] -> [0,100]
    return (cos + 1.0) * 50.0

def embed(path: str) -> np.ndarray:
    # Using ArcFace to diversify from FaceNet script
    rep = DeepFace.represent(img_path=path, model_name="ArcFace", detector_backend="skip")
    # DeepFace.represent returns list[dict] in recent versions; handle both
    if isinstance(rep, list):
        rep = rep[0]
    emb = np.array(rep["embedding"], dtype=np.float32)
    return emb

# ---------- main ----------
def main():
    ap = argparse.ArgumentParser(description="DeepFace (ArcFace) similarity: source vs folder")
    ap.add_argument("--folder", required=True, help="Folder containing variant images")
    ap.add_argument("--source", required=True, help="Source image filename (inside folder)")
    ap.add_argument("--outfile", default="deepface_results.csv", help="Output CSV path")
    args = ap.parse_args()

    folder = Path(args.folder)
    src_path = folder / args.source
    if not src_path.exists():
        raise FileNotFoundError(f"Source not found: {src_path}")

    src_emb = embed(str(src_path))

    exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    rows = []
    for p in sorted(folder.iterdir()):
        if not p.is_file() or p.name == args.source:
            continue
        if p.suffix.lower() not in exts:
            continue
        try:
            emb = embed(str(p))
            cos = cosine_similarity(src_emb, emb)
            perc = cosine_to_percent(cos)
            rows.append({
                "filename": clean_filename(p.name),
                "cosine": round(cos, 3),
                "p": round(perc, 1),
                "bucket": bucket_from_p(perc),
            })
        except Exception as e:
            print(f"[WARN] failed: {p.name} ({e})")

    rows.sort(key=lambda r: r["p"], reverse=True)
    save_csv(rows, ["filename", "cosine", "p", "bucket"], args.outfile)
    print(f"[OK] saved: {args.outfile} ({len(rows)} rows)")

if __name__ == "__main__":
    main()
