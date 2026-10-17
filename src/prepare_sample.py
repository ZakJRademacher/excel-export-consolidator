"""Create disclosed test exports from an attributed public sales sample."""

import csv
import hashlib
import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/source/sales_2018-12.csv"
FIELDS = ["RowID", "OrderID", "OrderDate", "ShipDate", "Category", "Region", "ProductID", "Sales"]
FORMATS = [
    ["batch_a_", ",", "yyyy-MM-dd", "en-US"],
    ["batch_b_", ",", "MM/dd/yyyy", "en-US"],
    ["batch_c_", ";", "dd/MM/yyyy", "en-US"],
    ["batch_d_", ",", "yyyy-MM-dd", "en-US"],
    ["batch_e_", ",", "yyyy-MM-dd", "en-US"],
]
HEADERS = [
    FIELDS,
    ["Line ID", "Order Ref", "Placed On", "Shipped On", "Product Group", "Sales Region", "SKU", "Sales Amount"],
    ["record_id", "order", "order_dt", "ship_dt", "dept", "territory", "item_code", "amount"],
    [" ROW ID ", "ORDER ID", "ORDER DATE", "SHIP DATE", "CATEGORY", "REGION", "PRODUCT ID", "SALES"],
    ["RowID", "OrderID", "OrderDate", "ShipDate", "Category", "Region", "ProductID", "Sales"],
]


def write_csv(path, headers, rows, delimiter=","):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=delimiter)
        w.writerow(headers)
        w.writerows(rows)


def encode(row, profile):
    vals = [row[k] for k in FIELDS]
    fmt = {"yyyy-MM-dd": "%Y-%m-%d", "MM/dd/yyyy": "%m/%d/%Y", "dd/MM/yyyy": "%d/%m/%Y"}[FORMATS[profile][2]]
    for index in [2, 3]:
        vals[index] = datetime.strptime(vals[index], "%d/%m/%Y").strftime(fmt)
    if Decimal(vals[7]) >= 1000:
        whole, _, frac = vals[7].partition(".")
        vals[7] = f"{int(whole):,}" + ("." + frac if frac else "")
    return vals


def main():
    with SOURCE.open(encoding="utf-8-sig", newline="") as f:
        original = [{k.replace(" ", ""): v for k, v in r.items()} for r in csv.DictReader(f)]
    sample = original[:300]
    batches = [[encode(r, i) for r in sample[i * 60:(i + 1) * 60]] for i in range(5)]
    for i, rows in enumerate(batches):
        for j, r in enumerate(rows):
            if j % 7 == 0:
                r[0], r[1], r[6] = ["  " + r[k] + " " for k in [0, 1, 6]]
            if j % 4 == 0:
                r[4], r[5] = r[4].lower(), r[5].upper()
    changes = []
    edits = [(20, 0, "", "Missing RowID"), (21, 7, "N/A", "Invalid sales"),
             (22, 2, "2018-02-30", "Invalid date"), (23, 4, "Office supp", "Unknown category"),
             (24, 5, "", "Missing region"), (25, 3, "2014-01-01", "Ship before order"),
             (26, 1, "", "Missing OrderID"), (27, 6, "", "Missing ProductID")]
    for index, field, value, reason in edits:
        batches[0][index][field] = value
        changes.append({"source_row_id": sample[index]["RowID"], "change": reason})
    for index in range(8):
        batches[4].append(encode(sample[index], 4))
        changes.append({"source_row_id": sample[index]["RowID"], "change": "Added exact repeat to batch e"})
    conflict = dict(sample[10])
    conflict["Sales"] = str(Decimal(conflict["Sales"]) + Decimal("10"))
    batches[4].append(encode(conflict, 4))
    changes.append({"source_row_id": sample[10]["RowID"], "change": "Added conflicting amount; both copies must be reviewed"})
    for i, rows in enumerate(batches):
        write_csv(ROOT / f"data/incoming/{FORMATS[i][0]}2018-12.csv", HEADERS[i], rows, FORMATS[i][1])
    aliases = list(zip(FIELDS, FIELDS))
    for headers in HEADERS[1:]:
        aliases += list(zip(headers, FIELDS))
    seen = set()
    unique = []
    for alias, canonical in aliases:
        key = "".join(c for c in alias.lower() if c not in " _-")
        if key not in seen:
            seen.add(key)
            unique.append([alias, canonical])
    write_csv(ROOT / "config/column-mapping.csv", ["Alias", "Canonical"], unique)
    write_csv(ROOT / "config/file-formats.csv", ["Prefix", "Delimiter", "DateFormat", "Culture"], FORMATS)
    excluded = {10, *range(20, 28)}
    golden = {"files": 5, "input_rows": 309, "clean_rows": 291, "review_rows": 10, "repeated_rows": 8,
              "file_issues": 0, "clean_sales": str(sum((Decimal(r["Sales"]) for i, r in enumerate(sample) if i not in excluded), Decimal(0))),
              "clean_ids": [r["RowID"] for i, r in enumerate(sample) if i not in excluded]}
    (ROOT / "evidence/expected-results.json").write_text(json.dumps(golden, indent=2) + "\n")
    provenance = {"source": "https://www.kaggle.com/datasets/rohitsahoo/sales-forecasting", "source_partition": SOURCE.name,
                  "partition_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(), "sample": "First 300 data rows, original order",
                  "changes": changes, "note": "Controlled export variants and seeded defects, not observed business errors or client results."}
    (ROOT / "evidence/sample-provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    # One genuine additional source record, reserved for an add-file refresh demonstration.
    write_csv(ROOT / "evidence/batch_a_next.csv", HEADERS[0], [encode(original[300], 0)])
    print(json.dumps({k: v for k, v in golden.items() if k != "clean_ids"}))


if __name__ == "__main__":
    main()
