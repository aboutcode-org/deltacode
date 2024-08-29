#
# Copyright (c) 2017-2018 nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/aboutcode-org/deltacode/
# The DeltaCode software is licensed under the Apache License version 2.0.
# Data generated with DeltaCode require an acknowledgment.
# DeltaCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with DeltaCode or any DeltaCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with DeltaCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  DeltaCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  DeltaCode is a free and open source software analysis tool from nexB Inc. and others.
#  Visit https://github.com/aboutcode-org/deltacode/ for support and download.
#

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
    Copied from https://github.com/aboutcode-org/scancode-toolkit/blob/develop/etc/scripts/test_json2csv.py
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
    Copied from https://github.com/aboutcode-org/scancode-toolkit/blob/develop/etc/scripts/test_json2csv.py
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

    def test_json_delta_to_csv_blank_json(self):
        test_json = self.get_test_loc('json2csv/empty.json')
        deltas = json2csv.load_deltas(test_json)

        headers = OrderedDict([
            ('Score', []),
            ('Factors', []),
            ('Path', []),
            ('Name', []),
            ('Type', []),
            ('Size', []),
            ('Old Path', []),
        ])

        result = list(json2csv.flatten_deltas(deltas, headers))
        expected_file = self.get_test_loc('json2csv/empty.json-expected')

        check_json(result, expected_file)

    def test_json_delta_to_csv_added_json(self):
        test_json = self.get_test_loc('json2csv/added.json')
        deltas = json2csv.load_deltas(test_json)

        headers = OrderedDict([
            ('Score', []),
            ('Factors', []),
            ('Path', []),
            ('Name', []),
            ('Type', []),
            ('Size', []),
            ('Old Path', []),
        ])

        result = list(json2csv.flatten_deltas(deltas, headers))
        expected_file = self.get_test_loc('json2csv/added.json-expected')

        check_json(result, expected_file)

    def test_json_delta_to_csv_blank_csv(self):
        test_json = self.get_test_loc('json2csv/empty.json')
        result_file = self.get_temp_file('.csv')
        with open(result_file, 'wb') as rf:
            json2csv.json_delta_to_csv(test_json, rf)
        expected_file = self.get_test_loc('json2csv/empty.csv')

        check_csvs(result_file, expected_file)

    def test_json_delta_to_csv_added_csv(self):
        test_json = self.get_test_loc('json2csv/added.json')
        result_file = self.get_temp_file('.csv')
        with open(result_file, 'wb') as rf:
            json2csv.json_delta_to_csv(test_json, rf)
        expected_file = self.get_test_loc('json2csv/added.csv')

        check_csvs(result_file, expected_file)

    def test_json_delta_to_csv_modified_csv(self):
        test_json = self.get_test_loc('json2csv/modified.json')
        result_file = self.get_temp_file('.csv')
        with open(result_file, 'wb') as rf:
            json2csv.json_delta_to_csv(test_json, rf)
        expected_file = self.get_test_loc('json2csv/modified.csv')

        check_csvs(result_file, expected_file)

    def test_json_delta_to_csv_removed_csv(self):
        test_json = self.get_test_loc('json2csv/removed.json')
        result_file = self.get_temp_file('.csv')
        with open(result_file, 'wb') as rf:
            json2csv.json_delta_to_csv(test_json, rf)
        expected_file = self.get_test_loc('json2csv/removed.csv')

        check_csvs(result_file, expected_file)

    def test_json_delta_to_csv_renamed_csv(self):
        test_json = self.get_test_loc('json2csv/renamed.json')
        result_file = self.get_temp_file('.csv')
        with open(result_file, 'wb') as rf:
            json2csv.json_delta_to_csv(test_json, rf)
        expected_file = self.get_test_loc('json2csv/renamed.csv')

        check_csvs(result_file, expected_file)

    def test_json_delta_to_csv_new_license_added_csv(self):
        test_json = self.get_test_loc('json2csv/new_license_added.json')
        result_file = self.get_temp_file('.csv')
        with open(result_file, 'wb') as rf:
            json2csv.json_delta_to_csv(test_json, rf)
        expected_file = self.get_test_loc('json2csv/new_license_added.csv')

        check_csvs(result_file, expected_file)

    def test_json_delta_to_csv_license_info_removed_csv(self):
        test_json = self.get_test_loc('json2csv/license_info_removed.json')
        result_file = self.get_temp_file('.csv')
        with open(result_file, 'wb') as rf:
            json2csv.json_delta_to_csv(test_json, rf)
        expected_file = self.get_test_loc('json2csv/license_info_removed.csv')

        check_csvs(result_file, expected_file)

    def test_json_delta_to_csv_license_info_added_csv(self):
        test_json = self.get_test_loc('json2csv/license_info_added.json')
        result_file = self.get_temp_file('.csv')
        with open(result_file, 'wb') as rf:
            json2csv.json_delta_to_csv(test_json, rf)
        expected_file = self.get_test_loc('json2csv/license_info_added.csv')

        check_csvs(result_file, expected_file)

    def test_json_delta_to_csv_moved_csv(self):
        test_json = self.get_test_loc('json2csv/moved.json')
        result_file = self.get_temp_file('.csv')
        with open(result_file, 'wb') as rf:
            json2csv.json_delta_to_csv(test_json, rf)
        expected_file = self.get_test_loc('json2csv/moved.csv')

        check_csvs(result_file, expected_file)

    def test_json_delta_to_csv_1_file_moved_and_1_copy_csv(self):
        test_json = self.get_test_loc('json2csv/1_file_moved_and_1_copy.json')
        result_file = self.get_temp_file('.csv')
        with open(result_file, 'wb') as rf:
            json2csv.json_delta_to_csv(test_json, rf)
        expected_file = self.get_test_loc(
            'json2csv/1_file_moved_and_1_copy.csv')

        check_csvs(result_file, expected_file)

    def test_json_delta_to_csv_1_file_moved_and_added_csv(self):
        test_json = self.get_test_loc('json2csv/1_file_moved_and_added.json')
        result_file = self.get_temp_file('.csv')
        with open(result_file, 'wb') as rf:
            json2csv.json_delta_to_csv(test_json, rf)
        expected_file = self.get_test_loc(
            'json2csv/1_file_moved_and_added.csv')

        check_csvs(result_file, expected_file)

    def test_json_delta_to_csv_single_copyright_change_csv(self):
        test_json = self.get_test_loc('json2csv/single_copyright_change.json')
        result_file = self.get_temp_file('.csv')
        with open(result_file, 'wb') as rf:
            json2csv.json_delta_to_csv(test_json, rf)
        expected_file = self.get_test_loc(
            'json2csv/single_copyright_change.csv')

        check_csvs(result_file, expected_file)

    def test_json_delta_to_csv_copyright_info_added_csv(self):
        test_json = self.get_test_loc('json2csv/copyright_info_added.json')
        result_file = self.get_temp_file('.csv')
        with open(result_file, 'wb') as rf:
            json2csv.json_delta_to_csv(test_json, rf)
        expected_file = self.get_test_loc('json2csv/copyright_info_added.csv')

        check_csvs(result_file, expected_file)

    def test_json_delta_to_csv_copyright_info_removed_csv(self):
        test_json = self.get_test_loc('json2csv/copyright_info_removed.json')
        result_file = self.get_temp_file('.csv')
        with open(result_file, 'wb') as rf:
            json2csv.json_delta_to_csv(test_json, rf)
        expected_file = self.get_test_loc(
            'json2csv/copyright_info_removed.csv')

        check_csvs(result_file, expected_file)

    def test_json_delta_to_csv_copyright_and_license_info_added_csv(self):
        test_json = self.get_test_loc(
            'json2csv/copyright_and_license_info_added.json')
        result_file = self.get_temp_file('.csv')
        with open(result_file, 'wb') as rf:
            json2csv.json_delta_to_csv(test_json, rf)
        expected_file = self.get_test_loc(
            'json2csv/copyright_and_license_info_added.csv')

        check_csvs(result_file, expected_file)

    def test_json_delta_to_csv_copyright_and_license_info_removed_csv(self):
        test_json = self.get_test_loc(
            'json2csv/copyright_and_license_info_removed.json')
        result_file = self.get_temp_file('.csv')
        with open(result_file, 'wb') as rf:
            json2csv.json_delta_to_csv(test_json, rf)
        expected_file = self.get_test_loc(
            'json2csv/copyright_and_license_info_removed.csv')

        check_csvs(result_file, expected_file)

    def test_json_delta_to_csv_copyright_info_added_license_info_removed_csv(self):
        test_json = self.get_test_loc(
            'json2csv/copyright_info_added_license_info_removed.json')
        result_file = self.get_temp_file('.csv')
        with open(result_file, 'wb') as rf:
            json2csv.json_delta_to_csv(test_json, rf)
        expected_file = self.get_test_loc(
            'json2csv/copyright_info_added_license_info_removed.csv')

        check_csvs(result_file, expected_file)

    def test_json_delta_to_csv_license_info_added_copyright_info_removed_csv(self):
        test_json = self.get_test_loc(
            'json2csv/license_info_added_copyright_info_removed.json')
        result_file = self.get_temp_file('.csv')
        with open(result_file, 'wb') as rf:
            json2csv.json_delta_to_csv(test_json, rf)
        expected_file = self.get_test_loc(
            'json2csv/license_info_added_copyright_info_removed.csv')

        check_csvs(result_file, expected_file)

    def test_json_delta_to_csv_copyright_change_no_license_change_csv(self):
        test_json = self.get_test_loc(
            'json2csv/copyright_change_no_license_change.json')
        result_file = self.get_temp_file('.csv')
        with open(result_file, 'wb') as rf:
            json2csv.json_delta_to_csv(test_json, rf)
        expected_file = self.get_test_loc(
            'json2csv/copyright_change_no_license_change.csv')

        check_csvs(result_file, expected_file)

    def test_json_delta_to_csv_license_change_no_copyright_change_csv(self):
        test_json = self.get_test_loc(
            'json2csv/license_change_no_copyright_change.json')
        result_file = self.get_temp_file('.csv')
        with open(result_file, 'wb') as rf:
            json2csv.json_delta_to_csv(test_json, rf)
        expected_file = self.get_test_loc(
            'json2csv/license_change_no_copyright_change.csv')

        check_csvs(result_file, expected_file)
