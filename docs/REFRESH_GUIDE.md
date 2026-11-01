# Refresh guide

## First setup

Use Excel Desktop for Windows with Power Query. The workbook opens with saved sample results. Follow the setup below and check all query statuses to confirm that it has refreshed from your local folder.

1. Extract the whole project ZIP to a normal local folder.
2. Open `deliverables/Export Consolidator.xlsx`.
3. Open **Start here**. In the amber **Folder** cell, enter the full local path to `data/incoming`. Do not include quotation marks or a CSV filename.
4. Select **Data > Refresh All**.
5. Open **Data > Queries & Connections** and wait for CleanMaster, NeedsReview, and ImportHistory to finish loading. Check for errors. Consolidation is a connection-only helper.
6. Check the Summary counts against the README sample totals. Save the workbook after a successful refresh.

Any Excel permission or privacy prompt must be reviewed by the person using Excel, following their organization's policies.

## Each week

1. Export CSVs using the agreed schema and filename profile. Close files after saving them.
2. Put them in the configured input folder. Do not modify files while Excel is refreshing.
3. Keep historical CSVs if they should remain in the master. For a current-only snapshot, move obsolete exports outside the input folder before refreshing.
4. Select **Refresh All**, wait for completion, and check query errors.
5. Review **Files needing correction** first. Such files have unknown row counts and can make the master incomplete.
6. Open **Needs review**, filter Status to **Needs review**, and correct the identified source records. Use SourceFile and SourceRow to locate them.
7. Save corrected CSVs under their existing filenames and refresh again.
8. Use **Clean master** for downstream reporting. Save a dated copy outside the input folder if you need a historical result.

Do not enter corrections or persistent notes in generated output tables. Those values can be replaced or move during refresh. Keep any review notes in a separate file keyed by RowID and source record.

## Read the summary

| Field | Meaning |
|---|---|
| Files loaded | CSVs listed in the current import snapshot, including files with issues |
| Rows parsed | Records from files that passed file-level parsing |
| Clean master rows | Accepted unique records |
| Rows needing correction | Rejected records, including every copy of a conflicting RowID |
| Identical repeats skipped | Extra copies excluded after normalization |
| Files needing correction | Files the query could not accept |
| Accepted sales | Sum of Sales from accepted records only |
| Last loaded | Timestamp from the loaded import-history query |

The timestamp is not a guarantee that every output succeeded. Always inspect all query statuses. A failed refresh can leave previously saved results visible, and independent output loads can finish at different times. Keep the source folder unchanged until every query finishes.

## Troubleshooting

| Symptom | Action |
|---|---|
| Folder not found | Re-enter the full extracted input-folder path on Start here |
| No CSV files found | Add compatible CSVs; old visible results remain stale until refresh succeeds |
| Exactly one matching format profile required | Match the filename to one configured prefix; remove overlapping profiles |
| Missing, extra or duplicate mapped columns | Compare the header to the eight required fields and the alias table |
| Invalid OrderDate or ShipDate | Use the exact date format for that filename profile |
| Invalid Sales | Remove currency symbols and use a nonnegative en-US number with at most four decimals |
| Conflicting RowID | Compare all copies; correct or remove obsolete source records rather than accepting an arbitrary copy |
| File issue with SourceRow 0 | This identifies a file-level problem; row counts are unknown |
| Changes disappear | Edit the source CSV, not a generated result table |

## Demonstrate an added export

Copy `evidence/batch_a_next.csv` into `data/incoming`, refresh, and expect 6 files, 310 parsed rows, and 292 accepted rows. Repeat the refresh with no file changes to confirm stable results. Move that demonstration file back outside the input folder, refresh, and return to the baseline totals. The extra record is a genuine reserved source record, not an invented sale.
