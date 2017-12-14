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

    def test_DeltaCode_to_dict_original_path_openssl(self):
        test_scan_new = self.get_test_loc('deltacode/to-dict-openssl-new.json')
        test_scan_old = self.get_test_loc('deltacode/to-dict-openssl-old.json')

        deltacode = DeltaCode(test_scan_new, test_scan_old)
        result = deltacode.to_dict()

        assert (len(result.get('added')) + len(result.get('removed'))
                + len(result.get('modified')) + len(result.get('unmodified'))) == 2459

        assert len(result.get('added')) == 76
        assert len(result.get('removed')) == 10
        assert len(result.get('modified')) == 291
        assert len(result.get('unmodified')) == 2082

    def test_DeltaCode_to_dict_original_path_dropbear(self):
        test_scan_new = self.get_test_loc('deltacode/to-dict-dropbear-new.json')
        test_scan_old = self.get_test_loc('deltacode/to-dict-dropbear-old.json')

        delta = DeltaCode(test_scan_new, test_scan_old)
        data = delta.to_dict()

        deltacode = DeltaCode(test_scan_new, test_scan_old)
        result = deltacode.to_dict()

        assert (len(result.get('added')) + len(result.get('removed'))
                + len(result.get('modified')) + len(result.get('unmodified'))) == 733

        assert len(result.get('added')) == 0
        assert len(result.get('removed')) == 0
        assert len(result.get('modified')) == 17
        assert len(result.get('unmodified')) == 716

    def test_DeltaCode_to_dict_original_path_zlib(self):
        test_scan_new = self.get_test_loc('deltacode/to-dict-zlib-new.json')
        test_scan_old = self.get_test_loc('deltacode/to-dict-zlib-old.json')

        delta = DeltaCode(test_scan_new, test_scan_old)
        data = delta.to_dict()

        deltacode = DeltaCode(test_scan_new, test_scan_old)
        result = deltacode.to_dict()

        assert (len(result.get('added')) + len(result.get('removed'))
                + len(result.get('modified')) + len(result.get('unmodified'))) == 259

        assert len(result.get('added')) == 0
        assert len(result.get('removed')) == 6
        assert len(result.get('modified')) == 34
        assert len(result.get('unmodified')) == 219

    def test_DeltaCode_to_dict_original_path_added1(self):
        test_scan_new = self.get_test_loc('deltacode/to-dict-new-added1.json')
        test_scan_old = self.get_test_loc('deltacode/to-dict-old-added1.json')

        deltacode = DeltaCode(test_scan_new, test_scan_old)
        result = deltacode.to_dict()

        assert (len(result.get('added')) + len(result.get('removed'))
                + len(result.get('modified')) + len(result.get('unmodified'))) == 9

        assert len(result.get('added')) == 1
        assert len(result.get('removed')) == 0
        assert len(result.get('modified')) == 0
        assert len(result.get('unmodified')) == 8

    def test_DeltaCode_to_dict_original_path_full_root(self):
        test_scan_new = self.get_test_loc('deltacode/to-dict-align-trees-simple-new.json')
        # Our old scan uses --full-root option in scancode
        test_scan_old = self.get_test_loc('deltacode/to-dict-align-trees-simple-old.json')

        deltacode = DeltaCode(test_scan_new, test_scan_old)
        result = deltacode.to_dict()

        assert (len(result.get('added')) + len(result.get('removed'))
                + len(result.get('modified')) + len(result.get('unmodified'))) == 33

        assert len(result.get('added')) == 0
        assert len(result.get('removed')) == 0
        assert len(result.get('modified')) == 0
        assert len(result.get('unmodified')) == 33

    def test_DeltaCode_to_dict_simple_file_added(self):
        new_scan = self.get_test_loc('deltacode/new_added1.json')
        old_scan = self.get_test_loc('deltacode/old_added1.json')

        deltacode = DeltaCode(new_scan, old_scan)
        result = deltacode.to_dict()

        assert (len(result.get('added')) + len(result.get('removed'))
                + len(result.get('modified')) + len(result.get('unmodified'))) == 9

        assert len(result.get('added')) == 1
        assert len(result.get('removed')) == 0
        assert len(result.get('modified')) == 0
        assert len(result.get('unmodified')) == 8

    def test_DeltaCode_to_dict_simple_file_modified(self):
        new_scan = self.get_test_loc('deltacode/new_modified1.json')
        old_scan = self.get_test_loc('deltacode/old_modified1.json')

        deltacode = DeltaCode(new_scan, old_scan)
        result = deltacode.to_dict()

        assert (len(result.get('added')) + len(result.get('removed'))
                + len(result.get('modified')) + len(result.get('unmodified'))) == 8

        assert len(result.get('added')) == 0
        assert len(result.get('removed')) == 0
        assert len(result.get('modified')) == 1
        assert len(result.get('unmodified')) == 7

    def test_DeltaCode_to_dict_simple_unmodified(self):
        test_file = self.get_test_loc('deltacode/to-dict-unmodified.json')

        deltacode = DeltaCode(test_file, test_file)

        expected = OrderedDict([
            ('added', []),
            ('removed', []),
            ('modified', []),
            ('unmodified', [
                OrderedDict([
                    ('category', 'unmodified'),
                    ('path', u'test/unmodified.txt'),
                    ('name', u'unmodified.txt'),
                    ('type', u'file'),
                    ('size', 11)
                ])
            ])
        ])

        result = deltacode.to_dict()

        assert result == expected

    def test_DeltaCode_to_dict_empty(self):
        delta = DeltaCode(None, None)

        result = delta.to_dict()

        assert result == OrderedDict([('added', []), ('removed', []), ('modified', []), ('unmodified', [])])

    def test_DeltaCode_invalid_paths(self):
        test_path_1 = '/some/invalid/path/1.json'
        test_path_2 = '/some/invalid/path/2.json'

        result = DeltaCode(test_path_1, test_path_2)

        assert result.new.path == ''
        assert result.new.files_count == 0
        assert result.new.files == []

        assert result.old.path == ''
        assert result.old.files_count == 0
        assert result.old.files == []

        assert result.deltas == OrderedDict([('added', []), ('removed', []), ('modified', []), ('unmodified', [])])

    def test_DeltaCode_empty_paths(self):
        result = DeltaCode('', '')

        assert result.new.path == ''
        assert result.new.files_count == 0
        assert result.new.files == []

        assert result.old.path == ''
        assert result.old.files_count == 0
        assert result.old.files == []

        assert result.deltas == OrderedDict([('added', []), ('removed', []), ('modified', []), ('unmodified', [])])

    def test_DeltaCode_None_paths(self):
        result = DeltaCode(None, None)

        assert result.new.path == ''
        assert result.new.files_count == 0
        assert result.new.files == []

        assert result.old.path == ''
        assert result.old.files_count == 0
        assert result.old.files == []
        assert result.deltas == OrderedDict([('added', []), ('removed', []), ('modified', []), ('unmodified', [])])

    def test_Delta_license_diff_new_no_license_info(self):
        new_file = models.File({'path': 'new/path.txt'})
        old_file = models.File({'path': 'old/path.txt', 'licenses': [{'key': 'mit', 'score': 50.0}]})

        result = deltacode.Delta(new_file, old_file, 'modified')

        assert result.category == 'license change'

    def test_Delta_license_diff_old_no_license_info(self):
        new_file = models.File({'path': 'new/path.txt', 'licenses': [{'key': 'mit', 'score': 50.0}]})
        old_file = models.File({'path': 'old/path.txt'})

        result = deltacode.Delta(new_file, old_file, 'modified')
        #result.license_diff()

        assert result.category == 'license change'

    def test_Delta_license_diff_single_diff_multiple_keys(self):
        new_file = models.File({'path': 'new/path.txt', 'licenses': [{'key': 'gpl-2.0', 'score': 100.0}, {'key': 'mit', 'score':30.0}]})
        old_file = models.File({'path': 'old/path.txt', 'licenses': [{'key': 'mit', 'score': 50.0}]})

        result = deltacode.Delta(new_file, old_file, 'modified')
        #result.license_diff()

        assert result.category == 'license change'

    def test_Delta_license_diff_no_diff_multiple_keys(self):
        new_file = models.File({'path': 'new/path.txt', 'licenses': [{'key': 'mit', 'score': 75.0}, {'key': 'mit', 'score': 90.0}]})
        old_file = models.File({'path': 'old/path.txt', 'licenses': [{'key': 'mit', 'score': 100.0}]})

        result = deltacode.Delta(new_file, old_file, 'modified')
        #result.license_diff()

        assert result.category == 'modified'

    def test_Delta_license_diff_no_diff_multiple_keys_low_score_new(self):
        new_file = models.File({'path': 'new/path.txt', 'licenses': [{'key': 'mit', 'score': 75.0}, {'key': 'mit', 'score': 90.0}, {'key': 'gpl-2.0', 'score': 49.9}]})
        old_file = models.File({'path': 'old/path.txt', 'licenses': [{'key': 'mit', 'score': 100.0}]})

        result = deltacode.Delta(new_file, old_file, 'modified')
        #result.license_diff()

        assert result.category == 'modified'

    def test_Delta_license_diff_no_diff_multiple_keys_low_score_old(self):
        new_file = models.File({'path': 'new/path.txt', 'licenses': [{'key': 'mit', 'score': 75.0}, {'key': 'mit', 'score': 90.0}]})
        old_file = models.File({'path': 'old/path.txt', 'licenses': [{'key': 'mit', 'score': 100.0}, {'key': 'gpl-2.0', 'score': 49.9}]})

        result = deltacode.Delta(new_file, old_file, 'modified')
        #result.license_diff()

        assert result.category == 'modified'

    def test_Delta_license_diff_single_diff(self):
        new_file = models.File({'path': 'new/path.txt', 'licenses': [{'key': 'gpl-2.0', 'score': 70.0}]})
        old_file = models.File({'path': 'old/path.txt', 'licenses': [{'key': 'mit', 'score': 80.0}]})

        result = deltacode.Delta(new_file, old_file, 'modified')
        #result.license_diff()

        assert result.category == 'license change'

    def test_Delta_license_diff_no_diff(self):
        new_file = models.File({'path': 'new/path.txt', 'licenses': [{'key': 'mit', 'score': 95.0}]})
        old_file = models.File({'path': 'old/path.txt', 'licenses': [{'key': 'mit', 'score': 95.0}]})

        result = deltacode.Delta(new_file, old_file, 'modified')
        #result.license_diff()

        assert result.category == 'modified'

    def test_Delta_license_diff_missing_diff_low_score_new(self):
        new_file = models.File({'path': 'new/path.txt', 'licenses': [{'key': 'mit', 'score': 45.0}]})
        old_file = models.File({'path': 'old/path.txt', 'licenses': [{'key': 'mit', 'score': 95.0}]})

        result = deltacode.Delta(new_file, old_file, 'modified')
        #result.license_diff()

        assert result.category == 'license change'

    def test_Delta_license_diff_missing_diff_low_score_old(self):
        new_file = models.File({'path': 'new/path.txt', 'licenses': [{'key': 'mit', 'score': 95.0}]})
        old_file = models.File({'path': 'old/path.txt', 'licenses': [{'key': 'mit', 'score': 45.0}]})

        result = deltacode.Delta(new_file, old_file, 'modified')
        #result.license_diff()

        assert result.category == 'license change'

    def test_Delta_license_diff_one_None(self):
        file_obj = models.File({'path': 'fake/path.txt'})

        first_None = deltacode.Delta(None, file_obj, 'removed')
        second_None = deltacode.Delta(file_obj, None, 'added')

        #first_None.license_diff()
        #second_None.license_diff()

        assert first_None.category == 'removed'
        assert second_None.category == 'added'

    def test_Delta_license_diff_None_files(self):
        delta = deltacode.Delta(None, None, None)

        assert type(delta.new_file) == type(models.File())
        assert type(delta.old_file) == type(models.File())
        assert delta.category == ''

    def test_DeltaCode_license_modified_low_score(self):
        new_scan = self.get_test_loc('deltacode/scan_modified_new_license_added_low_score.json')
        old_scan = self.get_test_loc('deltacode/scan_modified_old_license_added_low_score.json')

        result = DeltaCode(new_scan, old_scan)

        deltas = result.deltas

        assert len([i for i in deltas.get('modified') if i.category == 'license change']) == 0

    def test_DeltaCode_license_modified(self):
        new_scan = self.get_test_loc('deltacode/scan_modified_new_license_added.json')
        old_scan = self.get_test_loc('deltacode/scan_modified_old_license_added.json')

        result = DeltaCode(new_scan, old_scan)

        deltas = result.deltas

        assert len([i for i in deltas.get('modified') if i.category == 'license change']) == 2
        assert len([i for i in deltas.get('modified') if i.category == 'modified']) == 1

    def test_DeltaCode_no_license_key_value(self):
        new_scan = self.get_test_loc('deltacode/scan_modified_new_no_license_key.json')
        old_scan = self.get_test_loc('deltacode/scan_modified_old_no_license_key.json')

        result = DeltaCode(new_scan, old_scan)

        deltas = result.deltas

        assert len([i for i in deltas.get('modified') if i.category == 'license change']) == 0
        assert len([i for i in deltas.get('modified') if i.category == 'modified']) == 2

    def test_DeltaCode_no_license_changes(self):
        new_scan = self.get_test_loc('deltacode/scan_modified_new_no_license_changes.json')
        old_scan = self.get_test_loc('deltacode/scan_modified_old_no_license_changes.json')

        result = DeltaCode(new_scan, old_scan)

        deltas = result.deltas

        assert len([i for i in deltas.get('modified') if i.category == 'license change']) == 0
        assert len([i for i in deltas.get('modified') if i.category == 'modified']) == 2

    def test_Delta_to_dict_modified_license_added(self):
        new_scan = self.get_test_loc('deltacode/scan_modified_new_license_added.json')
        old_scan = self.get_test_loc('deltacode/scan_modified_old_license_added.json')

        result = DeltaCode(new_scan, old_scan)

        deltas = result.deltas

        assert [d.to_dict().get('category') for d in deltas.get('modified') if d.to_dict().get('path') == 'some/path/a/a1.py'] == ['license change']
        assert [d.to_dict().get('category') for d in deltas.get('modified') if d.to_dict().get('path') == 'some/path/b/b1.py'] == ['license change']
        assert [d.to_dict().get('category') for d in deltas.get('modified') if d.to_dict().get('path') == 'some/path/c/c1.py'] == ['modified']

    def test_Delta_to_dict_modified_license_added_low_score(self):
        new_scan = self.get_test_loc('deltacode/scan_modified_new_license_added_low_score.json')
        old_scan = self.get_test_loc('deltacode/scan_modified_old_license_added_low_score.json')

        result = DeltaCode(new_scan, old_scan)

        deltas = result.deltas

        assert [d.to_dict().get('category') for d in deltas.get('modified') if d.to_dict().get('path') == 'some/path/a/a1.py'] == ['modified']
        assert [d.to_dict().get('category') for d in deltas.get('modified') if d.to_dict().get('path') == 'some/path/b/b1.py'] == ['modified']

    def test_Delta_to_dict_modified_no_license_changes(self):
        new_scan = self.get_test_loc('deltacode/scan_modified_new_no_license_changes.json')
        old_scan = self.get_test_loc('deltacode/scan_modified_old_no_license_changes.json')

        result = DeltaCode(new_scan, old_scan)

        deltas = result.deltas

        assert [d.to_dict().get('category') for d in deltas.get('modified') if d.to_dict().get('path') == 'some/path/a/a1.py'] == ['modified']
        assert [d.to_dict().get('category') for d in deltas.get('modified') if d.to_dict().get('path') == 'some/path/b/b1.py'] == ['modified']

    def test_Delta_to_dict_modified_no_license_key(self):
        new_scan = self.get_test_loc('deltacode/scan_modified_new_no_license_key.json')
        old_scan = self.get_test_loc('deltacode/scan_modified_old_no_license_key.json')

        result = DeltaCode(new_scan, old_scan)

        deltas = result.deltas

        assert [d.to_dict().get('category') for d in deltas.get('modified') if d.to_dict().get('path') == 'some/path/a/a1.py'] == ['modified']
        assert [d.to_dict().get('category') for d in deltas.get('modified') if d.to_dict().get('path') == 'some/path/b/b1.py'] == ['modified']

    def test_Delta_to_dict_removed(self):
        old = models.File({
            'path': 'path/removed.txt',
            'type': 'file',
            'name': 'removed.txt',
            'size': 20,
            'sha1': 'a',
            'original_path': ''
        })

        expected = {
            'category': 'removed',
            'path': 'path/removed.txt',
            'name': 'removed.txt',
            'type': 'file',
            'size': 20
        }

        delta = deltacode.Delta(None, old, 'removed')

        assert delta.to_dict() == expected

    def test_Delta_to_dict_added(self):
        new = models.File({
            'path': 'path/added.txt',
            'type': 'file',
            'name': 'added.txt',
            'size': 20,
            'sha1': 'a',
            'original_path': ''
        })

        expected = {
            'category': 'added',
            'path': 'path/added.txt',
            'name': 'added.txt',
            'type': 'file',
            'size': 20
        }

        delta = deltacode.Delta(new, None, 'added')

        assert delta.to_dict() == expected

    def test_Delta_to_dict_modified(self):
        new = models.File({
            'path': 'path/modified.txt',
            'type': 'file',
            'name': 'modified.txt',
            'size': 20,
            'sha1': 'a',
            'original_path': ''
        })
        old = models.File({
            'path': 'path/modified.txt',
            'type': 'file',
            'name': 'modified.txt',
            'size': 21,
            'sha1': 'b',
            'original_path': ''
        })

        expected = {
            'category': 'modified',
            'path': 'path/modified.txt',
            'name': 'modified.txt',
            'type': 'file',
            'size': 20
        }

        delta = deltacode.Delta(new, old, 'modified')

        assert delta.to_dict() == expected

    def test_Delta_to_dict_unmodified(self):
        new = models.File({
            'path': 'path/unmodified.txt',
            'type': 'file',
            'name': 'unmodified.txt',
            'size': 20,
            'sha1': 'a',
            'original_path': ''
        })
        old = models.File({
            'path': 'path/unmodified.txt',
            'type': 'file',
            'name': 'unmodified.txt',
            'size': 20,
            'sha1': 'a',
            'original_path': ''
        })

        expected = {
            'category': 'unmodified',
            'path': 'path/unmodified.txt',
            'name': 'unmodified.txt',
            'type': 'file',
            'size': 20
        }

        delta = deltacode.Delta(new, old, 'unmodified')

        assert delta.to_dict() == expected

    def test_Delta_to_dict_empty(self):
        delta = deltacode.Delta()

        assert delta.to_dict() == OrderedDict([('category', 'unmodified'), ('path', ''), ('name', ''), ('type', ''), ('size', '')])

    def test_Delta_to_dict_license_modified(self):
        new_scan = self.get_test_loc('deltacode/scan_modified_new_license_added.json')
        old_scan = self.get_test_loc('deltacode/scan_modified_old_license_added.json')

        result = DeltaCode(new_scan, old_scan)

        expected = OrderedDict([
            ('added', []),
            ('removed', []),
            ('modified', [
                OrderedDict([
                    ('category', 'modified'),
                    ('path', u'some/path/c/c1.py'),
                    ('name', u'c1.py'),
                    ('type', u'file'),
                    ('size', 300)
                ]),
                OrderedDict([
                    ('category', 'license change'),
                    ('path', u'some/path/a/a1.py'),
                    ('name', u'a1.py'),
                    ('type', u'file'),
                    ('size', 300)
                ]),
                OrderedDict([
                    ('category', 'license change'),
                    ('path', u'some/path/b/b1.py'),
                    ('name', u'b1.py'),
                    ('type', u'file'),
                    ('size', 300)
                ])
            ]),
            ('unmodified', [])
        ])

        assert result.to_dict() == expected

    def test_Delta_to_dict_no_license_key_value(self):
        new_scan = self.get_test_loc('deltacode/scan_modified_new_no_license_key.json')
        old_scan = self.get_test_loc('deltacode/scan_modified_old_no_license_key.json')

        result = DeltaCode(new_scan, old_scan)

        expected = OrderedDict([
            ('added', []),
            ('removed', []),
            ('modified', [
                OrderedDict([
                    ('category', 'modified'),
                    ('path', u'some/path/a/a1.py'),
                    ('name', u'a1.py'),
                    ('type', u'file'),
                    ('size', 250)
                ]),
                OrderedDict([
                    ('category', 'modified'),
                    ('path', u'some/path/b/b1.py'),
                    ('name', u'b1.py'),
                    ('type', u'file'),
                    ('size', 310)
                ])
            ]),
            ('unmodified', [])
        ])

        assert result.to_dict() == expected

    def test_Delta_create_object_removed(self):
        new = None
        old = models.File({'path': 'path/removed.txt'})

        delta = deltacode.Delta(new, old, 'removed')

        assert type(delta.new_file) == type(models.File())
        assert delta.old_file.path == 'path/removed.txt'
        assert delta.category == 'removed'

    def test_Delta_create_object_added(self):
        new = models.File({'path': 'path/added.txt'})
        old = None

        delta = deltacode.Delta(new, old, 'added')

        assert delta.new_file.path == 'path/added.txt'
        assert type(delta.old_file) == type(models.File())
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

        assert type(delta.new_file) == type(models.File())
        assert type(delta.old_file) == type(models.File())
        assert delta.category == ''
