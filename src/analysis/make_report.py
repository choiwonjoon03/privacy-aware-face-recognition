# src/analysis/make_report.py
import argparse
from pathlib import Path
import pandas as pd

def main():
    ap = argparse.ArgumentParser(description="Make text-only report from merged.csv (no images)")
    ap.add_argument("--in", dest="inp", required=True, help="Input merged.csv")
    ap.add_argument("--out", dest="outdir", default="results", help="Output directory (default: results)")
    ap.add_argument("--topk", type=int, default=10, help="Top/Bottom K (default: 10)")
    args = ap.parse_args()

    inp = Path(args.inp)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(inp)
    if "p_mean" not in df.columns:
        raise SystemExit("p_mean column not found; run merge_4models.py first.")

    df_sorted = df.sort_values("p_mean", ascending=False)

    # 1) Bucket summary → summary.md
    bucket_counts = df_sorted["bucket_mean"].value_counts(dropna=False).rename_axis("bucket").reset_index(name="count")
    total = int(bucket_counts["count"].sum()) if not bucket_counts.empty else 0

    lines = [
        "# Report Summary",
        "",
        f"- Input: `{inp}`",
        f"- Total rows: **{total}**",
        "",
        "## Bucket distribution"
    ]
    if total > 0:
        for _, row in bucket_counts.iterrows():
            b = str(row["bucket"]) if pd.notna(row["bucket"]) else "(blank)"
            c = int(row["count"])
            lines.append(f"- {b}: {c}")
    else:
        lines.append("- (no data)")

    (outdir / "summary.md").write_text("\n".join(lines), encoding="utf-8")

    # 2) Top/Bottom K → CSV
    topk = max(1, int(args.topk))
    top_cols = ["filename", "p_mean", "bucket_mean"]
    df_sorted.head(topk)[top_cols].to_csv(outdir / "topk.csv", index=False, encoding="utf-8")
    df_sorted.tail(topk)[top_cols].to_csv(outdir / "bottomk.csv", index=False, encoding="utf-8")

    print(f"[OK] summary: {outdir/'summary.md'}")
    print(f"[OK] top:     {outdir/'topk.csv'}")
    print(f"[OK] bottom:  {outdir/'bottomk.csv'}")

if __name__ == "__main__":
    main()
