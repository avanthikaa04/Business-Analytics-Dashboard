"""Import the supplied Excel workbook into the local SQLite analytics database."""
import argparse
import sys
from pathlib import Path

import pandas as pd

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))
from app.database import get_connection, initialize_database  # noqa: E402

REQUIRED = [
    "BillNo", "Outlet_Name", "Order_Datetime", "Group", "Order_Type",
    "Item", "Price", "Quantity", "Settlement", "Brand"
]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default=str(BACKEND_DIR / "data" / "data.xlsx"))
    args = parser.parse_args()
    source = Path(args.file)
    if not source.exists():
        raise SystemExit(f"Dataset not found: {source}")

    print(f"Reading {source} ...")
    frame = pd.read_excel(source)
    missing = [column for column in REQUIRED if column not in frame.columns]
    if missing:
        raise SystemExit(f"Missing required columns: {', '.join(missing)}")

    frame = frame[REQUIRED].copy()
    frame["Order_Datetime"] = pd.to_datetime(frame["Order_Datetime"], errors="coerce", dayfirst=True)
    frame["Price"] = pd.to_numeric(frame["Price"], errors="coerce")
    frame["Quantity"] = pd.to_numeric(frame["Quantity"], errors="coerce")
    frame = frame.dropna(subset=["BillNo", "Order_Datetime", "Price", "Quantity"])
    for column in ["Outlet_Name", "Group", "Order_Type", "Item", "Settlement", "Brand"]:
        frame[column] = frame[column].fillna("Unknown").astype(str).str.strip()
    frame["BillNo"] = frame["BillNo"].astype(str)
    frame["Order_Datetime"] = frame["Order_Datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")

    rows = list(frame.itertuples(index=False, name=None))
    initialize_database()
    with get_connection() as conn:
        conn.execute("DELETE FROM order_lines")
        conn.executemany("""
            INSERT INTO order_lines
            (bill_no, outlet_name, order_datetime, category, order_type,
             item, price, quantity, settlement, brand)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, rows)
        conn.commit()

    print(f"Imported {len(rows):,} line items.")
    print(f"Unique orders: {frame['BillNo'].nunique():,}")
    print(f"Revenue: {float((frame['Price'] * frame['Quantity']).sum()):,.2f}")

if __name__ == "__main__":
    main()
