# Client handoff

## Before adapting this to business exports

Start with representative exports from each source. Agree on the following before changing the workbook:

1. What one record represents and the stable unique key. RowID in this sample identifies an order line, not an entire order.
2. Required fields, acceptable aliases, missing-value rules, and allowed categories.
3. Exact date formats and numeric punctuation for each source.
4. Currency, precision, refunds/negative amounts, tax treatment, and any reconciliation controls.
5. Whether exports are incremental batches or full snapshots, and how corrected records should replace prior versions.
6. Who resolves conflicts, where review notes live, and who signs off on totals.
7. File volume, record volume, Excel version, refresh frequency, and acceptable refresh time.

Do not simply rename client columns and assume the sample's rules fit. For example, returns may need negative sales, product categories will differ, and an export may reuse line IDs across stores. Those require explicit rule changes.

## Handoff acceptance

- Set the folder on the recipient's computer and perform a successful native refresh.
- Reconcile counts and monetary totals to an independently agreed source control.
- Show one accepted record and its source location.
- Show one invalid record, correct it in its CSV, and confirm it enters the master after refresh.
- Show repeated and conflicting IDs and agree the business resolution policy.
- Add a compatible file and verify the expected increase; refresh again with unchanged inputs.
- Demonstrate a file-level error and explain that old visible values can be stale after refresh failure.
- Confirm output formatting remains readable and the recipient can operate the workbook using the refresh guide.

## Weekly operator instructions

Save exports in the agreed folder, close them, Refresh All, check every query, review file and row errors, correct sources, refresh again, and save. Keep the folder fixed while refresh runs. Archive dated results outside the input folder if historical snapshots are required.

## Portfolio service description

“I consolidate recurring CSV exports into a refreshable Excel master, standardize agreed fields, identify invalid and duplicate records, and provide a correction list, reconciliation totals, and written refresh instructions.”

Estimate the work from the number of source formats, the rules needed, and the checks required for a successful handoff. Test the recipient's files and Excel version before promising compatibility.
