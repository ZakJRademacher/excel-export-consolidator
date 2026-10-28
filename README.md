# Excel Export Consolidator

![Excel](https://img.shields.io/badge/Excel-217346?style=flat-square) ![Power Query](https://img.shields.io/badge/Power%20Query-356859?style=flat-square) ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square)

**How can differently formatted recurring exports become one usable Excel master?**

A macro-free **Excel Power Query** workflow that combines CSV files, standardizes known headers and dates, and separates accepted records from corrections.

![Excel summary after native refresh](evidence/native-summary.jpg)

[Download the workbook](deliverables/Export%20Consolidator.xlsx) · [Refresh guide](docs/REFRESH_GUIDE.md) · [Correction queue preview](evidence/native-review.jpg)

## What it delivers

- **Clean master:** validated unique records with source filename and record number.
- **Needs review:** invalid values, conflicting IDs and skipped duplicate copies, with reasons and correction steps.
- **Import history and summary:** file-level counts, totals and refresh status.

The sample reconciles **309 input records = 291 accepted + 10 corrections + 8 skipped repeats** across five exports. Accepted sales total **57,507.7198 source monetary units**. The review table contains 18 rows, including both corrections and skipped copies.

## Try the sample

1. Download the repository using **Code > Download ZIP**, then extract it.
2. Open the workbook in **Excel Desktop for Windows with Power Query**.
3. On **Start here**, set **Folder** to the absolute path of the extracted `data/incoming` folder.
4. Select **Data > Refresh All**, wait for completion, and check query errors and **Summary**.

Routine refresh runs inside Excel. Correct the source CSVs before refreshing; output-table edits are regenerated. Keep the files that belong in the current master. Import history describes the current folder snapshot.

## Evidence

Native Excel checks confirmed that adding a file changed accepted rows from **291 to 292**; an unchanged refresh kept those results. An unsupported filename appeared as a file issue, and removing the demonstration files restored the baseline.

[Native validation record](evidence/native-validation.json) · [Power Query source](power-query) · [Independent Python reference](src/consolidate.py) · [Tests](tests)

## Handoff and implementation

- [Operating and reproduction detail](docs/PROJECT_GUIDE.md)
- [Data contract and duplicate rules](docs/DATA_CONTRACT.md)
- [Client handoff](docs/CLIENT_HANDOFF.md)
- [Implementation and rebuild notes](docs/TECHNICAL.md)
- [Validation scope](docs/QA.md) · [Sample provenance](docs/SAMPLE.md)

## Scope

Independent portfolio demonstration using historical Kaggle Superstore values with disclosed export variations and seeded defects. Client adaptation requires agreed mappings, formats, keys and validation rules. No client savings are claimed, and the source does not establish a currency.

Code/documentation: [MIT](LICENSE). Dataset-derived files retain the source's GPL 2 label; see [data attribution](licenses/DATA.md).
