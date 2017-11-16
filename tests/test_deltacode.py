#
#  Copyright (c) 2015 nexB Inc. and others. All rights reserved.
#
from __future__ import absolute_import, print_function

from collections import OrderedDict
import json
import os

from click.testing import CliRunner
import pytest

from commoncode.testcase import FileBasedTesting
import deltacode
from deltacode import DeltaCode
from deltacode import models


def get_license_keys(deltas, age, path):
    """
    This helper function constructs a list of license keys from the
    DeltaCode.deltas OrderedDict passed from DeltaCode.determine_delta() to
    DeltaCode.modified_lic_diff() in order to add the 'license_changes'
    key/value pair to the OrderedDict.  See, e.g.,
    test_DeltaCode_license_modified().
    """
    if deltas['license_changes']:
        for lic_diff in deltas['license_changes']:
            if age == 'new_file' and lic_diff.new_file.path == path:
                new_key_list = [license.key for license in lic_diff.new_file.licenses]
                return sorted(new_key_list)
            elif age == 'old_file' and lic_diff.old_file.path == path:
                old_key_list = [license.key for license in lic_diff.old_file.licenses]
                return sorted(old_key_list)
    else:
        return []



class TestDeltacode(FileBasedTesting):

    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_align_and_index_scans(self):
        new_scan = self.get_test_loc('deltacode/ecos-align-index-new.json')
        old_scan = self.get_test_loc('deltacode/ecos-align-index-old.json')

        new = models.Scan(new_scan)
        old = models.Scan(old_scan)

        delta = DeltaCode(None, None)
        delta.new = new
        delta.old = old

        delta.align_scan()

        new_index = delta.new.index_files()
        old_index = delta.old.index_files()

        new_index_length = 0
        for k,v in new_index.items():
            new_index_length += len(v)

        old_index_length = 0
        for k,v in old_index.items():
            old_index_length += len(v)

        assert delta.new.files_count == new_index_length
        assert delta.old.files_count == old_index_length

    def test_DeltaCode_ecos_failed_counts_assertion(self):
        new_scan = self.get_test_loc('deltacode/ecos-failed-counts-assertion-new.json')
        old_scan = self.get_test_loc('deltacode/ecos-failed-counts-assertion-old.json')

        result = DeltaCode(new_scan, old_scan)

        assert result.new.files_count == 11408
        assert result.old.files_count == 8631

    def test_DeltaCode_abcm_aligned(self):
        new_scan = self.get_test_loc('deltacode/abcm-aligned-new.json')
        old_scan = self.get_test_loc('deltacode/abcm-aligned-old.json')

        result = DeltaCode(new_scan, old_scan)
        counts = result.get_stats()

        assert counts.get('added') == 25
        assert counts.get('modified') == 16
        assert counts.get('removed') == 5
        assert counts.get('unmodified') == 280

    def test_DeltaCode_zlib_unaligned_same_base_path(self):
        new_scan = self.get_test_loc('deltacode/zlib-unaligned-same-base-path-new.json')
        old_scan = self.get_test_loc('deltacode/zlib-unaligned-same-base-path-old.json')

        result = DeltaCode(new_scan, old_scan)
        counts = result.get_stats()

        assert counts.get('added') == 232
        assert counts.get('modified') == 22
        assert counts.get('removed') == 18
        assert counts.get('unmodified') == 0

    def test_DeltaCode_zlib_unaligned(self):
        new_scan = self.get_test_loc('deltacode/zlib-unaligned-new.json')
        old_scan = self.get_test_loc('deltacode/zlib-unaligned-old.json')

        result = DeltaCode(new_scan, old_scan)
        counts = result.get_stats()

        assert counts.get('added') == 254
        assert counts.get('modified') == 0
        assert counts.get('removed') == 40
        assert counts.get('unmodified') == 0

    def test_DeltaCode_identical(self):
        new_scan = self.get_test_loc('deltacode/identical.json')
        old_scan = self.get_test_loc('deltacode/identical.json')

        result = DeltaCode(new_scan, old_scan)
        counts = result.get_stats()

        assert counts.get('added') == 0
        assert counts.get('modified') == 0
        assert counts.get('removed') == 0
        assert counts.get('unmodified') == 8

    def test_DeltaCode_file_added(self):
        new_scan = self.get_test_loc('deltacode/new_added1.json')
        old_scan = self.get_test_loc('deltacode/old_added1.json')

        result = DeltaCode(new_scan, old_scan)
        counts = result.get_stats()

        assert counts.get('added') == 1
        assert counts.get('modified') == 0
        assert counts.get('removed') == 0
        assert counts.get('unmodified') == 8

    def test_DeltaCode_file_removed(self):
        new_scan = self.get_test_loc('deltacode/new_removed1.json')
        old_scan = self.get_test_loc('deltacode/old_removed1.json')

        result = DeltaCode(new_scan, old_scan)
        counts = result.get_stats()

        assert counts.get('added') == 0
        assert counts.get('modified') == 0
        assert counts.get('removed') == 1
        assert counts.get('unmodified') == 7

    def test_DeltaCode_file_renamed(self):
        new_scan = self.get_test_loc('deltacode/new_renamed1.json')
        old_scan = self.get_test_loc('deltacode/old_renamed1.json')

        result = DeltaCode(new_scan, old_scan)
        counts = result.get_stats()

        assert counts.get('added') == 1
        assert counts.get('modified') == 0
        assert counts.get('removed') == 1
        assert counts.get('unmodified') == 7

    def test_DeltaCode_file_modified(self):
        new_scan = self.get_test_loc('deltacode/new_modified1.json')
        old_scan = self.get_test_loc('deltacode/old_modified1.json')

        result = DeltaCode(new_scan, old_scan)
        counts = result.get_stats()

        assert counts.get('added') == 0
        assert counts.get('modified') == 1
        assert counts.get('removed') == 0
        assert counts.get('unmodified') == 7

    def test_DeltaCode_json_file_added(self):
        new_scan = self.get_test_loc('deltacode/new_added1.json')
        old_scan = self.get_test_loc('deltacode/old_added1.json')

        result = DeltaCode(new_scan, old_scan)
        loaded_json = result.to_dict()

        assert loaded_json['deltas_count'] == 9
        assert loaded_json['deltacode_stats']['added'] == 1
        assert loaded_json['deltacode_stats']['modified'] == 0
        assert loaded_json['deltacode_stats']['removed'] == 0
        assert loaded_json['deltacode_stats']['unmodified'] == 8

    def test_DeltaCode_json_file_modified(self):
        new_scan = self.get_test_loc('deltacode/new_modified1.json')
        old_scan = self.get_test_loc('deltacode/old_modified1.json')

        result = DeltaCode(new_scan, old_scan)
        loaded_json = result.to_dict()

        assert loaded_json['deltas_count'] == 8
        assert loaded_json['deltacode_stats']['added'] == 0
        assert loaded_json['deltacode_stats']['modified'] == 1
        assert loaded_json['deltacode_stats']['removed'] == 0
        assert loaded_json['deltacode_stats']['unmodified'] == 7

    def test_DeltaCode_align_scan_zlib_alignment_exception(self):
        new_scan = self.get_test_loc('deltacode/align-scan-zlib-alignment-exception-new.json')
        # Our old scan uses --full-root option in scancode
        old_scan = self.get_test_loc('deltacode/align-scan-zlib-alignment-exception-old.json')

        results = DeltaCode(new_scan, old_scan)

        assert results.new.files_count == 293
        assert results.old.files_count == 40

        for f in results.new.files:
            assert f.__class__.__name__ == 'File'
            assert f.original_path != None
            assert f.original_path == f.path

        for f in results.old.files:
            assert f.__class__.__name__ == 'File'
            assert f.original_path != None
            assert f.original_path == f.path

    def test_DeltaCode_delta_len_error(self):
        new_scan = self.get_test_loc('deltacode/delta-len-error-new.json')
        old_scan = self.get_test_loc('deltacode/delta-len-error-old.json')

        result = DeltaCode(new_scan, old_scan)

        # Modifiy files_count value to raise the error.
        # This should never happen in reality.
        result.new.files_count = 42

        with pytest.raises(AssertionError):
            result.determine_delta()

    def test_DeltaCode_invalid_paths(self):
        test_path_1 = '/some/invalid/path/1.json'
        test_path_2 = '/some/invalid/path/2.json'

        result = DeltaCode(test_path_1, test_path_2)

        assert result.new.path == '/some/invalid/path/1.json'
        assert result.new.files_count == None
        assert result.new.files == None

        assert result.old.path == '/some/invalid/path/2.json'
        assert result.new.files_count == None
        assert result.old.files == None

        assert result.deltas == None

    def test_DeltaCode_empty_paths(self):
        result = DeltaCode('', '')

        assert result.new.path == ''
        assert result.new.files_count == None
        assert result.new.files == None

        assert result.old.path == ''
        assert result.new.files_count == None
        assert result.old.files == None

        assert result.deltas == None

    def test_DeltaCode_None_paths(self):
        result = DeltaCode(None, None)

        assert result.new.path == ''
        assert result.new.files_count == None
        assert result.new.files == None

        assert result.old.path == ''
        assert result.new.files_count == None
        assert result.old.files == None

        assert result.deltas == None

    def test_Delta_license_diff_new_no_license_info(self):
        new_file = models.File({'path': 'new/path.txt'})
        old_file = models.File({'path': 'old/path.txt', 'licenses': [{'key': 'mit', 'score': 50.0}]})

        result = deltacode.Delta(new_file, old_file, 'modified').license_diff()

        assert result == True

    def test_Delta_license_diff_old_no_license_info(self):
        new_file = models.File({'path': 'new/path.txt', 'licenses': [{'key': 'mit', 'score': 50.0}]})
        old_file = models.File({'path': 'old/path.txt'})

        result = deltacode.Delta(new_file, old_file, 'modified').license_diff()

        assert result == True

    def test_Delta_license_diff_single_diff_multiple_keys(self):
        new_file = models.File({'path': 'new/path.txt', 'licenses': [{'key': 'gpl-2.0', 'score': 100.0}, {'key': 'mit', 'score':30.0}]})
        old_file = models.File({'path': 'old/path.txt', 'licenses': [{'key': 'mit', 'score': 50.0}]})

        result = deltacode.Delta(new_file, old_file, 'modified').license_diff()

        assert result == True

    def test_Delta_license_diff_no_diff_multiple_keys(self):
        new_file = models.File({'path': 'new/path.txt', 'licenses': [{'key': 'mit', 'score': 75.0}, {'key': 'mit', 'score': 90.0}]})
        old_file = models.File({'path': 'old/path.txt', 'licenses': [{'key': 'mit', 'score': 100.0}]})

        result = deltacode.Delta(new_file, old_file, 'modified').license_diff()

        assert result == False

    def test_Delta_license_diff_no_diff_multiple_keys_low_score_new(self):
        new_file = models.File({'path': 'new/path.txt', 'licenses': [{'key': 'mit', 'score': 75.0}, {'key': 'mit', 'score': 90.0}, {'key': 'gpl-2.0', 'score': 49.9}]})
        old_file = models.File({'path': 'old/path.txt', 'licenses': [{'key': 'mit', 'score': 100.0}]})

        result = deltacode.Delta(new_file, old_file, 'modified').license_diff()

        assert result == False

    def test_Delta_license_diff_no_diff_multiple_keys_low_score_old(self):
        new_file = models.File({'path': 'new/path.txt', 'licenses': [{'key': 'mit', 'score': 75.0}, {'key': 'mit', 'score': 90.0}]})
        old_file = models.File({'path': 'old/path.txt', 'licenses': [{'key': 'mit', 'score': 100.0}, {'key': 'gpl-2.0', 'score': 49.9}]})

        result = deltacode.Delta(new_file, old_file, 'modified').license_diff()

        assert result == False

    def test_Delta_license_diff_single_diff(self):
        new_file = models.File({'path': 'new/path.txt', 'licenses': [{'key': 'gpl-2.0', 'score': 70.0}]})
        old_file = models.File({'path': 'old/path.txt', 'licenses': [{'key': 'mit', 'score': 80.0}]})

        result = deltacode.Delta(new_file, old_file, 'modified').license_diff()

        assert result == True

    def test_Delta_license_diff_no_diff(self):
        new_file = models.File({'path': 'new/path.txt', 'licenses': [{'key': 'mit', 'score': 95.0}]})
        old_file = models.File({'path': 'old/path.txt', 'licenses': [{'key': 'mit', 'score': 95.0}]})

        result = deltacode.Delta(new_file, old_file, 'modified').license_diff()

        assert result == False

    def test_Delta_license_diff_missing_diff_low_score_new(self):
        new_file = models.File({'path': 'new/path.txt', 'licenses': [{'key': 'mit', 'score': 45.0}]})
        old_file = models.File({'path': 'old/path.txt', 'licenses': [{'key': 'mit', 'score': 95.0}]})

        result = deltacode.Delta(new_file, old_file, 'modified').license_diff()

        assert result == True

    def test_Delta_license_diff_missing_diff_low_score_old(self):
        new_file = models.File({'path': 'new/path.txt', 'licenses': [{'key': 'mit', 'score': 95.0}]})
        old_file = models.File({'path': 'old/path.txt', 'licenses': [{'key': 'mit', 'score': 45.0}]})

        result = deltacode.Delta(new_file, old_file, 'modified').license_diff()

        assert result == True

    def test_Delta_license_diff_one_None(self):
        file_obj = models.File({'path': 'fake/path.txt'})

        first_None = deltacode.Delta(None, file_obj, 'removed')
        second_None = deltacode.Delta(file_obj, None, 'added')

        result1 = first_None.license_diff()
        result2 = second_None.license_diff()

        assert result1 == False
        assert result2 == False

    def test_Delta_license_diff_None_files(self):
        delta = deltacode.Delta(None, None, None)

        result = delta.license_diff()

        assert result == False

    def test_DeltaCode_license_modified_low_score(self):
        new_scan = self.get_test_loc('deltacode/scan_modified_new_license_added_low_score.json')
        old_scan = self.get_test_loc('deltacode/scan_modified_old_license_added_low_score.json')

        result = DeltaCode(new_scan, old_scan)

        deltas = result.deltas

        assert len(deltas['license_changes']) == 0

    def test_DeltaCode_license_modified(self):
        new_scan = self.get_test_loc('deltacode/scan_modified_new_license_added.json')
        old_scan = self.get_test_loc('deltacode/scan_modified_old_license_added.json')

        result = DeltaCode(new_scan, old_scan)

        deltas = result.deltas

        assert len(deltas['license_changes']) == 2
        assert get_license_keys(deltas, 'new_file', 'some/path/a/a1.py') == sorted([u'apache-2.0', u'agpl-2.0', u'bsd-simplified', u'mit'])
        assert get_license_keys(deltas, 'old_file', 'some/path/a/a1.py') == sorted([u'apache-2.0', u'public-domain', u'bsd-simplified'])
        assert get_license_keys(deltas, 'new_file', 'some/path/b/b1.py') == sorted([u'apache-2.0', u'gpl-2.0', u'bsd-simplified', u'mit'])
        assert get_license_keys(deltas, 'old_file', 'some/path/b/b1.py') == sorted([u'mpl-2.0', u'public-domain', u'bsd-simplified'])
        assert get_license_keys(deltas, 'old_file', 'some/path/b/b1.py') == sorted(['mpl-2.0', 'public-domain', 'bsd-simplified'])
        assert get_license_keys(deltas, 'old_file', 'some/path/b/b1.py') != sorted([u'public-domain', u'bsd-simplified', u'mpl-4.01'])
        assert get_license_keys(deltas, 'old_file', 'some/path/b/b1.py') != sorted([u'public-domain', u'bsd-simplified', u'mpl-2.00'])
        assert get_license_keys(deltas, 'old_file', 'some/path/b/b1.py') == sorted([u'public-domain', u'bsd-simplified', u'mpl-2.0'])

    def test_DeltaCode_no_license_key_value(self):
        new_scan = self.get_test_loc('deltacode/scan_modified_new_no_license_key.json')
        old_scan = self.get_test_loc('deltacode/scan_modified_old_no_license_key.json')

        result = DeltaCode(new_scan, old_scan)

        deltas = result.deltas

        assert len(deltas['license_changes']) == 0
        assert get_license_keys(deltas, 'new_file', 'some/path/a/a1.py') == sorted([])
        assert get_license_keys(deltas, 'old_file', 'some/path/a/a1.py') == sorted([])
        assert get_license_keys(deltas, 'new_file', 'some/path/b/b1.py') == sorted([])
        assert get_license_keys(deltas, 'old_file', 'some/path/b/b1.py') == sorted([])

    def test_DeltaCode_no_license_changes(self):
        new_scan = self.get_test_loc('deltacode/scan_modified_new_no_license_changes.json')
        old_scan = self.get_test_loc('deltacode/scan_modified_old_no_license_changes.json')

        result = DeltaCode(new_scan, old_scan)

        deltas = result.deltas

        assert len(deltas['license_changes']) == 0
        assert get_license_keys(deltas, 'new_file', 'some/path/a/a1.py') == sorted([])
        assert get_license_keys(deltas, 'old_file', 'some/path/a/a1.py') == sorted([])
        assert get_license_keys(deltas, 'new_file', 'some/path/b/b1.py') == sorted([])
        assert get_license_keys(deltas, 'old_file', 'some/path/b/b1.py') == sorted([])
