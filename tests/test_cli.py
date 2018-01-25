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

from click.testing import CliRunner

from commoncode.testcase import FileBasedTesting
from deltacode import cli
from deltacode import DeltaCode
from deltacode import utils


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
        cli.write_csv(delta, result_file, True)
        expected_file = self.get_test_loc('cli/added1.csv')
        check_csvs(result_file, expected_file)

    def test_write_csv_modified(self):
        new_scan = self.get_test_loc('cli/new_modified1.json')
        old_scan = self.get_test_loc('cli/old_modified1.json')

        delta = DeltaCode(new_scan, old_scan)
        result_file = self.get_temp_file('.csv')
        cli.write_csv(delta, result_file, True)
        expected_file = self.get_test_loc('cli/modified1.csv')
        check_csvs(result_file, expected_file)

    def test_write_csv_removed(self):
        new_scan = self.get_test_loc('cli/new_removed1.json')
        old_scan = self.get_test_loc('cli/old_removed1.json')

        delta = DeltaCode(new_scan, old_scan)
        result_file = self.get_temp_file('.csv')
        cli.write_csv(delta, result_file, True)
        expected_file = self.get_test_loc('cli/removed1.csv')
        check_csvs(result_file, expected_file)

    def test_write_csv_renamed(self):
        new_scan = self.get_test_loc('cli/new_renamed1.json')
        old_scan = self.get_test_loc('cli/old_renamed1.json')

        delta = DeltaCode(new_scan, old_scan)
        result_file = self.get_temp_file('.csv')
        cli.write_csv(delta, result_file, True)
        expected_file = self.get_test_loc('cli/renamed1.csv')
        check_csvs(result_file, expected_file)

    def test_write_csv_modified_new_license_added(self):
        new_scan = self.get_test_loc('cli/scan_modified_new_license_added.json')
        old_scan = self.get_test_loc('cli/scan_modified_old_license_added.json')

        delta = DeltaCode(new_scan, old_scan)
        result_file = self.get_temp_file('.csv')
        cli.write_csv(delta, result_file, True)
        expected_file = self.get_test_loc('cli/modified_new_license_added.csv')
        check_csvs(result_file, expected_file)

    def test_write_csv_modified_new_license_added_low_score(self):
        new_scan = self.get_test_loc('cli/scan_modified_new_license_added_low_score.json')
        old_scan = self.get_test_loc('cli/scan_modified_old_license_added_low_score.json')

        delta = DeltaCode(new_scan, old_scan)
        result_file = self.get_temp_file('.csv')
        cli.write_csv(delta, result_file, True)
        expected_file = self.get_test_loc('cli/modified_new_license_added_low_score.csv')
        check_csvs(result_file, expected_file)

    def test_write_csv_license_info_removed(self):
        new_scan = self.get_test_loc('cli/scan_new_license_info_removed.json')
        old_scan = self.get_test_loc('cli/scan_old_license_info_removed.json')

        delta = DeltaCode(new_scan, old_scan)
        result_file = self.get_temp_file('.csv')
        cli.write_csv(delta, result_file, True)
        expected_file = self.get_test_loc('cli/license_info_removed.csv')
        check_csvs(result_file, expected_file)

    def test_write_csv_license_info_added(self):
        new_scan = self.get_test_loc('cli/scan_new_license_info_added.json')
        old_scan = self.get_test_loc('cli/scan_old_license_info_added.json')

        delta = DeltaCode(new_scan, old_scan)
        result_file = self.get_temp_file('.csv')
        cli.write_csv(delta, result_file, True)
        expected_file = self.get_test_loc('cli/license_info_added.csv')
        check_csvs(result_file, expected_file)

    def test_write_csv_license_info_removed_below_cutoff_score(self):
        new_scan = self.get_test_loc('cli/scan_new_license_info_removed_below_cutoff_score.json')
        old_scan = self.get_test_loc('cli/scan_old_license_info_removed_below_cutoff_score.json')

        delta = DeltaCode(new_scan, old_scan)
        result_file = self.get_temp_file('.csv')
        cli.write_csv(delta, result_file, True)
        expected_file = self.get_test_loc('cli/license_info_removed_below_cutoff_score.csv')
        check_csvs(result_file, expected_file)

    def test_write_csv_license_info_added_below_cutoff_score(self):
        new_scan = self.get_test_loc('cli/scan_new_license_info_added_below_cutoff_score.json')
        old_scan = self.get_test_loc('cli/scan_old_license_info_added_below_cutoff_score.json')

        delta = DeltaCode(new_scan, old_scan)
        result_file = self.get_temp_file('.csv')
        cli.write_csv(delta, result_file, True)
        expected_file = self.get_test_loc('cli/license_info_added_below_cutoff_score.csv')
        check_csvs(result_file, expected_file)

    def test_write_csv_1_file_moved(self):
        new_scan = self.get_test_loc('cli/scan_1_file_moved_new.json')
        old_scan = self.get_test_loc('cli/scan_1_file_moved_old.json')

        delta = DeltaCode(new_scan, old_scan)
        result_file = self.get_temp_file('.csv')
        cli.write_csv(delta, result_file, True)
        expected_file = self.get_test_loc('cli/1_file_moved.csv')
        check_csvs(result_file, expected_file)

    def test_write_csv_1_file_moved_and_1_copy(self):
        new_scan = self.get_test_loc('cli/scan_1_file_moved_and_1_copy_new.json')
        old_scan = self.get_test_loc('cli/scan_1_file_moved_and_1_copy_old.json')

        delta = DeltaCode(new_scan, old_scan)
        result_file = self.get_temp_file('.csv')
        cli.write_csv(delta, result_file, True)
        expected_file = self.get_test_loc('cli/1_file_moved_and_1_copy.csv')
        check_csvs(result_file, expected_file)

    def test_write_csv_1_file_moved_and_added(self):
        new_scan = self.get_test_loc('cli/scan_1_file_moved_and_added_new.json')
        old_scan = self.get_test_loc('cli/scan_1_file_moved_and_added_old.json')

        delta = DeltaCode(new_scan, old_scan)
        result_file = self.get_temp_file('.csv')
        cli.write_csv(delta, result_file, True)
        expected_file = self.get_test_loc('cli/1_file_moved_and_added.csv')
        check_csvs(result_file, expected_file)

    def test_json_output_option_selected_all_selected(self):
        new_scan = self.get_test_loc('deltacode/scan_1_file_moved_new.json')
        old_scan = self.get_test_loc('deltacode/scan_1_file_moved_old.json')

        result_file = self.get_temp_file('json')

        runner = CliRunner()
        result = runner.invoke(cli.cli, ['-n', new_scan, '-o',  old_scan, '-j', result_file, '-a'])

        assert result.exit_code == 0

        json_result = json.load(open(result_file))
        stats = {'unmodified': 7, 'removed': 0, 'added': 0, 'moved': 1, 'modified': 0}

        assert json_result.get('deltacode_stats') == stats

        moved_expected = {
            "category": "moved",
            "new": {
                "path": "b/a4.py",
                "type": "file",
                "name": "a4.py",
                "size": 200,
                "sha1": "6f71666c46446c29d3f45feef5419ae76fb86a5b",
                "original_path": "1_file_moved_new/b/a4.py",
                "licenses": [
                    {
                        "key": "apache-2.0",
                        "score": 40.0,
                        "short_name": "Apache 2.0",
                        "category": "Permissive",
                        "owner": "Apache Software Foundation"
                    }
                ]
            },
            "old": {
                "path": "a/a4.py",
                "type": "file",
                "name": "a4.py",
                "size": 200,
                "sha1": "6f71666c46446c29d3f45feef5419ae76fb86a5b",
                "original_path": "1_file_moved_old/a/a4.py",
                "licenses": [
                    {
                        "key": "apache-2.0",
                        "score": 40.0,
                        "short_name": "Apache 2.0",
                        "category": "Permissive",
                        "owner": "Apache Software Foundation"
                    }
                ]
            }
        }
        moved_result = [d for d in json_result.get('deltas') if d.get('category') == 'moved'].pop()

        assert moved_result == moved_expected

        unmodified_expected = {
            "category": "unmodified",
            "new": {
                "path": "a/a3.py",
                "type": "file",
                "name": "a3.py",
                "size": 200,
                "sha1": "fd5d3589c825f448546d7dcec36da3e567d35fe9",
                "original_path": "1_file_moved_new/a/a3.py",
                "licenses": [
                    {
                        "key": "apache-2.0",
                        "score": 40.0,
                        "short_name": "Apache 2.0",
                        "category": "Permissive",
                        "owner": "Apache Software Foundation"
                    }
                ]
            },
            "old": {
                "path": "a/a3.py",
                "type": "file",
                "name": "a3.py",
                "size": 200,
                "sha1": "fd5d3589c825f448546d7dcec36da3e567d35fe9",
                "original_path": "1_file_moved_old/a/a3.py",
                "licenses": [
                    {
                        "key": "apache-2.0",
                        "score": 40.0,
                        "short_name": "Apache 2.0",
                        "category": "Permissive",
                        "owner": "Apache Software Foundation"
                    }
                ]
            }
        }
        unmodified_result = [d for d in json_result.get('deltas') if d.get('category') == 'unmodified' and d.get('new').get('path') == 'a/a3.py'].pop()

        assert unmodified_result == unmodified_expected

    def test_json_output_option_selected_all_not_selected(self):
        new_scan = self.get_test_loc('deltacode/scan_1_file_moved_new.json')
        old_scan = self.get_test_loc('deltacode/scan_1_file_moved_old.json')

        result_file = self.get_temp_file('json')

        runner = CliRunner()
        result = runner.invoke(cli.cli, ['-n', new_scan, '-o',  old_scan, '-j', result_file])

        assert result.exit_code == 0

        json_result = json.load(open(result_file))
        stats = {'unmodified': 7, 'removed': 0, 'added': 0, 'moved': 1, 'modified': 0}

        assert json_result.get('deltacode_stats') == stats

        moved_expected = {
            "category": "moved",
            "new": {
                "path": "b/a4.py",
                "type": "file",
                "name": "a4.py",
                "size": 200,
                "sha1": "6f71666c46446c29d3f45feef5419ae76fb86a5b",
                "original_path": "1_file_moved_new/b/a4.py",
                "licenses": [
                    {
                        "key": "apache-2.0",
                        "score": 40.0,
                        "short_name": "Apache 2.0",
                        "category": "Permissive",
                        "owner": "Apache Software Foundation"
                    }
                ]
            },
            "old": {
                "path": "a/a4.py",
                "type": "file",
                "name": "a4.py",
                "size": 200,
                "sha1": "6f71666c46446c29d3f45feef5419ae76fb86a5b",
                "original_path": "1_file_moved_old/a/a4.py",
                "licenses": [
                    {
                        "key": "apache-2.0",
                        "score": 40.0,
                        "short_name": "Apache 2.0",
                        "category": "Permissive",
                        "owner": "Apache Software Foundation"
                    }
                ]
            }
        }

        moved_result = [d for d in json_result.get('deltas') if d.get('category') == 'moved'].pop()

        assert moved_result == moved_expected

        unmodified_result = [d for d in json_result.get('deltas') if d.get('category') == 'unmodified']

        assert len(unmodified_result) == 0

    def test_csv_output_option_selected_all_selected(self):
        new_scan = self.get_test_loc('deltacode/scan_1_file_moved_new.json')
        old_scan = self.get_test_loc('deltacode/scan_1_file_moved_old.json')

        result_file = self.get_temp_file('.csv')
        expected_file = self.get_test_loc('cli/1_file_moved.csv')

        runner = CliRunner()
        result = runner.invoke(cli.cli, ['-n', new_scan, '-o',  old_scan, '-c', result_file, '-a'])

        assert result.exit_code == 0
        check_csvs(result_file, expected_file)

    def test_csv_output_option_selected_all_not_selected(self):
        new_scan = self.get_test_loc('deltacode/scan_1_file_moved_new.json')
        old_scan = self.get_test_loc('deltacode/scan_1_file_moved_old.json')

        result_file = self.get_temp_file('.csv')
        expected_file = self.get_test_loc('cli/1_file_moved_all_not_selected.csv')

        runner = CliRunner()
        result = runner.invoke(cli.cli, ['-n', new_scan, '-o',  old_scan, '-c', result_file])

        assert result.exit_code == 0
        check_csvs(result_file, expected_file)

    def test_no_output_option_selected_all_selected(self):
        new_scan = self.get_test_loc('deltacode/scan_1_file_moved_new.json')
        old_scan = self.get_test_loc('deltacode/scan_1_file_moved_old.json')

        runner = CliRunner()
        result = runner.invoke(cli.cli, ['-n', new_scan, '-o',  old_scan, '-a'])

        assert result.exit_code == 0

        assert '"added": 0' in result.output
        assert '"modified": 0' in result.output
        assert '"moved": 1' in result.output
        assert '"removed": 0' in result.output
        assert '"unmodified": 7' in result.output

        assert '"category": "moved"' in result.output

        assert '"new"' in result.output
        assert '"path": "b/a4.py"' in result.output
        assert '"name": "a4.py"' in result.output
        assert '"type": "file"' in result.output
        assert '"size": 200' in result.output
        assert '"sha1": "6f71666c46446c29d3f45feef5419ae76fb86a5b"' in result.output
        assert '"original_path": "1_file_moved_new/b/a4.py"' in result.output
        assert '"key": "apache-2.0"' in result.output

        assert '"old"' in result.output
        assert '"path": "a/a4.py"' in result.output
        assert '"original_path": "1_file_moved_old/a/a4.py"' in result.output
        assert '"key": "apache-2.0"' in result.output

        assert '"category": "unmodified"' in result.output

        assert '"path": "a/a3.py"' in result.output
        assert '"name": "a3.py"' in result.output
        assert '"type": "file"' in result.output
        assert '"size": 200' in result.output
        assert '"sha1": "fd5d3589c825f448546d7dcec36da3e567d35fe9"' in result.output
        assert '"original_path": "1_file_moved_new/a/a3.py"' in result .output

    def test_no_output_option_selected_all_not_selected(self):
        new_scan = self.get_test_loc('deltacode/scan_1_file_moved_new.json')
        old_scan = self.get_test_loc('deltacode/scan_1_file_moved_old.json')

        runner = CliRunner()
        result = runner.invoke(cli.cli, ['-n', new_scan, '-o',  old_scan])

        assert result.exit_code == 0

        assert '"added": 0' in result.output
        assert '"modified": 0' in result.output
        assert '"moved": 1' in result.output
        assert '"removed": 0' in result.output
        assert '"unmodified": 7' in result.output

        assert '"category": "moved"' in result.output

        assert '"new"' in result.output
        assert '"path": "b/a4.py"' in result.output
        assert '"name": "a4.py"' in result.output
        assert '"type": "file"' in result.output
        assert '"size": 200' in result.output
        assert '"sha1": "6f71666c46446c29d3f45feef5419ae76fb86a5b"' in result.output
        assert '"original_path": "1_file_moved_new/b/a4.py"' in result.output
        assert '"key": "apache-2.0"' in result.output

        assert '"old"' in result.output
        assert '"path": "a/a4.py"' in result.output
        assert '"original_path": "1_file_moved_old/a/a4.py"' in result.output
        assert '"key": "apache-2.0"' in result.output

        assert '"category": "unmodified"' not in result.output

        assert '"path": "a/a3.py"' not in result.output
        assert '"name": "a3.py"' not in result.output
        assert '"sha1": "fd5d3589c825f448546d7dcec36da3e567d35fe9"' not in result.output
        assert '"original_path": "1_file_moved_new/a/a3.py"' not in result .output

    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(cli.cli, ['--help'])

        assert 'Usage: cli [OPTIONS]' in result.output
        assert 'Identify the changes that need to be made' in result.output
        assert 'If no file option is selected' in result.output
        assert 'Include unmodified files' in result.output

    def test_empty(self):
        runner = CliRunner()
        result = runner.invoke(cli.cli, [])

        assert 'Usage: cli [OPTIONS]' in result.output
        assert 'Error: Missing option "-n" / "--new".' in result.output

    def test_incorrect_flag(self):
        runner = CliRunner()
        result = runner.invoke(cli.cli, ['-xyz'])

        assert 'Error: no such option: -x' in result.output
