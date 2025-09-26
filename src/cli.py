# src/cli.py (patched)
import argparse
from pathlib import Path
import os
import subprocess
import sys

def has_env(keys):
    return all(os.getenv(k) for k in keys)

def run(cmd: list[str]):
    print(">", " ".join(cmd))
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[WARN] failed -> {e}")

def main():
    ap = argparse.ArgumentParser(description="Run selected engines over a folder (source vs variants).")
    ap.add_argument("--folder", required=True, help="Folder containing images (source + variants)")
    ap.add_argument("--source", required=True, help="Source image filename (inside folder)")
    ap.add_argument("--outdir", default="results/csv", help="Output directory for CSVs")
    ap.add_argument("--engines", default="facenet,deepface,aws,facepp",
                    help="Comma-separated engines: facenet,deepface,aws,facepp")
    args = ap.parse_args()

    folder = Path(args.folder)
    if not folder.exists():
        raise SystemExit(f"Folder not found: {folder}")

    source = args.source
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    engines = [e.strip().lower() for e in args.engines.split(",") if e.strip()]
    engines = [e for e in engines if e in {"facenet", "deepface", "aws", "facepp"}]
    if not engines:
        raise SystemExit("No valid engines specified.")

    # Facenet
    if "facenet" in engines:
        run([sys.executable, "src/compare/run_facenet_compare.py",
             "--folder", str(folder),
             "--source", source,
             "--outfile", str(outdir / "facenet_results.csv")])

    # DeepFace
    if "deepface" in engines:
        run([sys.executable, "src/compare/run_deepface_compare.py",
             "--folder", str(folder),
             "--source", source,
             "--outfile", str(outdir / "deepface_results.csv")])

    # AWS Rekognition
    if "aws" in engines:
        if has_env(["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]):
            run([sys.executable, "src/compare/run_aws_compare.py",
                 "--folder", str(folder),
                 "--source", source,
                 "--outfile", str(outdir / "aws_results.csv")])
        else:
            print("[INFO] Skipping AWS (missing AWS_* keys in .env)")

    # Face++
    if "facepp" in engines:
        if has_env(["FACEPP_API_KEY", "FACEPP_API_SECRET"]):
            run([sys.executable, "src/compare/run_facepp_compare.py",
                 "--folder", str(folder),
                 "--source", source,
                 "--outfile", str(outdir / "facepp_results.csv")])
        else:
            print("[INFO] Skipping Face++ (missing FACEPP_* keys in .env)")

    print("[OK] Done. Check CSVs in:", outdir)

if __name__ == "__main__":
    main()
