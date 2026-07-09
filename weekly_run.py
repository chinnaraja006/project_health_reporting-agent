import glob
import os
from agent import run, print_report
from datetime import datetime
import json

DATA_DIR = "data"
OUT_DIR = "outputs"


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    date_tag = datetime.now().strftime("%Y%m%d")
    files = glob.glob(os.path.join(DATA_DIR, "*.xlsx"))
    if not files:
        print(f"No .xlsx files found in {DATA_DIR}/")
        return
    for path in files:
        print(f"\n=== Running: {path} ===")
        result = run(path)
        stem = os.path.splitext(os.path.basename(path))[0]
        out_path = os.path.join(OUT_DIR, f"{stem}_{date_tag}.json")
        with open(out_path, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print_report(result)
        print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
