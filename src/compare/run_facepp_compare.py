# src/compare/run_facepp_compare.py
import argparse
from pathlib import Path
import time
import requests

from src.utils.filename_cleaner import clean_filename
from src.utils.bucketer import bucket_from_p
from src.utils.io_helpers import save_csv, load_env

EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
API_URL = "https://api-us.faceplusplus.com/facepp/v3/compare"  # change region if needed

def post_with_retry(files, data, timeout=30, max_retries=3, base_delay=1.5):
    """
    Simple exponential backoff: 1.5s, 3.0s, 4.5s ...
    Retries on network errors or 5xx. 4xx는 즉시 실패.
    """
    attempt = 0
    while True:
        attempt += 1
        try:
            r = requests.post(API_URL, data=data, files=files, timeout=timeout)
            if 500 <= r.status_code < 600:
                raise requests.HTTPError(f"Server error {r.status_code}", response=r)
            r.raise_for_status()
            return r
        except requests.HTTPError as e:
            # 4xx면 재시도 의미 없음
            if 400 <= e.response.status_code < 500 and e.response.status_code != 429:
                raise
            if attempt >= max_retries:
                raise
        except (requests.Timeout, requests.ConnectionError):
            if attempt >= max_retries:
                raise
        # backoff
        time.sleep(base_delay * attempt)

def main():
    ap = argparse.ArgumentParser(description="Face++ compare: source vs folder")
    ap.add_argument("--folder", required=True, help="Folder containing variant images")
    ap.add_argument("--source", required=True, help="Source image filename (inside folder)")
    ap.add_argument("--outfile", default="results/csv/facepp_results.csv", help="Output CSV path")
    ap.add_argument("--timeout", type=float, default=30.0, help="HTTP timeout seconds")
    ap.add_argument("--retries", type=int, default=3, help="Max retries on transient errors")
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

        f1 = f2 = None
        try:
            f1 = open(src_path, "rb")
            f2 = open(p, "rb")
            files = {"image_file1": f1, "image_file2": f2}
            data = {"api_key": key, "api_secret": secret}

            r = post_with_retry(files, data, timeout=args.timeout, max_retries=args.retries)
            js = r.json()
            conf = float(js.get("confidence", 0.0))

            rows.append({
                "filename": clean_filename(p.name),
                "cosine": "",              # not applicable for Face++
                "p": round(conf, 1),
                "bucket": bucket_from_p(conf),
            })
        except Exception as e:
            print(f"[WARN] failed: {p.name} ({e})")
        finally:
            try:
                if f1: f1.close()
                if f2: f2.close()
            except Exception:
                pass

    rows.sort(key=lambda r: r["p"], reverse=True)
    save_csv(rows, ["filename", "cosine", "p", "bucket"], args.outfile)
    print(f"[OK] saved: {args.outfile} ({len(rows)} rows)")

if __name__ == "__main__":
    main()
