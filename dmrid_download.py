#!/usr/bin/env python3
"""
Download and reformat radioid.net user.csv for the Radtel RT-4D address book.

Source: https://radioid.net/static/user.csv
Reference: https://www.w1aex.com/dmrid/dmrid.html
"""

import argparse
import csv
import os
import sys
import tempfile
import requests

SOURCE_URL = "https://radioid.net/static/user.csv"

EXPECTED_COLUMNS = ["RADIO_ID", "CALLSIGN", "FIRST_NAME", "LAST_NAME", "CITY", "STATE", "COUNTRY"]

COUNTRY_ABBREVS = {
    "United States":           "USA",
    "Netherlands":             "NLD",
    "Czech Republic":          "CZE",
    "United Kingdom":          "GBR",
    "Germany":                 "DEU",
    "Korea Republic of":       "ROK",
    "Australia":               "AUS",
    "Philippines":             "PHL",
    "New Zealand":             "NZL",
    "Argentina Republic":      "ARG",
    "Slovenia":                "SVN",
    "Bosnia and Hercegovina":  "BIH",
    "Greece":                  "GRC",
    "Belgium":                 "BEL",
    "France":                  "FRA",
    "Denmark":                 "DNK",
    "Portugal":                "PRT",
    "Türkiye":                 "TUR",
}

RT4D_MAX_KB = 12_289


def download(url: str) -> str:
    """Stream-download url to a temp file, return its path."""
    print(f"Downloading {url} ...", flush=True)
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        tmp = tempfile.NamedTemporaryFile(
            mode="wb", suffix=".csv", delete=False, prefix="radioid_"
        )
        downloaded = 0
        for chunk in r.iter_content(chunk_size=1 << 20):  # 1 MB chunks
            tmp.write(chunk)
            downloaded += len(chunk)
            if total:
                pct = downloaded / total * 100
                print(f"\r  {downloaded // 1024:,} KB / {total // 1024:,} KB  ({pct:.1f}%)", end="", flush=True)
        tmp.close()
    print(f"\r  Downloaded {downloaded // 1024:,} KB{' ' * 20}")
    return tmp.name


def transform(src_path: str, dst_path: str) -> int:
    """Read src CSV, apply all transformations, write to dst. Returns row count."""
    print("Transforming ...", flush=True)
    rows_written = 0

    with open(src_path, newline="", encoding="utf-8", errors="replace") as fin, \
         open(dst_path, "w", newline="", encoding="utf-8") as fout:

        reader = csv.DictReader(fin)

        # Validate columns
        if reader.fieldnames != EXPECTED_COLUMNS:
            sys.exit(
                f"ERROR: unexpected columns.\n"
                f"  Expected: {EXPECTED_COLUMNS}\n"
                f"  Got:      {list(reader.fieldnames)}"
            )

        out_fields = ["RADIO_ID", "CALLSIGN", "FIRST_NAME", "LAST_NAME", "STATE", "COUNTRY", ""]
        writer = csv.DictWriter(fout, fieldnames=out_fields, extrasaction="ignore", lineterminator="\r\n")
        writer.writeheader()

        for row in reader:
            # Merge and truncate name
            merged = (row["FIRST_NAME"] + " " + row["LAST_NAME"]).strip()[:18]

            # Abbreviate country
            country = COUNTRY_ABBREVS.get(row["COUNTRY"], row["COUNTRY"])

            writer.writerow({
                "RADIO_ID":   row["RADIO_ID"],
                "CALLSIGN":   row["CALLSIGN"],
                "FIRST_NAME": merged,
                "LAST_NAME":  "",
                "STATE":      row["STATE"][:14],
                "COUNTRY":    country,
                "":           "",
            })
            rows_written += 1

            if rows_written % 50_000 == 0:
                print(f"  {rows_written:,} rows processed ...", flush=True)

    return rows_written


def main():
    parser = argparse.ArgumentParser(description="Download and reformat radioid.net user.csv for the RT-4D.")
    parser.add_argument("--output", default="user_rt4d.csv", help="Output file path (default: user_rt4d.csv)")
    parser.add_argument("--keep-download", action="store_true", help="Keep the raw downloaded file instead of deleting it")
    args = parser.parse_args()

    tmp_path = download(SOURCE_URL)

    try:
        rows = transform(tmp_path, args.output)
    finally:
        if args.keep_download:
            print(f"Raw download kept at: {tmp_path}")
        else:
            os.unlink(tmp_path)

    size_kb = os.path.getsize(args.output) // 1024
    print(f"\nDone: {rows:,} rows → {args.output}")
    print(f"File size: {size_kb:,} KB  (RT-4D limit: {RT4D_MAX_KB:,} KB)")
    if size_kb > RT4D_MAX_KB:
        print(f"WARNING: file exceeds the RT-4D address book limit of {RT4D_MAX_KB:,} KB")


if __name__ == "__main__":
    main()
