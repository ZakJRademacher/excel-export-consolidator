# Sample provenance

Source: Rohit Sahoo, [Superstore Sales Dataset](https://www.kaggle.com/datasets/rohitsahoo/sales-forecasting), Kaggle. The dataset page labels the license GPL 2. Source monetary units are retained without assigning a currency.

`data/source/sales_2018-12.csv` is a frozen December 2018 partition used to reproduce this demonstration. Its SHA-256 and the individual seeded changes are recorded in `evidence/sample-provenance.json`.

`src/prepare_sample.py` selects the first 300 records in the frozen partition's existing order. It keeps eight relevant sales-line fields and splits the records into five batches of 60. It creates different headings, date formats, a semicolon-delimited export, capitalization variations, whitespace, and correctly grouped thousands.

The following problems are deliberately introduced:

- Eight extra identical copies in batch e.
- One conflicting extra copy with Sales increased by 10 source units; both copies are quarantined.
- Eight individual invalid records: missing RowID, invalid Sales, invalid date, unknown category, blank region, ShipDate before OrderDate, missing OrderID, and missing ProductID.

This yields 309 input records: 291 accepted, 10 requiring correction, and 8 repeated copies skipped. Expected accepted IDs and the amount total are derived from the unmodified source values and the explicit exclusion positions in the preparation script, independently of the cleanup engine.

The next source record, at position 301, is reserved in `evidence/batch_a_next.csv` for a refresh demonstration. It is outside the live input folder in the baseline delivery.

These are controlled test conditions. They do not establish that a real client's exports contain these defects or demonstrate measured time or cost savings.
