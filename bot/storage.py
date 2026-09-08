"""
Shared CSV read/write helpers.

Originally an empty stub (savedata.py). The scraper and the trader used to
each keep their own copy of the same "write CSV" / "backup CSV" logic;
this module is that logic pulled out into one place so both can share it.
"""
import csv

import pandas as pd


def write_csv(file_path, header, rows):
    """Write a header row followed by data rows, overwriting the file."""
    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def append_csv_row(file_path, row):
    """Append a single row to an existing CSV file."""
    with open(file_path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row)


def read_csv_rows(file_path):
    """Read a CSV file back into a list of rows."""
    with open(file_path, newline="") as f:
        return list(csv.reader(f))


def backup_csv(source_path, backup_path):
    """Write a backup copy of a CSV file next to the original."""
    df = pd.read_csv(source_path, sep="delimiter", header=None, engine="python")
    df.to_csv(backup_path)
