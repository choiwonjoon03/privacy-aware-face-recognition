# src/compare/run_aws_compare.py
import argparse
import time
from pathlib import Path

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, EndpointConnectionError, ConnectionClosedError, ReadTimeoutError

from src.utils.filename_cleaner import clean_filename
from src.utils.bucketer import bucket_from_p
from src.utils.io_helpers import save_csv, load_env

EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

RETRY_ERRORS = {
    "Throttling",
    "ThrottlingException",
    "ProvisionedThroughputExceededException",
    "InternalServerError",
    "ServiceUnavailable",
    "RequestTimeout",
}

def compare_with_retry(client, src_bytes: bytes, tgt_bytes: bytes, threshold: float,
                       max_retries: int = 3, base_delay: float = 1.5, timeout_note: str = "") -> dict:
    """
    Exponential backoff: 1.5s, 3.0s, 4.5s ...
    Retries on common transient AWS errors and network timeouts.
    """
    attempt = 0
    while True:
        attempt += 1
        try:
            return client.compare_faces(
                SourceImage={"Bytes": src_bytes},
                TargetImage={"Bytes": tgt_bytes},
                SimilarityThreshold=threshold
            )
        except (EndpointConnectionError, ConnectionClosedError, ReadTimeoutError) as e:
            if attempt >= max_retries:
                raise
        except ClientError as e:
            code = e.response.get("Error", {}).get("Code", "")
            if code in RETRY_ERRORS and attempt < max_retries:
                pass  # retry
            else:
                # non-retryable (e.g., InvalidImageFormatException) → re-raise
                raise
        time.sleep(base_delay * attempt)

def main():
    ap = argparse.ArgumentParser(description="AWS Rekognition CompareFaces: source vs folder (with retry)")
    ap.add_argument("--folder", required=True, help="Folder containing variant images")
    ap.add_argument("--source", required=True, help="Source image filename (inside folder)")
    ap.add_argument("--outfile", default="results/csv/aws_results.csv", help="Output CSV path")
    ap.add_argument("--similarity-threshold", type=float, default=0.0, help="Min Similarity filter (0-100)")
    ap.add_argument("--connect-timeout", type=float, default=10.0, help="Connect timeout seconds")
    ap.add_argument("--read-timeout", type=float, default=60.0, help="Read timeout seconds")
    ap.add_argument("--retries", type=int, default=3, help="Max retries on transient errors")
    args = ap.parse_args()

    env = load_env()
    region = env["AWS_REGION"] or "us-east-1"
    key = env["AWS_ACCESS_KEY_ID"]
    secret = env["AWS_SECRET_ACCESS_KEY"]
    if not key or not secret:
        raise SystemExit("AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY not set in .env")

    cfg = Config(
        region_name=region,
        retries={"max_attempts": 0},  # we handle retries ourselves
        connect_timeout=float(args.connect_timeout),
        read_timeout=float(args.read_timeout),
    )
    client = boto3.client(
        "rekognition",
        aws_access_key_id=key,
        aws_secret_access_key=secret,
        config=cfg,
    )

    folder = Path(args.folder)
    src_path = folder / args.source
    if not src_path.exists():
        raise FileNotFoundError(f"Source not found: {src_path}")

    src_bytes = src_path.read_bytes()

    rows = []
    for p in sorted(folder.iterdir()):
        if not p.is_file() or p.name == args.source:
            continue
        if p.suffix.lower() not in EXTS:
            continue

        try:
            tgt_bytes = p.read_bytes()
            resp = compare_with_retry(
                client,
                src_bytes,
                tgt_bytes,
                threshold=float(args.similarity_threshold),
                max_retries=int(args.retries),
            )
            matches = resp.get("FaceMatches", [])
            p_val = max((m.get("Similarity", 0.0) for m in matches), default=0.0)

            rows.append({
                "filename": clean_filename(p.name),
                "cosine": "",  # not applicable for AWS
                "p": round(float(p_val), 1),
                "bucket": bucket_from_p(float(p_val)),
            })
        except ClientError as e:
            code = e.response.get("Error", {}).get("Code", "Unknown")
            print(f"[WARN] {p.name}: AWS ClientError {code} — skipped")
        except Exception as e:
            print(f"[WARN] {p.name}: {e} — skipped")

    rows.sort(key=lambda r: r["p"], reverse=True)
    save_csv(rows, ["filename", "cosine", "p", "bucket"], args.outfile)
    print(f"[OK] saved: {args.outfile} ({len(rows)} rows)")

if __name__ == "__main__":
    main()
