"""Build a portable project ZIP without local runtimes, drafts or lock files."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def project_files():
    files = [ROOT / n for n in ["README.md", "LICENSE", ".gitignore", "requirements-qa.txt"]]
    for folder in [".github", "config", "data", "deliverables", "docs", "licenses", "power-query", "src", "tests"]:
        files += [p for p in (ROOT / folder).rglob("*") if p.is_file()
                  and "__pycache__" not in p.parts and not p.name.startswith("~$")
                  and p.suffix not in (".pyc", ".ndjson")]
    files += [p for p in (ROOT / "evidence").glob("*") if p.is_file() and
              (p.name.startswith("native-") and p.suffix in (".json", ".jpg") or
               p.name in ("expected-results.json", "sample-provenance.json", "batch_a_next.csv"))]
    return sorted(set(files))


if __name__ == "__main__":
    files = project_files()
    destination = ROOT.parent / "Excel Export Consolidator - Project.zip"
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, "excel-export-consolidator/" + path.relative_to(ROOT).as_posix())
    print(json.dumps({"archive": str(destination), "files": len(files), "bytes": destination.stat().st_size,
                      "sha256": hashlib.sha256(destination.read_bytes()).hexdigest()}))
