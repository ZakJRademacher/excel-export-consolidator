# Portfolio walkthrough

## Suggested title

CSV Export Cleanup and Consolidation in Excel Power Query

## Description

A refreshable Excel workflow that combines five differently formatted sales exports, standardizes known column names and dates, validates records, and separates usable data from corrections and duplicate copies. The sample contains 309 input records, producing 291 accepted records, 10 corrections, and 8 skipped repeats. Each result includes source lineage, while the summary and per-file totals explain what was loaded. Includes Power Query source, an independent Python reference, tests, source attribution, and operator documentation.

Historical data is public Kaggle data with disclosed seeded defects. No client outcomes are claimed.

## A three-minute demonstration

1. Start on Summary. Explain the 309 = 291 + 10 + 8 reconciliation.
2. Open Clean master. Filter Category or Region and show SourceFile and SourceRow.
3. Open Needs review. Show the invalid date and both conflicting RowID copies. Explain why choosing one amount automatically would be unsafe.
4. Open Start here. Show the folder setting and how known aliases and date profiles support recurring exports.
5. Add the reserved extra CSV, Refresh All, and show the increase to 292 accepted records. Remove the demonstration file from the input folder and restore the baseline.

## Knowledge needed to support this project

- Explain CSV quoting, delimiters, encoding, and why Excel can misinterpret dates and identifiers.
- Explain Power Query's import, transformation, query dependencies, and load destinations.
- Distinguish raw source values from normalized values and explain each validation rule.
- Explain RowID versus OrderID and why the business key determines deduplication.
- Trace a summary total to the master, source file, and source record.
- Explain how identical copies differ from conflicting records.
- Show how to check refresh errors and recognize stale saved results.
- Explain that settings tables in Excel and Python config CSVs are separate copies.
- Run the Python tests and explain the independent golden fixture.
- Identify changes needed for a client's schema, currencies, returns, keys, and full-snapshot exports.

Before offering client support, practice the demonstration and make one source correction yourself. If a question involves an untested input format, inspect a representative file and test it rather than promising it will work.
