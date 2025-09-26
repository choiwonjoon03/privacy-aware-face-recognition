# src/compare/run_aws_compare.py
import argparse
from pathlib import Path
import boto3

from src.utils.filename_cleaner import clean_filename
from src.utils.bucketer import bucket_from_p
from src.utils.io_helpers import save_csv, load_env

EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

def read_bytes(p: Path) -> bytes:
    return p.read_bytes()

def main():
    ap = argparse.ArgumentParser(description="AWS Rekognition CompareFaces: source vs folder")
    ap.add_argument("--folder", required=True, help="Folder containing variant images")
    ap.add_argument("--source", required=True, help="Source image filename (inside folder)")
    ap.add_argument("--outfile", default="results/csv/aws_results.csv", help="Output CSV path")
    ap.add_argument("--similarity-threshold", type=float, default=0.0, help="Min Similarity filter (0-100)")
    args = ap.parse_args()

    env = load_env()
    client = boto3.client(
        "rekognition",
        region_name=env["AWS_REGION"] or "us-east-1",
        aws_access_key_id=env["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=env["AWS_SECRET_ACCESS_KEY"],
    )

    folder = Path(args.folder)
    src_path = folder / args.source
    if not src_path.exists():
        raise FileNotFoundError(f"Source not found: {src_path}")

    src_bytes = read_bytes(src_path)

    rows = []
    for p in sorted(folder.iterdir()):
        if not p.is_file() or p.name == args.source:
            continue
        if p.suffix.lower() not in EXTS:
            continue

        try:
            tgt_bytes = read_bytes(p)
            resp = client.compare_faces(
                SourceImage={"Bytes": src_bytes},
                TargetImage={"Bytes": tgt_bytes},
                SimilarityThreshold=args.similarity-threshold if hasattr(args, "similarity-threshold") else 0.0  # guard
            )
            # Use the max similarity among matches; if none, set 0
            matches = resp.get("FaceMatches", [])
            p_val = max((m.get("Similarity", 0.0) for m in matches), default=0.0)

            rows.append({
                "filename": clean_filename(p.name),
                "cosine": "",               # not applicable for AWS
                "p": round(float(p_val), 1),
                "bucket": bucket_from_p(float(p_val)),
            })
        except Exception as e:
            print(f"[WARN] failed: {p.name} ({e})")

    rows.sort(key=lambda r: r["p"], reverse=True)
    save_csv(rows, ["filename", "cosine", "p", "bucket"], args.outfile)
    print(f"[OK] saved: {args.outfile} ({len(rows)} rows)")

if __name__ == "__main__":
    main()
