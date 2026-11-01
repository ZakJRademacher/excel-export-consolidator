# Independent Excel / Power Query practice

Work in a disposable workbook and input-folder copy. Attempt the task before consulting the [worked refresh guide](REFRESH_GUIDE.md).

## Your task

Begin with the documented five-file baseline. Configure one new filename format using the workbook's **FileFormats** table and map one unfamiliar heading through **ColumnMapping**. Use the reserved valid record in `evidence/batch_a_next.csv` as the business record for the exercise; make format/header variations only, without inventing its sale amount or changing IDs. Explain each mapping and date convention before refreshing.

Next create a deliberate conflicting RowID in a disposable file, refresh and trace every conflicting copy to its source. Correct that file and refresh again. Inspect a separate malformed-file example and explain why its unknown row count differs from an empty file.

## Acceptance checks

- Baseline: 309 parsed records = 291 accepted + 10 corrections + eight skipped repeats; accepted sales 57,507.7198 source units.
- After the one valid extra record: 310 parsed, 292 accepted. An unchanged rerun keeps the same result.
- Your native configuration is in the workbook's tables; changing a displayed query-source cell or repository CSV alone does not edit an executable workbook query.
- Text IDs, decimal precision and source references survive. Conflicts are reviewed, not resolved by picking an arbitrary copy.
- File issues remain visible; correct the source or configuration rather than overwriting generated outputs.
- Restore the disposable copy to the original five-file baseline and explain how you verified every output query finished successfully.

Keep a short handoff with the source-folder setting, mappings, actual refresh results and reconciliation. Native Excel evidence must come from an actual refresh, not just saved example values. This is an exercise to complete, not a proficiency claim.
