# Data contract

## File scope

Read direct CSV files in the configured folder. Subfolders are not combined. Files starting with `.` or `~` are ignored; Power Query also ignores files marked hidden by Windows. Use UTF-8 CSV, with a header and consistent field structure. Embedded commas and newlines must be correctly quoted.

A filename must match exactly one case-insensitive prefix in **FileFormats**. These are the supplied profiles:

| Prefix | Delimiter | Exact date format | Numeric culture |
|---|---|---|---|
| batch_a_ | comma | yyyy-MM-dd | en-US |
| batch_b_ | comma | MM/dd/yyyy | en-US |
| batch_c_ | semicolon | dd/MM/yyyy | en-US |
| batch_d_ | comma | yyyy-MM-dd | en-US |
| batch_e_ | comma | yyyy-MM-dd | en-US |

The file must contain exactly these eight logical columns, in any order. Aliases on **Start here** can translate known headings. Header matching ignores case, spaces, underscores, and hyphens. Unknown or duplicate mapped columns reject the file; they are not silently dropped.

| Field | Type and rule |
|---|---|
| RowID | Nonempty text; stable unique line-record key across exports |
| OrderID | Nonempty text; several line records may belong to one order |
| OrderDate | Valid date in the file's exact format |
| ShipDate | Valid date in that format, on or after OrderDate |
| Category | Furniture, Office Supplies, or Technology |
| Region | Central, East, South, or West |
| ProductID | Nonempty text |
| Sales | Nonnegative amount, up to four decimal places, en-US punctuation |

Leading and trailing whitespace is trimmed. Identifier case and leading zeros are preserved. Category and region are matched without case sensitivity and given canonical spelling. Dates are validated by parsing and formatting them back to the specified format, preventing ambiguous date guesses.

Sales accepts `1234.5678` or correctly grouped `1,234.5678`. It rejects negative amounts, currency symbols, malformed grouping, scientific notation, nonfinite numbers, and more than four decimals. Excel uses Power Query's fixed-decimal Currency type. Displaying four decimals does not mean the data has an established currency. Validate actual currency and rounding requirements before client use.

## Duplicate policy

Compare all eight normalized business fields within each RowID group:

- One valid copy: accept it.
- Multiple valid, identical normalized copies: retain the first by source filename and logical record number. Log later copies as **Repeat skipped**.
- Different values for one RowID, or an invalid copy in a repeated-ID group: quarantine **every copy** as **Needs review**.
- Missing RowIDs: review each record separately.

There is no fuzzy matching, guessed repair, latest-file-wins rule, or inference from OrderID alone. This prevents two legitimate order lines from being merged and prevents a conflicting amount from silently entering a total.

## Lineage and reconciliation

SourceRow counts logical CSV records, including the header as record 1. A quoted multiline field does not create several source records. The review output includes the mapped original record as JSON, before trimming and normalization, plus the source filename and record number. It is not a byte-for-byte archive of the original CSV.

For successfully parsed files:

`InputRows = CleanRows + ReviewRows + RepeatedRows`

File issues appear separately with SourceRow 0, FileIssues 1, and InputRows 0 meaning **unknown**, not an empty file. Review all file issues before claiming a complete combined total.

## Limits

The workbook rejects more than 10,000 files or more than 100,000 parsed records per refresh. These guards are not performance benchmarks. It reads the folder again on each refresh; it is not incremental loading. It does not maintain change history, resolve business conflicts automatically, handle arbitrary currencies, or support arbitrary schemas without adaptation.
