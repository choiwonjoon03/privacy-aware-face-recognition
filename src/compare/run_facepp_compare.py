# src/compare/run_facepp_compare.py
import argparse
from pathlib import Path
import requests

from src.utils.filename_cleaner import clean_filename
from src.utils.bucketer import bucket_from_p
from src.utils.io_helpers import save_csv, load_env

EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

API_URL = "https://api-us.faceplusplus.com/facepp/v3/compare"  # use US endpoint; change if needed

def main():
    ap = argparse.ArgumentParser(description="Face++ compare: source vs folder")
    ap.add_argument("--folder", required=True, help="Folder containing variant images")
    ap.add_argument("--source", required=True, help="Source image filename (inside folder)")
    ap.add_argument("--outfile", default="results/csv/facepp_results.csv", help="Output CSV path")
    args = ap.parse_args()

    env = load_env()
    key = env["FACEPP_API_KEY"]
    secret = env["FACEPP_API_SECRET"]
    if not key or not secret:
        raise SystemExit("FACEPP_API_KEY / FACEPP_API_SECRET not set in .env")

    folder = Path(args.folder)
    src_path = folder / args.source
    if not src_path.exists():
        raise FileNotFoundError(f"Source not found: {src_path}")

    rows = []
    for p in sorted(folder.iterdir()):
        if not p.is_file() or p.name == args.source:
            continue
        if p.suffix.lower() not in EXTS:
            continue

        try:
            files = {
                "image_file1": open(src_path, "rb"),
                "image_file2": open(p, "rb"),
            }
            data = {"api_key": key, "api_secret": secret}
            r = requests.post(API_URL, data=data, files=files, timeout=30)
            try:
                files["image_file1"].close()
                files["image_file2"].close()
            except Exception:
                pass

            r.raise_for_status()
            js = r.json()
            # Face++ returns "confidence" (0-100). Use as p.
            conf = float(js.get("confidence", 0.0))

            rows.append({
                "filename": clean_filename(p.name),
                "cosine": "",              # not applicable for Face++
                "p": round(conf, 1),
                "bucket": bucket_from_p(conf),
            })
        except Exception as e:
            print(f"[WARN] failed: {p.name} ({e})")

    rows.sort(key=lambda r: r["p"], reverse=True)
    save_csv(rows, ["filename", "cosine", "p", "bucket"], args.outfile)
    print(f"[OK] saved: {args.outfile} ({len(rows)} rows)")

if __name__ == "__main__":
    main()
