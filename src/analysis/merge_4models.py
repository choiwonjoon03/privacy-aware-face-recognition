# src/analysis/merge_4models.py
import argparse
import pandas as pd
from pathlib import Path

from src.utils.bucketer import bucket_from_p

def read_optional(path: str, model: str) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        return pd.DataFrame(columns=["filename", f"p_{model}"])
    df = pd.read_csv(p)
    # expect columns: filename, cosine, p, bucket
    out = df[["filename", "p"]].copy()
    out.rename(columns={"p": f"p_{model}"}, inplace=True)
    return out

def main():
    ap = argparse.ArgumentParser(description="Merge CSVs from up to 4 models by filename")
    ap.add_argument("--aws", default="", help="aws_results.csv")
    ap.add_argument("--facepp", default="", help="facepp_results.csv")
    ap.add_argument("--facenet", default="", help="facenet_results.csv")
    ap.add_argument("--deepface", default="", help="deepface_results.csv")
    ap.add_argument("--out", default="results/csv/merged.csv", help="output CSV")
    args = ap.parse_args()

    dfs = []
    if args.aws:     dfs.append(read_optional(args.aws, "aws"))
    if args.facepp:  dfs.append(read_optional(args.facepp, "facepp"))
    if args.facenet: dfs.append(read_optional(args.facenet, "facenet"))
    if args.deepface:dfs.append(read_optional(args.deepface, "deepface"))

    if not dfs:
        raise SystemExit("No inputs provided.")

    from functools import reduce
    merged = reduce(lambda l, r: pd.merge(l, r, on="filename", how="outer"), dfs)

    # mean of available p_*
    p_cols = [c for c in merged.columns if c.startswith("p_")]
    merged["p_mean"] = merged[p_cols].mean(axis=1, skipna=True)

    # bucket by mean
    merged["bucket_mean"] = merged["p_mean"].apply(lambda v: bucket_from_p(float(v)) if pd.notna(v) else "")

    # sort by mean desc (NaN last)
    merged = merged.sort_values(by=["p_mean"], ascending=[False], na_position="last")

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(args.out, index=False, encoding="utf-8")
    print(f"[OK] saved: {args.out} (rows={len(merged)})")

if __name__ == "__main__":
    main()
