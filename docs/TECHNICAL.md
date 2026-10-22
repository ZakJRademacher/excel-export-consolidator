# Implementation

## Runtime data flow

`Start here settings + input CSV folder -> Consolidation -> CleanMaster / NeedsReview / ImportHistory -> Summary`

Excel reads the ImportSettings, ColumnMapping, and FileFormats tables from the workbook. `Consolidation` is a connection-only M query returning a record containing classified rows and per-file counts. The three output queries select their respective tables and load into worksheets. Summary formulas read the loaded results.

The M source is supplied in `power-query/` and also shown on the Query source worksheet. Changing a displayed source-code cell does not edit a native query. Use **Data > Queries & Connections > Edit > Advanced Editor** to change executable queries, and keep the supplied `.pq` files synchronized.

Power Query trims fields, validates schema and values, records provenance, groups by RowID, and assigns acceptance/review/repeat status. File-level errors are retained as explicit review entries. A global failure, such as a missing folder, duplicate mapping aliases, empty input folder, or guardrail breach, raises an Excel query error. Saved worksheet results may remain visible after that failure.

Each output can evaluate its dependency independently. Keep inputs fixed throughout Refresh All and check that all outputs finish. The snapshot does not provide a transactional database commit or append-only import history.

## Independent Python reference

`src/consolidate.py` implements normalization, validation, duplicate handling, lineage, and per-file reconciliation with the Python standard library. Decimal arithmetic avoids binary floating-point summation in the reference totals. Its JSON output also records SHA-256 for the input files; the Excel import-history table does not include hashes.

The reference is a separate implementation used for comparisons. It is not called by Excel and does not refresh the workbook. Its config CSVs correspond to the workbook's settings tables; changes to one do not automatically update the other.

Known engine differences outside the demonstrated baseline:

- Python returns an empty result for an empty folder; Excel raises an error to expose stale saved results.
- Python rejects any inconsistent record field count as a whole-file error. Power Query can pad a short record with nulls and flag its missing values at row level.
- Power Query uses a bounded fixed-decimal Currency type; Python Decimal can represent larger amounts. Very large values need explicit cross-engine acceptance tests.
- The M query enforces duplicate-alias, supported-culture, and refresh-size guards. The reference expects the supplied valid configuration.
- Power Query ignores Windows-hidden files; Python ignores the documented filename prefixes but does not inspect Windows hidden attributes.

Do not claim arbitrary-input equivalence from matching the sample. Test any new client's actual exports in Excel.

## Workbook authoring and rebuild

`src/build_workbook.mjs` creates the original workbook layout, cached demonstration values, configuration tables, summary formulas, and source-code worksheet with `@oai/artifact-tool`. It requires that package in the JavaScript environment and current reference JSON. The delivered workbook is subsequently integrated and finished in Excel Desktop with native Power Query connections and query tables.

**Running the layout builder does not reproduce those native connections.** It writes a disconnected workbook into `layout-build/`; do not replace the connected deliverable with that layout draft. The finished `.xlsx` is the canonical runtime deliverable. To rebuild fully, generate the layout, add Consolidation as connection-only, add the three output queries as worksheet tables, clear old cached result ranges before loading, and revalidate formulas and native refresh behavior.

No macros, background web service, scheduled task, or Python installation are required for normal Excel use. Refresh is initiated by the workbook user.


Workbook authoring also uses Python 3.10+ for display-only theme metadata normalization. Set `PYTHON` to its executable if `python` is unavailable. This helper preserves native workbook parts and does not recalculate formulas.
