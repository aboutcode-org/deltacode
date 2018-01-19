#
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/deltacode/
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
#  Visit https://github.com/nexB/deltacode/ for support and download.
#

from __future__ import absolute_import, print_function, unicode_literals, division

import codecs
from collections import OrderedDict
import json
import os

import unicodecsv

import click
from click.testing import CliRunner

from commoncode.testcase import FileBasedTesting
from deltacode import cli
from deltacode import DeltaCode
from deltacode import utils

# NOTE: From https://github.com/nexB/scancode-toolkit/blob/develop/src/scancode/cli_test_utils.py#L96
# NOTE: Do we need the references to monkeypatch or can we delete?
# NOTE: We'll need to revise the docstring.
def run_scan_click(options, monkeypatch=None, catch_exceptions=False):
    """
    Run a scan as a Click-controlled subprocess
    If monkeypatch is provided, a tty with a size (80, 43) is mocked.
    Return a click.testing.Result object.
    """
    # import click
    # from click.testing import CliRunner
    # from scancode import cli

    # NOTE: I don't think we need to use monkeypatch, do we?
    # if monkeypatch:
    #     monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    #     monkeypatch.setattr(click , 'get_terminal_size', lambda : (80, 43,))
    runner = CliRunner()

    return runner.invoke(cli.cli, options, catch_exceptions=catch_exceptions)


# NOTE: Based on https://github.com/nexB/scancode-toolkit/blob/develop/src/scancode/cli_test_utils.py#L46
# NOTE: We'll need to revise the docstring.
# NOTE: I don't think we need to pass/use the 'strip_dates' parameter.
def check_json_scan(expected_file, result_file, regen=False, strip_dates=False):
    """
    Check the scan result_file JSON results against the expected_file expected JSON
    results. Removes references to test_dir for the comparison. If regen is True the
    expected_file WILL BE overwritten with the results. This is convenient for
    updating tests expectations. But use with caution.
    """
    result = _load_json_result(result_file)
    if strip_dates:
        remove_dates(result)
    if regen:
        with open(expected_file, 'wb') as reg:
            json.dump(result, reg, indent=2, separators=(',', ': '))
    expected = _load_json_result(expected_file)
    if strip_dates:
        remove_dates(expected)

    # NOTE: The following note comes from the original ScanCode code.
    # NOTE we redump the JSON as a string for a more efficient comparison of
    # failures
    expected = json.dumps(expected, indent=2, sort_keys=True, separators=(',', ': '))
    result = json.dumps(result, indent=2, sort_keys=True, separators=(',', ': '))
    assert expected == result


# NOTE: Based on https://github.com/nexB/scancode-toolkit/blob/develop/src/scancode/cli_test_utils.py#L70
# NOTE: We'll need to revise the docstring.
def _load_json_result(result_file):
    """
    Load the result file as utf-8 JSON
    Sort the results by location.  [1/19/18 This line applies to the ScanCode test and should be deleted from this DeltaCode file.]
    """
    with codecs.open(result_file, encoding='utf-8') as res:
        scan_result = json.load(res, object_pairs_hook=OrderedDict)

    # NOTE: 1/19/18  Following used for ScanCode testing but not applicable to DeltaCode?
    # if scan_result.get('scancode_version'):
    #     del scan_result['scancode_version']

    # NOTE: 1/19/18 Is this line only for ScanCode output?
    # scan_result['files'].sort(key=lambda x: x['path'])
    return scan_result


def load_csv(location):
    """
    Copied from https://github.com/nexB/scancode-toolkit/blob/848de9fa4aaa1bd487b1cb36a8559a473e6459af/etc/scripts/test_json2csv.py
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
    Copied from https://github.com/nexB/scancode-toolkit/blob/848de9fa4aaa1bd487b1cb36a8559a473e6459af/etc/scripts/test_json2csv.py
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

class TestCLI(FileBasedTesting):

    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_write_csv_added(self):
        new_scan = self.get_test_loc('cli/new_added1.json')
        old_scan = self.get_test_loc('cli/old_added1.json')

        delta = DeltaCode(new_scan, old_scan)
        result_file = self.get_temp_file('.csv')
        cli.write_csv(delta, result_file)
        expected_file = self.get_test_loc('cli/added1.csv')
        check_csvs(result_file, expected_file)

    def test_write_csv_modified(self):
        new_scan = self.get_test_loc('cli/new_modified1.json')
        old_scan = self.get_test_loc('cli/old_modified1.json')

        delta = DeltaCode(new_scan, old_scan)
        result_file = self.get_temp_file('.csv')
        cli.write_csv(delta, result_file)
        expected_file = self.get_test_loc('cli/modified1.csv')
        check_csvs(result_file, expected_file)

    def test_write_csv_removed(self):
        new_scan = self.get_test_loc('cli/new_removed1.json')
        old_scan = self.get_test_loc('cli/old_removed1.json')

        delta = DeltaCode(new_scan, old_scan)
        result_file = self.get_temp_file('.csv')
        cli.write_csv(delta, result_file)
        expected_file = self.get_test_loc('cli/removed1.csv')
        check_csvs(result_file, expected_file)

    def test_write_csv_renamed(self):
        new_scan = self.get_test_loc('cli/new_renamed1.json')
        old_scan = self.get_test_loc('cli/old_renamed1.json')

        delta = DeltaCode(new_scan, old_scan)
        result_file = self.get_temp_file('.csv')
        cli.write_csv(delta, result_file)
        expected_file = self.get_test_loc('cli/renamed1.csv')
        check_csvs(result_file, expected_file)

    def test_write_csv_modified_new_license_added(self):
        new_scan = self.get_test_loc('cli/scan_modified_new_license_added.json')
        old_scan = self.get_test_loc('cli/scan_modified_old_license_added.json')

        delta = DeltaCode(new_scan, old_scan)
        result_file = self.get_temp_file('.csv')
        cli.write_csv(delta, result_file)
        expected_file = self.get_test_loc('cli/modified_new_license_added.csv')
        check_csvs(result_file, expected_file)

    def test_write_csv_modified_new_license_added_low_score(self):
        new_scan = self.get_test_loc('cli/scan_modified_new_license_added_low_score.json')
        old_scan = self.get_test_loc('cli/scan_modified_old_license_added_low_score.json')

        delta = DeltaCode(new_scan, old_scan)
        result_file = self.get_temp_file('.csv')
        cli.write_csv(delta, result_file)
        expected_file = self.get_test_loc('cli/modified_new_license_added_low_score.csv')
        check_csvs(result_file, expected_file)

    def test_write_csv_license_info_removed(self):
        new_scan = self.get_test_loc('cli/scan_new_license_info_removed.json')
        old_scan = self.get_test_loc('cli/scan_old_license_info_removed.json')

        delta = DeltaCode(new_scan, old_scan)
        result_file = self.get_temp_file('.csv')
        cli.write_csv(delta, result_file)
        expected_file = self.get_test_loc('cli/license_info_removed.csv')
        check_csvs(result_file, expected_file)

    def test_write_csv_license_info_added(self):
        new_scan = self.get_test_loc('cli/scan_new_license_info_added.json')
        old_scan = self.get_test_loc('cli/scan_old_license_info_added.json')

        delta = DeltaCode(new_scan, old_scan)
        result_file = self.get_temp_file('.csv')
        cli.write_csv(delta, result_file)
        expected_file = self.get_test_loc('cli/license_info_added.csv')
        check_csvs(result_file, expected_file)

    def test_write_csv_license_info_removed_below_cutoff_score(self):
        new_scan = self.get_test_loc('cli/scan_new_license_info_removed_below_cutoff_score.json')
        old_scan = self.get_test_loc('cli/scan_old_license_info_removed_below_cutoff_score.json')

        delta = DeltaCode(new_scan, old_scan)
        result_file = self.get_temp_file('.csv')
        cli.write_csv(delta, result_file)
        expected_file = self.get_test_loc('cli/license_info_removed_below_cutoff_score.csv')
        check_csvs(result_file, expected_file)

    def test_write_csv_license_info_added_below_cutoff_score(self):
        new_scan = self.get_test_loc('cli/scan_new_license_info_added_below_cutoff_score.json')
        old_scan = self.get_test_loc('cli/scan_old_license_info_added_below_cutoff_score.json')

        delta = DeltaCode(new_scan, old_scan)
        result_file = self.get_temp_file('.csv')
        cli.write_csv(delta, result_file)
        expected_file = self.get_test_loc('cli/license_info_added_below_cutoff_score.csv')
        check_csvs(result_file, expected_file)

    def test_write_csv_1_file_moved(self):
        new_scan = self.get_test_loc('cli/scan_1_file_moved_new.json')
        old_scan = self.get_test_loc('cli/scan_1_file_moved_old.json')

        delta = DeltaCode(new_scan, old_scan)
        result_file = self.get_temp_file('.csv')
        cli.write_csv(delta, result_file)
        expected_file = self.get_test_loc('cli/1_file_moved.csv')
        check_csvs(result_file, expected_file)

    def test_write_csv_1_file_moved_and_1_copy(self):
        new_scan = self.get_test_loc('cli/scan_1_file_moved_and_1_copy_new.json')
        old_scan = self.get_test_loc('cli/scan_1_file_moved_and_1_copy_old.json')

        delta = DeltaCode(new_scan, old_scan)
        result_file = self.get_temp_file('.csv')
        cli.write_csv(delta, result_file)
        expected_file = self.get_test_loc('cli/1_file_moved_and_1_copy.csv')
        check_csvs(result_file, expected_file)

    def test_write_csv_1_file_moved_and_added(self):
        new_scan = self.get_test_loc('cli/scan_1_file_moved_and_added_new.json')
        old_scan = self.get_test_loc('cli/scan_1_file_moved_and_added_old.json')

        delta = DeltaCode(new_scan, old_scan)
        result_file = self.get_temp_file('.csv')
        cli.write_csv(delta, result_file)
        expected_file = self.get_test_loc('cli/1_file_moved_and_added.csv')
        check_csvs(result_file, expected_file)

    def test_json_output_option_selected(self):
        new_scan = self.get_test_loc('deltacode/scan_1_file_moved_new.json')
        old_scan = self.get_test_loc('deltacode/scan_1_file_moved_old.json')

        result_file = self.get_temp_file('json')

        result = run_scan_click(['-n', new_scan, '-o',  old_scan, '-j', result_file])

        expected_file = self.get_test_loc('cli/1_file_moved.json')

        assert result.exit_code == 0
        check_json_scan(result_file, expected_file)

    def test_csv_output_option_selected(self):
        new_scan = self.get_test_loc('deltacode/scan_1_file_moved_new.json')
        old_scan = self.get_test_loc('deltacode/scan_1_file_moved_old.json')

        result_file = self.get_temp_file('.csv')

        result = run_scan_click(['-n', new_scan, '-o',  old_scan, '-c', result_file])

        expected_file = self.get_test_loc('cli/1_file_moved.csv')

        assert result.exit_code == 0
        check_csvs(result_file, expected_file)

    # NOTE: Based on https://github.com/nexB/scancode-toolkit/blob/develop/tests/scancode/test_cli.py#L233
    def test_usage_and_help(self):
        result = run_scan_click(['--help'])
        assert 'Usage: cli [OPTIONS]' in result.output

        result = run_scan_click([])
        assert 'Usage: cli [OPTIONS]' in result.output

        result = run_scan_click(['-xyz'])
        assert 'Error: no such option: -x' in result.output
