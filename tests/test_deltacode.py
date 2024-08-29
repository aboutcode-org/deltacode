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
from deltacode import test_utils
from deltacode import utils
from deltacode.utils import collect_errors
from deltacode.test_utils import get_aligned_path
from commoncode.resource import VirtualCodebase


class TestDeltacode(FileBasedTesting):

    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_align_and_index_scans(self):
        new = self.get_test_loc('deltacode/ecos-align-index-new.json')
        old = self.get_test_loc('deltacode/ecos-align-index-old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        delta = DeltaCode(new, old, options)

        new_offset, old_offset = utils.align_trees(
            delta.codebase1, delta.codebase2)

        assert new_offset == 2

        assert old_offset == 2

    # def test_DeltaCode_ecos_failed_counts_assertion(self):
    #     new_scan = self.get_test_loc('deltacode/ecos-failed-counts-assertion-new.json')
    #     old_scan = self.get_test_loc('deltacode/ecos-failed-counts-assertion-old.json')

    #     options = OrderedDict([
    #         ('--all-delta-types', False)
    #     ])

    #     result = DeltaCode(new_scan, old_scan, options)

    #     assert len(result.new_files) == 11409
    #     assert len(result.old_files) == 8632

    def test_DeltaCode_align_scan_zlib_alignment_exception(self):
        new_scan = self.get_test_loc(
            'deltacode/align-scan-zlib-alignment-exception-new.json')
        # Our old scan uses --full-root option in scancode
        old_scan = self.get_test_loc(
            'deltacode/align-scan-zlib-alignment-exception-old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        results = DeltaCode(new_scan, old_scan, options)

        assert results.codebase1.compute_counts(
        )[0] + results.codebase1.compute_counts()[1] == 294
        assert results.codebase2.compute_counts(
        )[0] + results.codebase2.compute_counts()[1] == 41

        for f in results.codebase1.walk():
            assert f.__class__.__name__ == 'ScannedResource'
            assert f.path is not None
            assert not f.is_filtered

        for f in results.codebase2.walk():
            assert f.__class__.__name__ == 'ScannedResource'
            assert f.path is not None
            assert not f.is_filtered

    @pytest.mark.xfail(reason='Tests no longer required having None paths')
    def test_DeltaCode_invalid_paths(self):
        test_path_1 = '/some/invalid/path/1.json'
        test_path_2 = '/some/invalid/path/2.json'

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        result = DeltaCode(test_path_1, test_path_2, options)

        assert result.codebase1 == None
        assert result.codebase2 == None
        assert len(result.errors) >= 1

    @pytest.mark.xfail(reason='Tests no longer required having invalid paths')
    def test_DeltaCode_empty_paths(self):
        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        result = DeltaCode('', '', options)

        assert result.codebase1 == None

        assert result.codebase2 == None

        assert result.deltas == []

        assert result.errors

    @pytest.mark.xfail(reason='Tests no longer required having None paths')
    def test_DeltaCode_None_paths(self):
        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        result = DeltaCode(None, None, options)

        assert result.errors
        assert result.codebase1 == None
        assert result.codebase2 == None
        assert result.deltas == []

    @pytest.mark.xfail(reason='Tests no longer required having None paths')
    def test_Delta_one_None(self):
        try:
            file_obj = VirtualCodebase('fake/path.txt')
        except IOError:
            file_obj = None
            pass
        first_None = deltacode.Delta(10, None, file_obj)
        second_None = deltacode.Delta(100, file_obj, None)

        assert first_None.score == 10
        assert second_None.score == 100

        assert first_None.factors == []
        assert second_None.factors == []

        expected_first = OrderedDict([
            ('status', ''),
            ('factors', []),
            ('score', 10),
            ('new', None),
            ('old', OrderedDict([
                ('path', 'fake/path.txt'),
                ('type', ''),
                ('name', ''),
                ('size', ''),
                ('sha1', ''),
                ('fingerprint', ''),
                ('original_path', ''),
                ('licenses', []),
                ('copyrights', [])
            ]))
        ])

        expected_second = OrderedDict([
            ('status', ''),
            ('factors', []),
            ('score', 100),
            ('new', OrderedDict([
                ('path', 'fake/path.txt'),
                ('type', ''),
                ('name', ''),
                ('size', ''),
                ('sha1', ''),
                ('fingerprint', ''),
                ('original_path', ''),
                ('licenses', []),
                ('copyrights', [])
            ])),
            ('old', None)
        ])

    def test_DeltaCode_license_modified(self):
        new_scan = self.get_test_loc(
            'deltacode/scan_modified_new_license_added.json')
        old_scan = self.get_test_loc(
            'deltacode/scan_modified_old_license_added.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        result = DeltaCode(new_scan, old_scan, options)

        deltas = result.deltas

        assert len([i for i in deltas if i.score == 50]) == 1
        assert len([i for i in deltas if i.score == 40]) == 1
        assert len([i for i in deltas if i.score == 30]) == 0
        assert len([i for i in deltas if i.score == 20]) == 1

        assert [d.score for d in deltas if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'some/path/a/a1.py'] == [50]
        assert [d.score for d in deltas if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'some/path/b/b1.py'] == [40]
        assert [d.score for d in deltas if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'some/path/c/c1.py'] == [20]

        assert [d.factors for d in deltas if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'some/path/a/a1.py'].pop() == ['license change', 'copyleft added']
        assert [d.status for d in deltas if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'some/path/a/a1.py'] == ['modified']
        assert [d.factors for d in deltas if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'some/path/b/b1.py'].pop() == ['license change', 'copyleft added']
        assert [d.status for d in deltas if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'some/path/b/b1.py'] == ['modified']
        assert [d.factors for d in deltas if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'some/path/c/c1.py'].pop() == []
        assert [d.status for d in deltas if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'some/path/c/c1.py'] == ['modified']

    def test_DeltaCode_errors_empty(self):
        new_scan = self.get_test_loc('deltacode/scan_1_file_moved_new.json')
        old_scan = self.get_test_loc('deltacode/scan_1_file_moved_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        result = DeltaCode(new_scan, old_scan, options)

        assert result.errors == []

    def test_Delta_to_dict_removed(self):
        new_scan = self.get_test_loc(
            'deltacode/Delta_to_dict_removed_new.json')
        old_scan = self.get_test_loc(
            'deltacode/Delta_to_dict_removed_old.json')

        expected = OrderedDict([
            ('status', 'removed'),
            ('factors', []),
            ('score', 0),
            ('new', None),
            ('old', OrderedDict([
                ('path', 'music/CONTRIBUTING.rst'),
                ('type', 'file'),
                ('name', 'CONTRIBUTING.rst'),
                ('size', 7783),
                ('sha1', '476f2310923943accd0ec4361ab36053d8ce46e0'),
                ('fingerprint', ''),
                ('original_path', 'music/CONTRIBUTING.rst'),
                ('licenses', []),
                ('copyrights', [])
            ]))
        ])

        results = DeltaCode(new_scan, old_scan, {})
        delta = results.deltas[0]
        delta.status = 'removed'

        assert delta.to_dict(results) == expected

    def test_Delta_to_dict_added(self):
        new = self.get_test_loc('deltacode/delta_to_dict_added_new.json')
        old = self.get_test_loc('deltacode/delta_to_dict_added_old.json')

        expected = OrderedDict([
            ('status', 'added'),
            ('factors', []),
            ('score', 100),
            ('new', OrderedDict([
                ('path', 'path/added.txt'),
                ('type', 'file'),
                ('name', 'added.txt'),
                ('size', 20),
                ('sha1', 'a'),
                ('fingerprint', 'e30cf09443e7878dfed3288886e12345'),
                ('original_path', 'path/added.txt'),
                ('licenses', []),
                ('copyrights', [])
            ])),
            ('old', None)
        ])

        deltacode = DeltaCode(new, old, {})
        delta = deltacode.deltas[0]
        delta.status = 'added'

        assert delta.to_dict(deltacode) == expected

    def test_Delta_to_dict_modified(self):
        new = self.get_test_loc('deltacode/delta_to_dict_modified_new.json')
        old = self.get_test_loc('deltacode/delta_to_dict_modified_old.json')

        expected = OrderedDict([
            ('status', 'modified'),
            ('factors', []),
            ('score', 20),
            ('new', OrderedDict([
                ('path', 'path/modified.txt'),
                ('type', 'file'),
                ('name', 'modified.txt'),
                ('size', 20),
                ('sha1', 'a'),
                ("fingerprint", ""),
                ('original_path', 'path/modified.txt'),
                ('licenses', []),
                ('copyrights', [])
            ])),
            ('old', OrderedDict([
                ('path', 'path/modified.txt'),
                ('type', 'file'),
                ('name', 'modified.txt'),
                ('size', 21),
                ('sha1', 'b'),
                ("fingerprint", ""),
                ('original_path', 'path/modified.txt'),
                ('licenses', []),
                ('copyrights', [])
            ]))
        ])

        deltacode_object = DeltaCode(new, old, {})
        delta = deltacode_object.deltas[0]
        delta.status = 'modified'

        assert delta.to_dict(deltacode_object) == expected

    def test_Delta_to_dict_unmodified(self):
        new = self.get_test_loc('deltacode/delta_to_dict_unmodified_new.json')
        old = self.get_test_loc('deltacode/delta_to_dict_unmodified_old.json')

        expected = OrderedDict([
            ('status', 'unmodified'),
            ('factors', []),
            ('score', 0),
            ('new', OrderedDict([
                ('path', 'path/unmodified.txt'),
                ('type', 'file'),
                ('name', 'unmodified.txt'),
                ('size', 20),
                ('sha1', 'a'),
                ('fingerprint', 'e30cf09443e7878dfed3288886e97542'),
                ('original_path', 'path/unmodified.txt'),
                ('licenses', []),
                ('copyrights', [])
            ])),
            ('old', OrderedDict([
                ('path', 'path/unmodified.txt'),
                ('type', 'file'),
                ('name', 'unmodified.txt'),
                ('size', 20),
                ('sha1', 'a'),
                ('fingerprint', 'e30cf09443e7878dfed3288886e97542'),
                ('original_path', 'path/unmodified.txt'),
                ('licenses', []),
                ('copyrights', [])
            ]))
        ])

        results = DeltaCode(old, new, {"--all-delta-types": True})

        delta = results.deltas[0]

        delta.status = 'unmodified'

        assert delta.to_dict(results) == expected

    def test_Delta_to_dict_moved(self):
        new = self.get_test_loc('deltacode/delta_to_dict_moved_new.json')
        old = self.get_test_loc('deltacode/delta_to_dict_moved_old.json')

        expected = OrderedDict([
            ('status', 'moved'),
            ('factors', []),
            ('score', 0),
            ('new', OrderedDict([
                ('path', 'moved.txt'),
                ('type', 'file'),
                ('name', 'moved.txt'),
                ('size', 20),
                ('sha1', 'a'),
                ('fingerprint', 'e30cf09443e7878dfed3288886e97542'),
                ('original_path', 'path_new/moved.txt'),
                ('licenses', []),
                ('copyrights', [])
            ])),
            ('old', OrderedDict([
                ('path', 'moved.txt'),
                ('type', 'file'),
                ('name', 'moved.txt'),
                ('size', 20),
                ('sha1', 'a'),
                ('fingerprint', 'e30cf09443e7878dfed3288886e97542'),
                ('original_path', 'path_old/moved.txt'),
                ('licenses', []),
                ('copyrights', [])
            ]))
        ])

        deltacode = DeltaCode(new, old, {})
        delta = deltacode.deltas[0]
        delta.status = 'moved'

        assert delta.to_dict(deltacode) == expected

    def test_Delta_create_object_removed(self):
        new = None
        old = models.File({'path': 'path/removed.txt'})

        delta = deltacode.Delta(0, new, old)
        delta.factors.append('removed')

        assert type(delta.new_file) == type(None)
        assert delta.old_file.path == 'path/removed.txt'
        assert 'removed' in delta.factors
        assert delta.score == 0

    def test_Delta_create_object_added(self):
        new = models.File({'path': 'path/added.txt'})
        old = None

        delta = deltacode.Delta(100, new, old)
        delta.factors.append('added')

        assert delta.new_file.path == 'path/added.txt'
        assert type(delta.old_file) == type(None)
        assert 'added' in delta.factors
        assert delta.score == 100

    def test_Delta_create_object_modified(self):
        new = models.File({'path': 'path/modified.txt', 'sha1': 'a'})
        old = models.File({'path': 'path/modified.txt', 'sha1': 'b'})

        delta = deltacode.Delta(20, new, old)
        delta.factors.append('modified')

        assert delta.new_file.path == 'path/modified.txt'
        assert delta.new_file.sha1 == 'a'
        assert delta.old_file.path == 'path/modified.txt'
        assert delta.old_file.sha1 == 'b'
        assert 'modified' in delta.factors
        assert delta.score == 20

    def test_Delta_create_object_unmodified(self):
        new = models.File({'path': 'path/unmodified.txt', 'sha1': 'a'})
        old = models.File({'path': 'path/unmodified.txt', 'sha1': 'a'})

        delta = deltacode.Delta(0, new, old)
        delta.factors.append('unmodified')

        assert delta.new_file.path == 'path/unmodified.txt'
        assert delta.new_file.sha1 == 'a'
        assert delta.old_file.path == 'path/unmodified.txt'
        assert delta.old_file.sha1 == 'a'
        assert 'unmodified' in delta.factors
        assert delta.score == 0

    def test_Delta_create_object_moved(self):
        new = models.File({'path': 'path_new/moved.txt', 'sha1': 'a'})
        old = models.File({'path': 'path_old/moved.txt', 'sha1': 'a'})

        delta = deltacode.Delta(0, new, old)
        delta.factors.append('moved')

        assert delta.new_file.path == 'path_new/moved.txt'
        assert delta.new_file.sha1 == 'a'
        assert delta.old_file.path == 'path_old/moved.txt'
        assert delta.old_file.sha1 == 'a'
        assert 'moved' in delta.factors
        assert delta.score == 0

    def test_Delta_create_object_empty(self):
        delta = deltacode.Delta()

        assert type(delta.new_file) == type(None)
        assert type(delta.old_file) == type(None)
        assert delta.factors == []

    def test_score_new_no_lic_info(self):
        new_scan = self.get_test_loc(
            'deltacode/score_new_no_lic_info_new.json')
        old_scan = self.get_test_loc(
            'deltacode/score_new_no_lic_info_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.old_file.sha1 for d in deltas_object if get_aligned_path(
            d, d.old_file.path, new_file=False) == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == [35]
        assert [d.factors for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'].pop() == ['license info removed']
        assert [d.status for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == ['modified']
        assert [d.to_dict(deltacode_object).get('old').get('licenses') for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'mit'),
                ('score', 50.0),
                ('short_name', None),
                ('category', None),
                ('owner', None)
            ])
        ]
        assert [d.to_dict(deltacode_object).get('new').get('licenses') for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'].pop() == []

    def test_score_old_no_lic_info(self):
        new_scan = self.get_test_loc(
            'deltacode/score_old_no_lic_info_new.json')
        old_scan = self.get_test_loc(
            'deltacode/score_old_no_lic_info_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.old_file.sha1 for d in deltas_object if get_aligned_path(
            d, d.old_file.path, new_file=False) == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == [40]
        assert [d.factors for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'].pop() == ['license info added', 'permissive added']
        assert [d.status for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == ['modified']
        assert [d.to_dict(deltacode_object).get('old').get('licenses') for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'].pop() == []
        assert [d.to_dict(deltacode_object).get('new').get('licenses') for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'mit'),
                ('score', 50.0),
                ('short_name', 'MIT License'),
                ('category', 'Permissive'),
                ('owner', None)
            ])
        ]

    def test_score_multiple_lic_keys(self):
        new_scan = self.get_test_loc(
            'deltacode/score_multiple_lic_keys_new.json')
        old_scan = self.get_test_loc(
            'deltacode/score_multiple_lic_keys_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.old_file.sha1 for d in deltas_object if get_aligned_path(
            d, d.old_file.path, new_file=False) == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == [50]
        assert [d.factors for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'].pop() == ['license change', 'copyleft added']
        assert [d.status for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == ['modified']
        assert [d.to_dict(deltacode_object).get('old').get('licenses') for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'mit'),
                ('score', 50.0),
                ('short_name', 'MIT License'),
                ('category', 'Permissive'),
                ('owner', None)
            ])
        ]
        assert [d.to_dict(deltacode_object).get('new').get('licenses') for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'gpl-2.0'),
                ('score', 100.0),
                ('short_name', 'GPL 2.0'),
                ('category', 'Copyleft'),
                ('owner', None)
            ]),
            OrderedDict([
                ('key', 'mit'),
                ('score', 30.0),
                ('short_name', 'MIT License'),
                ('category', 'Permissive'),
                ('owner', None)
            ])
        ]

    def test_score_no_lic_change(self):
        new_scan = self.get_test_loc('deltacode/score_no_lic_change_new.json')
        old_scan = self.get_test_loc('deltacode/score_no_lic_change_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.old_file.sha1 for d in deltas_object if get_aligned_path(
            d, d.old_file.path, new_file=False) == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == [20]
        assert [d.factors for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'].pop() == []
        assert [d.status for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == ['modified']
        assert [d.to_dict(deltacode_object).get('old').get('licenses') for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'mit'),
                ('score', 95.0),
                ('short_name', None),
                ('category', None),
                ('owner', None)
            ])
        ]
        assert [d.to_dict(deltacode_object).get('new').get('licenses') for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'mit'),
                ('score', 95.0),
                ('short_name', None),
                ('category', None),
                ('owner', None)
            ])
        ]

    def test_score_new_multiple_keys_same_lic(self):
        new_scan = self.get_test_loc(
            'deltacode/score_new_multiple_keys_same_lic_new.json')
        old_scan = self.get_test_loc(
            'deltacode/score_new_multiple_keys_same_lic_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.old_file.sha1 for d in deltas_object if get_aligned_path(
            d, d.old_file.path, new_file=False) == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == [20]
        assert [d.factors for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'].pop() == []
        assert [d.status for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == ['modified']
        assert [d.to_dict(deltacode_object).get("old").get("licenses") for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'mit'),
                ('score', 100.0),
                ('short_name', None),
                ('category', None),
                ('owner', None)
            ])
        ]
        assert [d.to_dict(deltacode_object).get('new').get('licenses') for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'mit'),
                ('score', 75.0),
                ('short_name', None),
                ('category', None),
                ('owner', None)
            ]),
            OrderedDict([
                ('key', 'mit'),
                ('score', 90.0),
                ('short_name', None),
                ('category', None),
                ('owner', None)
            ])
        ]

    def test_score_single_copyright_change(self):
        new_scan = self.get_test_loc(
            'deltacode/score_single_copyright_change_new.json')
        old_scan = self.get_test_loc(
            'deltacode/score_single_copyright_change_old.json')
        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas
        assert [d.old_file.sha1 for d in deltas_object if get_aligned_path(
            d, d.old_file.path, new_file=False) == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == [25]
        assert [d.factors for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'].pop() == ['copyright change']
        assert [d.status for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == ['modified']
        assert [d.to_dict(deltacode_object).get('old').get('copyrights') for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'path.txt'].pop() == [
            OrderedDict([
                ('statements', [
                 'Copyright (c) 1995-2005, 2014, 2016 Jean-loup Gailly, Mark Adler']),
                ('holders', ['Jean-loup Gailly, Mark Adler'])
            ])
        ]
        assert [d.to_dict(deltacode_object).get('new').get('copyrights') for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'path.txt'].pop() == [
            OrderedDict([
                ('statements', ['Copyright (c) 2016 Mark Adler']),
                ('holders', ['Mark Adler'])
            ])
        ]
        assert len(deltas_object) == 2
        assert len([i for i in deltas_object if i.score == 30]) == 0
        assert len([i for i in deltas_object if i.score == 25]) == 1
        assert len([i for i in deltas_object if i.score == 20]) == 0

    def test_score_copyright_info_added(self):
        new_scan = self.get_test_loc(
            'deltacode/score_copyright_info_added_new.json')
        old_scan = self.get_test_loc(
            'deltacode/score_copyright_info_added_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.old_file.sha1 for d in deltas_object if get_aligned_path(
            d, d.old_file.path, new_file=False) == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == [30]
        assert [d.factors for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'].pop() == ['copyright info added']
        assert [d.status for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == ['modified']
        assert [d.to_dict(deltacode_object).get('old').get('copyrights') for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'].pop() == []
        assert [d.to_dict(deltacode_object).get('new').get('copyrights') for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'path.txt'].pop() == [
            OrderedDict([
                ('statements', ['Copyright (c) 2016 Mark Adler']),
                ('holders', ['Mark Adler'])
            ])
        ]

        assert len([i for i in deltas_object if i.score == 35]) == 0
        assert len([i for i in deltas_object if i.score == 30]) == 1
        assert len([i for i in deltas_object if i.score == 20]) == 0

    def test_score_copyright_info_removed(self):
        new_scan = self.get_test_loc(
            'deltacode/score_copyright_info_removed_new.json')
        old_scan = self.get_test_loc(
            'deltacode/score_copyright_info_removed_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.old_file.sha1 for d in deltas_object if get_aligned_path(
            d, d.old_file.path, new_file=False) == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == [30]
        assert [d.factors for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'].pop() == ['copyright info removed']
        assert [d.status for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == ['modified']
        assert [d.to_dict(deltacode_object).get('old').get('copyrights') for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'path.txt'].pop() == [
            OrderedDict([
                ('statements', ['Copyright (c) 2016 Mark Adler']),
                ('holders', ['Mark Adler'])
            ])
        ]
        assert [d.to_dict(deltacode_object).get('new').get('copyrights') for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'].pop() == []

        assert len([i for i in deltas_object if i.score == 30]) == 1
        assert len([i for i in deltas_object if i.score == 20]) == 0

    def test_score_no_copyright_info(self):
        new_scan = self.get_test_loc(
            'deltacode/score_no_copyright_info_new.json')
        old_scan = self.get_test_loc(
            'deltacode/score_no_copyright_info_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.old_file.sha1 for d in deltas_object if get_aligned_path(
            d, d.old_file.path, new_file=False) == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == [20]
        assert [d.factors for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'].pop() == []
        assert [d.status for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == ['modified']
        assert [d.to_dict(deltacode_object).get('old').get('copyrights') for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'].pop() == []
        assert [d.to_dict(deltacode_object).get('new').get('copyrights') for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'].pop() == []

        assert len([i for i in deltas_object if i.score == 30]) == 0
        assert len([i for i in deltas_object if i.score == 20]) == 1

    def test_score_no_copyright_changes(self):
        new_scan = self.get_test_loc(
            'deltacode/score_no_copyright_changes_new.json')
        old_scan = self.get_test_loc(
            'deltacode/score_no_copyright_changes_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.old_file.sha1 for d in deltas_object if get_aligned_path(
            d, d.old_file.path, new_file=False) == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == [20]
        assert [d.factors for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'].pop() == []
        assert [d.status for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == ['modified']
        assert [d.to_dict(deltacode_object).get('old').get('copyrights') for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'path.txt'].pop() == [
            OrderedDict([
                ('statements', ['Copyright (c) 2016 Mark Adler']),
                ('holders', ['Mark Adler'])
            ])
        ]
        assert [d.to_dict(deltacode_object).get('new').get('copyrights') for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'path.txt'].pop() == [
            OrderedDict([
                ('statements', ['Copyright (c) 2016 Mark Adler']),
                ('holders', ['Mark Adler'])
            ])
        ]

        assert len([i for i in deltas_object if i.score == 30]) == 0
        assert len([i for i in deltas_object if i.score == 20]) == 1

    def test_score_no_copyright_key(self):
        new_scan = self.get_test_loc(
            'deltacode/score_no_copyright_key_new.json')
        old_scan = self.get_test_loc(
            'deltacode/score_no_copyright_key_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.old_file.sha1 for d in deltas_object if get_aligned_path(
            d, d.old_file.path, new_file=False) == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == [20]
        assert [d.factors for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'].pop() == []
        assert [d.status for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == ['modified']
        assert [d.to_dict(deltacode_object).get('old').get('copyrights') for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'].pop() == []
        assert [d.to_dict(deltacode_object).get('new').get('copyrights') for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'].pop() == []

        assert len([i for i in deltas_object if i.score == 30]) == 0
        assert len([i for i in deltas_object if i.score == 20]) == 1

    def test_score_copyright_and_license_info_added(self):
        new_scan = self.get_test_loc(
            'deltacode/score_copyright_and_license_info_added_new.json')
        old_scan = self.get_test_loc(
            'deltacode/score_copyright_and_license_info_added_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.old_file.sha1 for d in deltas_object if get_aligned_path(
            d, d.old_file.path, new_file=False) == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == [70]
        assert [d.factors for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'path.txt'].pop() == [
            'license info added', 'copyleft added', 'copyright info added']
        assert [d.status for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == ['modified']
        assert [d.to_dict(deltacode_object).get('old').get('copyrights') for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'].pop() == []
        assert [d.to_dict(deltacode_object).get('new').get('copyrights') for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'path.txt'].pop() == [
            OrderedDict([
                ('statements', ['Copyright (c) 2016 Mark Adler']),
                ('holders', ['Mark Adler'])
            ])
        ]
        assert [d.to_dict(deltacode_object).get('old').get('licenses') for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'].pop() == []
        assert [d.to_dict(deltacode_object).get('new').get('licenses') for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'gpl-1.0-plus'),
                ('score', 20.0),
                ('short_name', 'GPL 1.0 or later'),
                ('category', 'Copyleft'),
                ('owner', "Free Software Foundation (FSF)")
            ])
        ]

        assert len([i for i in deltas_object if i.score == 70]) == 1
        assert len([i for i in deltas_object if i.score == 50]) == 0
        assert len([i for i in deltas_object if i.score == 30]) == 0
        assert len([i for i in deltas_object if i.score == 20]) == 0

    def test_score_copyright_and_license_info_removed(self):
        new_scan = self.get_test_loc(
            'deltacode/score_copyright_and_license_info_removed_new.json')
        old_scan = self.get_test_loc(
            'deltacode/score_copyright_and_license_info_removed_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.old_file.sha1 for d in deltas_object if get_aligned_path(
            d, d.old_file.path, new_file=False) == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == [45]
        assert [d.factors for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'path.txt'].pop() == [
            'license info removed', 'copyright info removed']
        assert [d.status for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == ['modified']
        assert [d.to_dict(deltacode_object).get('old').get('copyrights') for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'path.txt'].pop() == [
            OrderedDict([
                ('statements', ['Copyright (c) 2016 Mark Adler']),
                ('holders', ['Mark Adler'])
            ])
        ]
        assert [d.to_dict(deltacode_object).get('new').get('copyrights') for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'].pop() == []
        assert [d.to_dict(deltacode_object).get('old').get('licenses') for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'gpl-1.0-plus'),
                ('score', 20.0),
                ('short_name', 'GPL 1.0 or later'),
                ('category', 'Copyleft'),
                ('owner', "Free Software Foundation (FSF)")
            ])
        ]
        assert [d.to_dict(deltacode_object).get('new').get('licenses') for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'].pop() == []

        assert len([i for i in deltas_object if i.score == 55]) == 0
        assert len([i for i in deltas_object if i.score == 45]) == 1
        assert len([i for i in deltas_object if i.score == 30]) == 0
        assert len([i for i in deltas_object if i.score == 20]) == 0

    def test_score_copyright_info_added_license_info_removed(self):
        new_scan = self.get_test_loc(
            'deltacode/score_copyright_info_added_license_info_removed_new.json')
        old_scan = self.get_test_loc(
            'deltacode/score_copyright_info_added_license_info_removed_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.old_file.sha1 for d in deltas_object if get_aligned_path(
            d, d.old_file.path, new_file=False) == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == [45]
        assert [d.factors for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'path.txt'].pop() == [
            'license info removed', 'copyright info added']
        assert [d.status for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == ['modified']
        assert [d.to_dict(deltacode_object).get('old').get('copyrights') for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'].pop() == []
        assert [d.to_dict(deltacode_object).get('new').get('copyrights') for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'path.txt'].pop() == [
            OrderedDict([
                ('statements', ['Copyright (c) 2016 Mark Adler']),
                ('holders', ['Mark Adler'])
            ])
        ]
        assert [d.to_dict(deltacode_object).get('old').get('licenses') for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'gpl-3.0-plus'),
                ('score', 100.0),
                ('short_name', 'GPL 3.0 or later'),
                ('category', 'Copyleft'),
                ('owner', "Free Software Foundation (FSF)")
            ])
        ]
        assert [d.to_dict(deltacode_object).get('new').get('licenses') for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'].pop() == []

        assert len([i for i in deltas_object if i.score == 55]) == 0
        assert len([i for i in deltas_object if i.score == 50]) == 0
        assert len([i for i in deltas_object if i.score == 45]) == 1
        assert len([i for i in deltas_object if i.score == 30]) == 0
        assert len([i for i in deltas_object if i.score == 20]) == 0

    def test_score_license_info_added_copyright_info_removed(self):
        new_scan = self.get_test_loc(
            'deltacode/score_license_info_added_copyright_info_removed_new.json')
        old_scan = self.get_test_loc(
            'deltacode/score_license_info_added_copyright_info_removed_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.old_file.sha1 for d in deltas_object if get_aligned_path(
            d, d.old_file.path, new_file=False) == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == [70]
        assert [d.factors for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'path.txt'].pop() == [
            'license info added', 'copyleft added', 'copyright info removed']
        assert [d.status for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == ['modified']
        assert [d.to_dict(deltacode_object).get('old').get('copyrights') for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'path.txt'].pop() == [
            OrderedDict([
                ('statements', ['Copyright (c) 2016 Mark Adler']),
                ('holders', ['Mark Adler'])
            ])
        ]
        assert [d.to_dict(deltacode_object).get('new').get('copyrights') for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'].pop() == []
        assert [d.to_dict(deltacode_object).get('old').get('licenses') for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'].pop() == []
        assert [d.to_dict(deltacode_object).get('new').get('licenses') for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'gpl-3.0-plus'),
                ('score', 100.0),
                ('short_name', 'GPL 3.0 or later'),
                ('category', 'Copyleft'),
                ('owner', "Free Software Foundation (FSF)")
            ])
        ]

        assert len([i for i in deltas_object if i.score == 70]) == 1
        assert len([i for i in deltas_object if i.score == 50]) == 0
        assert len([i for i in deltas_object if i.score == 45]) == 0
        assert len([i for i in deltas_object if i.score == 30]) == 0
        assert len([i for i in deltas_object if i.score == 20]) == 0

    def test_score_copyright_change_no_license_change(self):
        new_scan = self.get_test_loc(
            'deltacode/score_copyright_change_no_license_change_new.json')
        old_scan = self.get_test_loc(
            'deltacode/score_copyright_change_no_license_change_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.old_file.sha1 for d in deltas_object if get_aligned_path(
            d, d.old_file.path, new_file=False) == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == [25]
        assert [d.factors for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'].pop() == ['copyright change']
        assert [d.status for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == ['modified']
        assert [d.to_dict(deltacode_object).get('old').get('copyrights') for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'path.txt'].pop() == [
            OrderedDict([
                ('statements', ['Copyright (c) 2016 Mark Adler']),
                ('holders', ['Mark Adler'])
            ])
        ]
        assert [d.to_dict(deltacode_object).get('new').get('copyrights') for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'path.txt'].pop() == [
            OrderedDict([
                ('statements', ['Copyright (c) 2016 Alfred E. Neuman']),
                ('holders', ['Alfred E. Neuman'])
            ])
        ]
        assert [d.to_dict(deltacode_object).get('old').get('licenses') for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'gpl-3.0-plus'),
                ('score', 100.0),
                ('short_name', 'GPL 3.0 or later'),
                ('category', 'Copyleft'),
                ('owner', "Free Software Foundation (FSF)")
            ])
        ]
        assert [d.to_dict(deltacode_object).get('new').get('licenses') for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'gpl-3.0-plus'),
                ('score', 100.0),
                ('short_name', 'GPL 3.0 or later'),
                ('category', 'Copyleft'),
                ('owner', "Free Software Foundation (FSF)")
            ])
        ]

        assert len([i for i in deltas_object if i.score == 30]) == 0
        assert len([i for i in deltas_object if i.score == 25]) == 1
        assert len([i for i in deltas_object if i.score == 20]) == 0

    def test_score_license_change_no_copyright_change(self):
        new_scan = self.get_test_loc(
            'deltacode/score_license_change_no_copyright_change_new.json')
        old_scan = self.get_test_loc(
            'deltacode/score_license_change_no_copyright_change_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.old_file.sha1 for d in deltas_object if get_aligned_path(
            d, d.old_file.path, new_file=False) == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == [30]
        assert [d.factors for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'].pop() == ['license change']
        assert [d.status for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == ['modified']
        assert [d.to_dict(deltacode_object).get('old').get('copyrights') for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'path.txt'].pop() == [
            OrderedDict([
                ('statements', ['Copyright (c) 2016 Mark Adler']),
                ('holders', ['Mark Adler'])
            ])
        ]
        assert [d.to_dict(deltacode_object).get('new').get('copyrights') for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'path.txt'].pop() == [
            OrderedDict([
                ('statements', ['Copyright (c) 2016 Mark Adler']),
                ('holders', ['Mark Adler'])
            ])
        ]
        assert [d.to_dict(deltacode_object).get('old').get('licenses') for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'gpl-3.0-plus'),
                ('score', 100.0),
                ('short_name', 'GPL 3.0 or later'),
                ('category', 'Copyleft'),
                ('owner', "Free Software Foundation (FSF)")
            ])
        ]
        assert [d.to_dict(deltacode_object).get('new').get('licenses') for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'gpl-1.0-plus'),
                ('score', 20.0),
                ('short_name', 'GPL 1.0 or later'),
                ('category', 'Copyleft'),
                ('owner', "Free Software Foundation (FSF)")
            ])
        ]

        assert len([i for i in deltas_object if i.score == 30]) == 1
        assert len([i for i in deltas_object if i.score == 25]) == 0
        assert len([i for i in deltas_object if i.score == 20]) == 0

    def test_Delta_update_added(self):
        new = models.File({
            'path': 'path/added.txt',
            'type': 'file',
            'name': 'added.txt',
            'size': 20,
            'sha1': 'a',
            'original_path': ''
        })

        delta = deltacode.Delta(100, new, None)

        delta.update(25, 'This is a test of an added file')

        assert delta.score == 125
        assert delta.factors == ['This is a test of an added file']

    def test_Delta_update_modified(self):
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

        delta = deltacode.Delta(20, new, old)

        delta.update(25, 'This is a test of a modified file')

        assert delta.score == 45
        assert delta.factors == ['This is a test of a modified file']

    def test_Delta_update_license_change_no_copyright_change(self):
        new_scan = self.get_test_loc(
            'deltacode/score_license_change_no_copyright_change_new.json')
        old_scan = self.get_test_loc(
            'deltacode/score_license_change_no_copyright_change_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.score for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == [30]
        assert [d.factors for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'].pop() == ['license change']
        assert [d.status for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == ['modified']

        for d in deltas_object:
            if get_aligned_path(d, d.new_file.path, new_file=True) == 'path.txt':
                d.update(25, 'This is a test of a license change')

        assert [d.score for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == [55]
        assert [d.factors for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'path.txt'].pop() == [
            'license change', 'This is a test of a license change']
        assert [d.status for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'path.txt'] == ['modified']

    def test_Delta_to_dict_multiple_copyright_statements_and_holders(self):
        new = self.get_test_loc(
            'deltacode/delta_to_dict_multiple_copyright_statements_and_holders_new.json')
        old = self.get_test_loc(
            'deltacode/delta_to_dict_multiple_copyright_statements_and_holders_old.json')

        expected = OrderedDict([
            ('status', 'modified'),
            ('factors', ['copyright change',
             'Similar with hamming distance : 5']),
            ('score', 30),
            ('new', OrderedDict([
                ('path', 'path/modified.txt'),
                ('type', 'file'),
                ('name', 'modified.txt'),
                ('size', 21),
                ('sha1', 'a_modified'),
                ('fingerprint', 'e30cf09443e7878dfed3288886e97542'),
                ('original_path', 'path/modified.txt'),
                ('licenses', []),
                ('copyrights', [OrderedDict([
                    ('statements', [
                        'Copyright (c) 1995-2005, 2014, 2016 Jean-loup Gailly, Mark Adler',
                        'Copyright (c) 1998 by Andreas R. Kleinert',
                        'Copyright (c) 2002-2004 Dmitriy Anisimkov',
                        'Copyright (c) 1998, 2007 Brian Raiter',
                        'Copyright (c) 1997,99 Borland Corp.',
                        '(c) Copyright Henrik Ravn 2004',
                        'Copyright (c) 1995-2010 Jean-loup Gailly, Brian Raiter and Gilles Vollant.',
                        'Copyright (c) 2003 Chris Anderson',
                        'Copyright (c) 1997 Christian Michelsen Research as Advanced Computing',
                        'Copyright (c) 2009-2010 Mathias Svensson http://result42.com',
                        'Copyright (c) 1990-2000 Info-ZIP.',
                        'Copyright (c) 1995-2005, 2014, 2016 Jean-loup Gailly, Mark Adler',
                        'Copyright (c) 1998 by Andreas R. Kleinert',
                        'Copyright (c) 2002-2004 Dmitriy Anisimkov',
                        'Copyright (c) 1998, 2007 Brian Raiter',
                        'Copyright (c) 1997,99 Borland Corp.',
                        '(c) Copyright Henrik Ravn 2004',
                        'Copyright (c) 1995-2010 Jean-loup Gailly, Brian Raiter and Gilles Vollant.',
                        'Copyright (c) 2003 Chris Anderson',
                        'Copyright (c) 1997 Christian Michelsen Research as Advanced Computing',
                        'Copyright (c) 2009-2010 Mathias Svensson http://result42.com',
                        'Copyright (c) 1990-2000 Info-ZIP.'
                    ]),
                    ('holders', [
                        'Jean-loup Gailly, Mark Adler',
                        'Andreas R. Kleinert',
                        'Dmitriy Anisimkov',
                        'Brian Raiter',
                        'Borland Corp.',
                        'Henrik Ravn',
                        'Jean-loup Gailly, Brian Raiter, Gilles Vollant',
                        'Chris Anderson',
                        'Christian Michelsen Research as Advanced Computing',
                        'Mathias Svensson',
                        'Info-ZIP',
                        'Jean-loup Gailly, Mark Adler',
                        'Andreas R. Kleinert',
                        'Dmitriy Anisimkov',
                        'Brian Raiter',
                        'Borland Corp.',
                        'Henrik Ravn',
                        'Jean-loup Gailly, Brian Raiter, Gilles Vollant',
                        'Chris Anderson',
                        'Christian Michelsen Research as Advanced Computing',
                        'Mathias Svensson',
                        'Info-ZIP'
                    ])])
                ])
            ])),
            ('old', OrderedDict([
                ('path', 'path/modified.txt'),
                ('type', 'file'),
                ('name', 'modified.txt'),
                ('size', 20),
                ('sha1', 'a'),
                ('fingerprint', 'e30cf09443e7878dfed3289786e97542'),
                ('original_path', 'path/modified.txt'),
                ('licenses', []),
                ('copyrights', [OrderedDict([
                    ('statements', [
                        'Copyright (c) 2018 Jane Doe'
                    ]),
                    ('holders', [
                        'Jane Doe'
                    ])])
                ])
            ]))
        ])

        results = DeltaCode(new, old, {})

        delta = results.deltas[0]

        assert delta.to_dict(results) == expected

    def test_Delta_to_dict_Copyright_unusual_characters(self):
        new_scan = self.get_test_loc(
            'deltacode/scan_unusual_characters_new.json')
        old_scan = self.get_test_loc(
            'deltacode/scan_unusual_characters_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.factors for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'a1.py'].pop() == [
            'license change', 'copyleft added', 'copyright change']
        assert [d.status for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'a1.py'] == ['modified']

        holders_list = [c["holders"].pop() for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'a1.py' for c in d.new_file.copyrights]

        assert 'Francois Hennebique and others.' in holders_list
        assert 'Ottomar Anschutz.' in holders_list
        assert 'Christiane Nusslein-Volhard.' in holders_list
        assert 'Behram Kursunoglu.' in holders_list

        statements_list = [c["statements"].pop() for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'a1.py' for c in d.new_file.copyrights]

        assert 'Copyright (c) 2017-2018 Francois Hennebique and others.' in statements_list
        assert 'Copyright (c) 1999 Ottomar Anschutz.' in statements_list
        assert 'Copyright (c) 2015-18 Christiane Nusslein-Volhard.' in statements_list
        assert 'Copyright (c) 1999 Behram Kursunoglu.' in statements_list

        assert [d.score for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'a1.py'] == [55]
        assert [d.score for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'a2.py'] == [0]

    def test_DeltaCode_sort_order(self):
        new_scan = self.get_test_loc('deltacode/scan_sorted01_new.json')
        old_scan = self.get_test_loc('deltacode/scan_sorted01_old.json')

        options = OrderedDict([
            ('--all-delta-types', True)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        expected = [
            ['license info added', 'permissive added', 'copyright info added'],
            ['copyright info added'],
            ['license change'],
            [],
        ]

        unexpected = [
            ['license change'],
            ['copyright info added'],
            ['license info added'],
            [],
        ]

        factors = [d.factors for d in deltas_object]
        assert factors == expected
        assert factors != unexpected

    def test_DeltaCode_no_lic_to_all_notable_lic(self):
        new_scan = self.get_test_loc(
            'deltacode/no_lic_to_all_notable_lic_new.json')
        old_scan = self.get_test_loc(
            'deltacode/no_lic_to_all_notable_lic_old.json')

        options = OrderedDict([
            ('--all-delta-types', True)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.score for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'a1.py'] == [170]
        assert [d.score for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'a2.py'] == [0]

        assert sorted([d.factors for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'a1.py'].pop()) == sorted(['license info added', 'commercial added',
                                                                                                                                             'copyleft added', 'copyleft limited added', 'free restricted added', 'patent license added', 'permissive added', 'proprietary free added', 'copyright info added'])
        assert [d.status for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'a1.py'] == ['modified']
        assert [d.factors for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'a2.py'].pop() == []
        assert [d.status for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'a2.py'] == ['unmodified']

    def test_DeltaCode_apache_to_all_notable_lic(self):
        new_scan = self.get_test_loc(
            'deltacode/apache_to_all_notable_lic_new.json')
        old_scan = self.get_test_loc(
            'deltacode/apache_to_all_notable_lic_old.json')

        options = OrderedDict([
            ('--all-delta-types', True)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.score for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'a1.py'] == [155]
        assert [d.score for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'a2.py'] == [0]

        assert sorted([d.factors for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True) == 'a1.py'].pop()) == sorted(
            ['license change', 'commercial added', 'copyleft added', 'copyleft limited added', 'free restricted added', 'patent license added', 'proprietary free added', 'copyright change'])
        assert [d.status for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'a1.py'] == ['modified']
        assert [d.factors for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'a2.py'].pop() == []
        assert [d.status for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'a2.py'] == ['unmodified']

    def test_DeltaCode_copyleft_etc_to_prop_free_and_commercial(self):
        new_scan = self.get_test_loc(
            'deltacode/copyleft_etc_to_prop_free_and_commercial_new.json')
        old_scan = self.get_test_loc(
            'deltacode/copyleft_etc_to_prop_free_and_commercial_old.json')

        options = OrderedDict([
            ('--all-delta-types', True)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.score for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'a1.py'] == [50]
        assert [d.score for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'a2.py'] == [0]

        assert sorted([d.factors for d in deltas_object if get_aligned_path(d, d.new_file.path, new_file=True)
                      == 'a1.py'].pop()) == sorted(['license change', 'commercial added', 'proprietary free added'])
        assert [d.status for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'a1.py'] == ['modified']
        assert [d.factors for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'a2.py'].pop() == []
        assert [d.status for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'a2.py'] == ['unmodified']

    def test_DeltaCode_permissive_add_public_domain(self):
        new_scan = self.get_test_loc(
            'deltacode/permissive_add_public_domain_new.json')
        old_scan = self.get_test_loc(
            'deltacode/permissive_add_public_domain_old.json')

        options = OrderedDict([
            ('--all-delta-types', True)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.score for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'a1.py'] == [30]
        assert [d.score for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'a2.py'] == [0]

        assert [d.factors for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'a1.py'].pop() == ['license change', 'public domain added']
        assert [d.status for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'a1.py'] == ['modified']
        assert [d.factors for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'a2.py'].pop() == []
        assert [d.status for d in deltas_object if get_aligned_path(
            d, d.new_file.path, new_file=True) == 'a2.py'] == ['unmodified']

    def test_Stat_calculation_and_ordering(self):
        new_scan = self.get_test_loc('deltacode/all_stat_order_check_new.json')
        old_scan = self.get_test_loc('deltacode/all_stat_order_check_old.json')

        options = OrderedDict([
            ('--all-delta-types', True)
        ])

        expected = OrderedDict([
            ('old_files_count', 7),
            ('new_files_count', 6),
            ('percent_added', 28.57),
            ('percent_removed', 42.86),
            ('percent_moved', 14.29),
            ('percent_modified', 14.29),
            ('percent_unmodified', 28.57)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        stats_object = deltacode_object.stats.to_dict()

        assert stats_object == expected

    def test_similarity_matching_1(self):
        old_file = self.get_test_loc('deltacode/coala-0.7.0-old.json')
        new_file = self.get_test_loc('deltacode/coala-0.10.0-new.json')
        result_file = self.get_temp_file('json')
        args = ['--new', new_file, '--old', old_file,
                '--json-file', result_file, '--all-delta-types']
        test_utils.run_scan_click(args)
        test_utils.check_json_scan(self.get_test_loc(
            'deltacode/coala-expected-result.json'), result_file, regen=False)

    def test_similarity_matching_2(self):
        old_file = self.get_test_loc('deltacode/sugar-0.108.0-old.json')
        new_file = self.get_test_loc('deltacode/sugar-0.114-new.json')
        result_file = self.get_temp_file('json')
        args = ['--new', new_file, '--old', old_file,
                '--json-file', result_file, '--all-delta-types']
        test_utils.run_scan_click(args)
        test_utils.check_json_scan(self.get_test_loc(
            'deltacode/sugar-expected.json'), result_file, regen=False)

    @pytest.mark.xfail(reason='Ambiguous test case')
    def test_non_similarity_matching_1(self):
        old_file = self.get_test_loc('deltacode/coala-0.7.0-old.json')
        new_file = self.get_test_loc('deltacode/sugar-0.114-new.json')
        result_file = self.get_temp_file('json')
        args = ['--new', new_file, '--old', old_file,
                '--json-file', result_file, '--all-delta-types']
        test_utils.run_scan_click(args)
        test_utils.check_json_scan(self.get_test_loc(
            'deltacode/sugar-coala-expected.json'), result_file, regen=False)

    def test_scancode_options(self):
        old_file = self.get_test_loc('deltacode/scancode_options_old.json')
        new_file = self.get_test_loc('deltacode/scancode_options_new.json')
        result_file = self.get_temp_file('json')
        args = ['--new', new_file, '--old', old_file,
                '--json-file', result_file, '--all-delta-types']
        test_utils.run_scan_click(args)
        test_utils.check_json_scan(self.get_test_loc(
            'deltacode/scancode_options_expected.json'), result_file, regen=False)
