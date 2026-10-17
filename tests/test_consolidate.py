import csv
import json
import shutil
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from consolidate import FIELDS, consolidate, parse_amount


class ConsolidationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.folder = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, rows, headers=FIELDS, delimiter=','):
        with (self.folder / name).open('w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=delimiter)
            writer.writerow(headers)
            writer.writerows(rows)

    def row(self, **changes):
        r = dict(zip(FIELDS, ['0001', 'O-1', '2018-12-01', '2018-12-03', 'Furniture', 'West', 'P-1', '12.3400']))
        r.update(changes)
        return [r[k] for k in FIELDS]

    def result(self):
        return consolidate(self.folder)

    def test_golden_fixture(self):
        expected = json.loads((ROOT / 'evidence/expected-results.json').read_text())
        result = consolidate(ROOT / 'data/incoming')
        self.assertEqual(result['metrics'], {k:v for k,v in expected.items() if k != 'clean_ids'})
        self.assertEqual([r['RowID'] for r in result['rows'] if r['Status']=='Clean'], expected['clean_ids'])
        self.assertEqual(sum(f['InputRows'] for f in result['files']), 291+10+8)

    def test_identifier_and_precision(self):
        self.write('batch_a_test.csv', [self.row(Sales='1,234.5678')])
        result = self.result()
        self.assertEqual(result['metrics']['clean_sales'], '1234.5678')
        self.assertEqual(result['rows'][0]['RowID'], '0001')

    def test_identical_normalized_repeat(self):
        self.write('batch_a_test.csv', [self.row(), self.row(Category=' furniture ', Region='WEST', Sales='12.34')])
        self.assertEqual([r['Status'] for r in self.result()['rows']], ['Clean', 'Repeat skipped'])

    def test_conflict_quarantines_every_copy(self):
        self.write('batch_a_test.csv', [self.row(), self.row(Sales='14')])
        self.assertEqual(self.result()['metrics']['review_rows'], 2)
        self.assertEqual(self.result()['metrics']['clean_rows'], 0)

    def test_invalid_copy_quarantines_valid_copy(self):
        self.write('batch_a_test.csv', [self.row(), self.row(Sales='N/A')])
        self.assertEqual(self.result()['metrics']['review_rows'], 2)

    def test_missing_ids_stay_separate(self):
        self.write('batch_a_test.csv', [self.row(RowID=''), self.row(RowID='')])
        result = self.result()
        self.assertEqual(result['metrics']['review_rows'], 2)
        self.assertTrue(all('Conflicting' not in r['Reason'] for r in result['rows']))

    def test_bad_date_is_not_guessed(self):
        for date in ['2018-02-30', '12/01/2018', '2018-1-01']:
            with self.subTest(date=date):
                self.write('batch_a_test.csv', [self.row(OrderDate=date)])
                self.assertIn('Invalid OrderDate', self.result()['rows'][0]['Reason'])

    def test_ship_before_order(self):
        self.write('batch_a_test.csv', [self.row(ShipDate='2018-11-30')])
        self.assertIn('ShipDate precedes', self.result()['rows'][0]['Reason'])

    def test_amount_grammar(self):
        for amount in ['-10', '$12', '1,23', '12.34567', 'NaN', '1e4', '', '1.']:
            with self.subTest(amount=amount), self.assertRaises(ValueError):
                parse_amount(amount)
        self.assertEqual(parse_amount('0.0000'), Decimal(0))

    def test_schema_rejected_as_a_file(self):
        self.write('batch_a_test.csv', [self.row()], headers=FIELDS[:-1]+['Mystery'])
        result = self.result()
        self.assertEqual(result['metrics']['file_issues'], 1)
        self.assertEqual(result['metrics']['clean_rows'], 0)

    def test_wrong_field_count_rejects_whole_file(self):
        self.write('batch_a_test.csv', [self.row(), self.row()[:-1]])
        result = self.result()
        self.assertEqual(result['metrics']['input_rows'], 0)
        self.assertEqual(result['metrics']['file_issues'], 1)

    def test_unknown_profile(self):
        self.write('unmapped.csv', [self.row()])
        self.assertEqual(self.result()['metrics']['file_issues'], 1)

    def test_header_only_file_logged(self):
        self.write('batch_a_test.csv', [])
        result = self.result()
        self.assertEqual(result['metrics']['files'], 1)
        self.assertEqual(result['metrics']['file_issues'], 0)
        self.assertEqual(result['metrics']['input_rows'], 0)

    def test_known_date_profiles(self):
        self.write('batch_b_test.csv', [self.row(OrderDate='12/01/2018', ShipDate='12/03/2018')])
        self.write('batch_c_test.csv', [self.row(RowID='0002', OrderDate='01/12/2018', ShipDate='03/12/2018')], delimiter=';')
        result = self.result()
        self.assertEqual(result['metrics']['clean_rows'], 2)
        self.assertTrue(all(r['OrderDate']=='2018-12-01' for r in result['rows']))

    def test_refresh_addition_and_idempotence(self):
        for p in (ROOT / 'data/incoming').glob('*.csv'):
            shutil.copyfile(p, self.folder / p.name)
        before = self.result()
        shutil.copyfile(ROOT / 'evidence/batch_a_next.csv', self.folder / 'batch_a_next.csv')
        after = self.result()
        with (ROOT / 'evidence/batch_a_next.csv').open(encoding='utf-8-sig', newline='') as f:
            amount = Decimal(list(csv.DictReader(f))[0]['Sales'])
        self.assertEqual(after['metrics']['clean_rows'], before['metrics']['clean_rows']+1)
        self.assertEqual(Decimal(after['metrics']['clean_sales']), Decimal(before['metrics']['clean_sales'])+amount)
        self.assertEqual(after, self.result())

    def test_multiline_record_lineage(self):
        self.write('batch_a_test.csv', [self.row(OrderID='O\n1')])
        row = self.result()['rows'][0]
        self.assertEqual(row['SourceRow'], 2)
        self.assertEqual(json.loads(row['RawRecord'])['OrderID'], 'O\n1')


if __name__ == '__main__':
    unittest.main(verbosity=2)
