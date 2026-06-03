import gzip
import json
from pathlib import Path

RAW_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/uncompressed")

OUTPUT_DIR.mkdir(exist_ok=True)

FIELDS = [
    "version",
    "account_id",
    "interface_id",
    "srcaddr",
    "dstaddr",
    "srcport",
    "dstport",
    "protocol",
    "packets",
    "bytes",
    "start",
    "end",
    "action",
    "log_status"
]

for gz_file in RAW_DIR.glob("*.gz"):

    output_file = OUTPUT_DIR / f"{gz_file.stem}.jsonl"

    print(f"Processing: {gz_file.name}")

    with gzip.open(gz_file, "rt") as f_in, open(output_file, "w") as f_out:

        for line in f_in:

            parts = line.strip().split()

            if len(parts) != len(FIELDS):
                continue

            record = dict(zip(FIELDS, parts))

            json.dump(record, f_out)
            f_out.write("\n")

    print(f"Saved: {output_file.name}")

print("Done.")