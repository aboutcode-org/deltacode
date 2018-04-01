from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import codecs
from collections import OrderedDict
import json
import os

import unicodecsv

from commoncode.testcase import FileBasedTesting

import json2csv


def load_csv(location):
    """
    Copied from https://github.com/nexB/scancode-toolkit/blob/develop/etc/scripts/test_json2csv.py
    Load a CSV file at location and return a tuple of (field names, list of rows as
    mappings field->value).
    """
    with codecs.open(location, 'rb', encoding='utf-8') as csvin:
        reader = unicodecsv.DictReader(csvin)
        fields = reader.fieldnames
        values = sorted(reader)
        return fields, values


def check_csvs(
        result_file, expected_file,
        regen=False):
    """
    Copied from https://github.com/nexB/scancode-toolkit/blob/develop/etc/scripts/test_json2csv.py
    Load and compare two CSVs.
    `ignore_keys`, a tuple of keys that will be ignored in the comparisons,
    has been removed from this function as unnecessary.
    """
    result_fields, results = load_csv(result_file)
    if regen:
        import shutil
        shutil.copy2(result_file, expected_file)
    expected_fields, expected = load_csv(expected_file)
    assert expected_fields == result_fields
    # then check results line by line for more compact results
    for exp, res in zip(sorted(expected), sorted(results)):
        assert exp == res


def check_json(result, expected_file, regen=False):
    if regen:
        with codecs.open(expected_file, 'wb', encoding='utf-8') as reg:
            reg.write(json.dumps(result, indent=4, separators=(',', ': ')))
    expected = json.load(
        codecs.open(expected_file, encoding='utf-8'), object_pairs_hook=OrderedDict)
    assert expected == result


class TestJson2CSV(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'testdata')

    def test_json_delta_to_csv_blank(self):
        test_json = self.get_test_loc('json2csv/empty.json')
        deltas = json2csv.load_deltas(test_json)

        headers = OrderedDict([
            ('score', []),
            ('factors', []),
            ('new', []),
            ('old', []),
        ])

        result = list(json2csv.flatten_deltas(deltas, headers))
        expected_file = self.get_test_loc('json2csv/empty.json-expected')

        check_json(result, expected_file)

    def test_json_delta_to_csv_added1(self):
        test_json = self.get_test_loc('json2csv/added1.json')
        deltas = json2csv.load_deltas(test_json)

        headers = OrderedDict([
            ('score', []),
            ('factors', []),
            ('new', []),
            ('old', []),
        ])

        result = list(json2csv.flatten_deltas(deltas, headers))
        # expected_file = self.get_test_loc('json2csv/added1.json-expected')
        expected_file = self.get_test_loc('json2csv/added1.strange-extension')

        check_json(result, expected_file)
        # check_json(result, expected_file, regen=True)

    def test_json_delta_to_csv_blank_csv(self):
        test_json = self.get_test_loc('json2csv/empty.json')
        result_file = self.get_temp_file('.csv')
        with open(result_file, 'wb') as rf:
            json2csv.json_delta_to_csv(test_json, rf)
        expected_file = self.get_test_loc('json2csv/empty.csv')

        check_csvs(result_file, expected_file)
