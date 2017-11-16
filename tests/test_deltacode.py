#
#  Copyright (c) 2017 nexB Inc. and others. All rights reserved.
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
    
    def test_Delta_create_object_removed(self):
        new = None
        old = models.File({'path': 'path/removed.txt'})

        delta = deltacode.Delta(new, old, 'removed')

        assert delta.new_file == None
        assert delta.old_file.path == 'path/removed.txt'
        assert delta.category == 'removed'

    def test_Delta_create_object_added(self):
        new = models.File({'path': 'path/added.txt'})
        old = None

        delta = deltacode.Delta(new, old, 'added')

        assert delta.new_file.path == 'path/added.txt'
        assert delta.old_file == None
        assert delta.category == 'added'
    
    def test_Delta_create_object_modified(self):
        new = models.File({'path': 'path/modified.txt', 'sha1': 'a'})
        old = models.File({'path': 'path/modified.txt', 'sha1': 'b'})

        delta = deltacode.Delta(new, old, 'modified')

        assert delta.new_file.path == 'path/modified.txt'
        assert delta.new_file.sha1 == 'a'
        assert delta.old_file.path == 'path/modified.txt'
        assert delta.old_file.sha1 == 'b'
        assert delta.category == 'modified'
    
    def test_Delta_create_object_unmodified(self):
        new = models.File({'path': 'path/unmodified.txt', 'sha1': 'a'})
        old = models.File({'path': 'path/unmodified.txt', 'sha1': 'a'})

        delta = deltacode.Delta(new, old, 'unmodified')

        assert delta.new_file.path == 'path/unmodified.txt'
        assert delta.new_file.sha1 == 'a'
        assert delta.old_file.path == 'path/unmodified.txt'
        assert delta.old_file.sha1 == 'a'
        assert delta.category == 'unmodified'

    def test_Delta_create_object_empty(self):
        delta = deltacode.Delta()

        assert delta.new_file == None
        assert delta.old_file == None
        assert delta.category == None
