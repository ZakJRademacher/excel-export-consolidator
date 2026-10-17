# Excel Export Consolidator

Combine recurring CSV exports into one usable Excel master, with a separate correction list and file-by-file totals.

![Actual Excel summary after native refresh](evidence/native-summary.jpg)

This portfolio project addresses a common operations task: several exports contain the same fields under different headings, mixed date formats, repeated records, and occasional invalid values. Excel Power Query reads the folder, standardizes known formats, checks records, and loads the results into filterable tables.

## What you receive

- **Clean master:** accepted, unique records with their source filename and record number.
- **Needs review:** excluded records, the specific reason, and a suggested correction step. Identical repeats are listed separately as skipped copies.
- **Import history:** the current folder's files, row counts, issue counts, and refresh timestamp.
- **Summary:** totals and the next action, linked to the loaded tables.
- Editable folder, column-alias, and filename-format settings.
- Power Query source, an independent Python reference implementation, tests, and a complete handoff guide.

The workbook is macro-free. Routine refreshes run inside Excel; Python is for reproduction and independent validation.

## Try the sample

1. Download the repository using **Code > Download ZIP**, then extract it. Keep the sample CSV folder.
2. Open [the workbook](deliverables/Export%20Consolidator.xlsx) in Excel Desktop for Windows with Power Query.
3. On **Start here**, replace the amber **Folder** value with the absolute path to your extracted `data/incoming` folder.
4. Select **Data > Refresh All**. Wait until every query finishes, then check for query errors and review **Summary**.

The supplied sample should produce:

| Result | Expected |
|---|---:|
| Files | 5 |
| Parsed records | 309 |
| Accepted records | 291 |
| Records needing correction | 10 |
| Identical repeated copies skipped | 8 |
| File issues | 0 |
| Accepted sales, source monetary units | 57,507.7198 |

The input reconciles as **309 = 291 + 10 + 8**. The review table has 18 rows because it includes both corrections and skipped repeats. Sales retain four decimal places; the source does not establish a currency.

## Weekly use

Place compatible exports in the configured folder and select **Refresh All**. Correct problems in the source CSVs, then refresh again. Output tables are regenerated, so manual output edits are not retained.

Each refresh rebuilds the master from the files currently in the folder. Retain files that belong in the current master. Replace a corrected file instead of leaving both old and corrected versions. **Import history is a current snapshot, not an append-only audit trail.**

This is a configured sales-export example, not a universal CSV importer. A different client's exports require agreed field mappings, date formats, categories, business keys, and validation rules.

![Actual Excel correction queue with source lineage](evidence/native-review.jpg)

## Verified in Excel

The delivered workbook was refreshed in Excel Desktop for Windows, then its saved tables and summary values were independently compared against the Python reference. Adding an export changed accepted rows from **291 to 292** and accepted sales from **57,507.7198 to 57,522.6718**. An unchanged refresh retained those results. An unsupported filename appeared as **one file issue**. Removing the two test files and refreshing restored the baseline. See the [native validation record](evidence/native-validation.json).

## Documentation

- [Refresh guide and troubleshooting](docs/REFRESH_GUIDE.md)
- [Data contract and duplicate rules](docs/DATA_CONTRACT.md)
- [Sample provenance and deliberate defects](docs/SAMPLE.md)
- [Implementation and rebuild notes](docs/TECHNICAL.md)
- [Validation scope and evidence](docs/QA.md)
- [Client handoff and adaptation checklist](docs/CLIENT_HANDOFF.md)
- [Portfolio walkthrough and interview notes](docs/PORTFOLIO.md)

## Reproduce the reference results

Requires Python 3.10 or later, with no third-party packages:

```console
python src/prepare_sample.py
python src/consolidate.py
python -m unittest discover -s tests -v
```

The preparation command recreates the five demonstration exports and configuration CSVs from the included frozen source partition. Run it only when you intend to reset the sample files. It does not refresh Excel. Configuration CSVs support the reference engine; Excel reads its settings tables on **Start here**.

## Source and scope

Historical sales values come from Rohit Sahoo's [Superstore Sales Dataset on Kaggle](https://www.kaggle.com/datasets/rohitsahoo/sales-forecasting). The demonstration uses the first 300 records from a frozen December 2018 partition, with disclosed export variations and seeded defects. These are demonstration conditions, not observed client errors or claimed business savings.

Code and documentation use the [MIT license](LICENSE). Dataset-derived files retain the source's GPL 2 label; see [data attribution](licenses/DATA.md).
