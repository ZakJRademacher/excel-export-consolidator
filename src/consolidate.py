"""Independent standard-library reference implementation for the Excel queries."""

import csv
import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ["RowID", "OrderID", "OrderDate", "ShipDate", "Category", "Region", "ProductID", "Sales"]
CATEGORIES = ["Furniture", "Office Supplies", "Technology"]
REGIONS = ["Central", "East", "South", "West"]


def read_csv(path, delimiter=","):
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f, delimiter=delimiter, strict=True))


def header_key(s):
    return re.sub(r"[ _-]", "", s.strip().lower())


def parse_amount(s):
    if not re.fullmatch(r"(?:\d+|\d{1,3}(?:,\d{3})+)(?:\.\d{1,4})?", s):
        raise ValueError("Invalid sales")
    return Decimal(s.replace(",", ""))


def normalize(raw, profile):
    result = {k: str(raw[k]).strip() for k in FIELDS}
    issues = []
    for key in ["RowID", "OrderID", "ProductID"]:
        if not result[key]:
            issues.append("Missing " + key)
    for key, allowed in [("Category", CATEGORIES), ("Region", REGIONS)]:
        matches = [x for x in allowed if x.lower() == result[key].lower()]
        if matches:
            result[key] = matches[0]
        else:
            issues.append("Invalid " + key)
    fmt = {"yyyy-MM-dd": "%Y-%m-%d", "MM/dd/yyyy": "%m/%d/%Y", "dd/MM/yyyy": "%d/%m/%Y"}[profile["DateFormat"]]
    for key in ["OrderDate", "ShipDate"]:
        try:
            parsed = datetime.strptime(result[key], fmt)
            if parsed.strftime(fmt) != result[key]:
                raise ValueError("Noncanonical date")
            result[key] = parsed.strftime("%Y-%m-%d")
        except ValueError:
            issues.append("Invalid " + key)
            result[key] = None
    if result["OrderDate"] and result["ShipDate"] and result["ShipDate"] < result["OrderDate"]:
        issues.append("ShipDate precedes OrderDate")
    try:
        result["Sales"] = str(parse_amount(result["Sales"]))
    except (ValueError, InvalidOperation):
        issues.append("Invalid Sales")
        result["Sales"] = None
    return result, issues


def consolidate(folder, config=ROOT / "config"):
    maps = read_csv(config / "column-mapping.csv")
    aliases = {header_key(a): c for a, c in maps[1:]}
    fmt_rows = read_csv(config / "file-formats.csv")
    formats = [dict(zip(fmt_rows[0], r)) for r in fmt_rows[1:]]
    records, files = [], []
    for path in sorted(Path(folder).iterdir()):
        if not path.is_file() or path.suffix.lower() != ".csv" or path.name.startswith((".", "~")):
            continue
        log = {"SourceFile": path.name, "InputRows": 0, "CleanRows": 0, "ReviewRows": 0, "RepeatedRows": 0, "FileIssues": 0,
               "SHA256": hashlib.sha256(path.read_bytes()).hexdigest()}
        files.append(log)
        try:
            profiles = [p for p in formats if path.name.lower().startswith(p["Prefix"].lower())]
            if len(profiles) != 1:
                raise ValueError("File needs exactly one matching format profile")
            p = profiles[0]
            rows = read_csv(path, p["Delimiter"])
            if not rows:
                raise ValueError("File is empty; include a header row")
            headers = [aliases.get(header_key(h)) for h in rows[0]]
            if len(headers) != 8 or None in headers or set(headers) != set(FIELDS):
                raise ValueError("Missing, extra or duplicate mapped columns")
            log["InputRows"] = len(rows) - 1
            for index, row in enumerate(rows[1:], 2):
                if len(row) != len(headers):
                    raise ValueError("Inconsistent field count on logical CSV row " + str(index))
            for index, row in enumerate(rows[1:], 2):
                raw = dict(zip(headers, row))
                clean, issues = normalize(raw, p)
                records.append({**clean, "SourceFile": path.name, "SourceRow": index, "Issues": issues,
                                "RawRecord": json.dumps(raw, ensure_ascii=False, separators=(",", ":")), "RawOrderDate": raw["OrderDate"], "RawSales": raw["Sales"]})
        except (ValueError, UnicodeError, csv.Error) as error:
            log["FileIssues"] = 1
            log["InputRows"] = 0
            records.append({**dict.fromkeys(FIELDS), "SourceFile": path.name, "SourceRow": 0, "Issues": [str(error)],
                            "RawRecord": "", "RawOrderDate": "", "RawSales": "", "Status": "File issue"})
    groups = defaultdict(list)
    for row in records:
        if row.get("Status") == "File issue":
            continue
        groups[row["RowID"] or (row["SourceFile"], row["SourceRow"])].append(row)
    for rows in groups.values():
        valid_values = {tuple(str(r[k]) if k != "Sales" or r[k] is None else str(Decimal(r[k]).normalize()) for k in FIELDS) for r in rows}
        conflict = len(rows) > 1 and (len(valid_values) > 1 or any(r["Issues"] for r in rows))
        for index, row in enumerate(rows):
            if conflict:
                row["Issues"].append("Conflicting RowID; review every copy")
            row["Status"] = "Needs review" if row["Issues"] else ("Clean" if index == 0 else "Repeat skipped")
            if row["Status"] == "Repeat skipped":
                row["Issues"] = ["Identical normalized RowID; retained first source file/row"]
    by_file = {f["SourceFile"]: f for f in files}
    for row in records:
        target = {"Clean": "CleanRows", "Needs review": "ReviewRows", "Repeat skipped": "RepeatedRows"}.get(row["Status"])
        if target:
            by_file[row["SourceFile"]][target] += 1
        row["Reason"] = "; ".join(row.pop("Issues"))
    return {"rows": records, "files": files, "metrics": {
        "files": len(files), "input_rows": sum(f["InputRows"] for f in files), "clean_rows": sum(f["CleanRows"] for f in files),
        "review_rows": sum(f["ReviewRows"] for f in files), "repeated_rows": sum(f["RepeatedRows"] for f in files),
        "file_issues": sum(f["FileIssues"] for f in files), "clean_sales": str(sum((Decimal(r["Sales"]) for r in records if r["Status"] == "Clean"), Decimal(0)))}}


if __name__ == "__main__":
    result = consolidate(ROOT / "data/incoming")
    (ROOT / "evidence/reference-results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["metrics"]))
