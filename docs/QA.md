# Validation record

## Automated reference checks

The independent Python implementation passed 16 unittest cases on 2026-10-17. These exercise:

1. Golden sample counts, accepted IDs, amount total, and reconciliation.
2. Leading-zero identifiers and four-decimal amounts.
3. Normalized identical repeats.
4. Conflicting amounts quarantining every copy.
5. An invalid duplicate quarantining its valid copy.
6. Missing IDs staying separate.
7. Invalid and noncanonical date rejection.
8. ShipDate before OrderDate.
9. Invalid amount grammar and a valid zero.
10. Unknown schema rejection.
11. Inconsistent CSV field count.
12. Unknown filename profiles.
13. Header-only files.
14. Explicit US and day-first date profiles.
15. Adding the reserved source record and repeating an unchanged reference run.
16. Logical record lineage for a quoted multiline field.

Run `python -m unittest discover -s tests -v` from the project root. CI runs this same reference suite. **CI does not run Excel Desktop or verify a native Refresh All.**

## Native Excel checks

The Power Query helper and all three worksheet output queries have evaluated in Excel Desktop for Windows. The baseline clean output loaded 291 records, the review output loaded 18 records, and the import output loaded 5 files. The review rows include 10 corrections and 8 skipped copies.

Native refreshes were completed on 2026-10-17, followed by read-only inspection of each saved workbook:

| Stage | Files | Parsed | Accepted | Corrections | Repeats | File issues | Accepted sales |
|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline | 5 | 309 | 291 | 10 | 8 | 0 | 57,507.7198 |
| Add reserved CSV | 6 | 310 | 292 | 10 | 8 | 0 | 57,522.6718 |
| Refresh unchanged inputs | 6 | 310 | 292 | 10 | 8 | 0 | 57,522.6718 |
| Add unsupported filename | 7 | 310 | 292 | 10 | 8 | 1 | 57,522.6718 |
| Remove test CSVs and refresh | 5 | 309 | 291 | 10 | 8 | 0 | 57,507.7198 |

The unsupported-file test exposed lazy evaluation escaping the original M error handler. The file table is now evaluated inside the handler; the corrected query passed that test and the restored baseline. Earlier added/unchanged stages predate this handler-only repair; the corrected file-issue stage also contains the added record and preserves all accepted rows.

For every saved stage, `src/verify_saved_workbook.py` compared all accepted fields, source lineage, review status/lineage, per-file counts, and cached summary values with the current inputs. It also checked for Excel error cells and the presence of three worksheet query tables. Install `requirements-qa.txt`, perform the relevant native refresh and Save, then run `python src/verify_saved_workbook.py restored` for the supplied baseline. This program does not operate Excel or trigger refresh.

Machine-readable results and workbook hashes are in `evidence/native-*.json`. `evidence/native-validation.json` indexes the stages. The native preview images are cropped screenshots of the actual refreshed workbook. Column widths, navy headers and wrapped review records remained in place after refresh. Empty-folder failure, arbitrary malformed CSV variants, cross-platform Excel behavior and large-scale performance were not tested natively.

## Scope

The sample tests do not establish arbitrary-input equivalence, performance at the workbook guardrail, or compatibility with Excel for Mac, Excel Online, LibreOffice, or a different client's export schema. Known reference/Power Query differences are documented in TECHNICAL.md. Client acceptance requires native tests using representative client files and independent source controls.
