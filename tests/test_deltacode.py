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

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        delta = DeltaCode(None, None, options)

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

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        result = DeltaCode(new_scan, old_scan, options)

        assert result.new.files_count == 11408
        assert result.old.files_count == 8631

    def test_DeltaCode_align_scan_zlib_alignment_exception(self):
        new_scan = self.get_test_loc('deltacode/align-scan-zlib-alignment-exception-new.json')
        # Our old scan uses --full-root option in scancode
        old_scan = self.get_test_loc('deltacode/align-scan-zlib-alignment-exception-old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        results = DeltaCode(new_scan, old_scan, options)

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

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        result = DeltaCode(new_scan, old_scan, options)

        # Modifiy files_count value to raise the error.
        # This should never happen in reality.
        result.new.files_count = 42
        result.old.files_count = 40

        result.determine_delta()
        assert result.errors == [
            'Deltacode Error: Number of visited files(43) does not match total_files(42) in the new scan',
            'Deltacode Error: Number of visited files(43) does not match total_files(40) in the old scan'
        ]

    def test_DeltaCode_invalid_paths(self):
        test_path_1 = '/some/invalid/path/1.json'
        test_path_2 = '/some/invalid/path/2.json'

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        result = DeltaCode(test_path_1, test_path_2, options)

        assert result.new.path == ''
        assert result.new.files_count == 0
        assert result.new.files == []

        assert result.old.path == ''
        assert result.old.files_count == 0
        assert result.old.files == []

        assert result.deltas == []

    def test_DeltaCode_empty_paths(self):
        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        result = DeltaCode('', '', options)

        assert result.new.path == ''
        assert result.new.files_count == 0
        assert result.new.files == []

        assert result.old.path == ''
        assert result.old.files_count == 0
        assert result.old.files == []

        assert result.deltas == []

    def test_DeltaCode_None_paths(self):
        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        result = DeltaCode(None, None, options)

        assert result.new.path == ''
        assert result.new.files_count == 0
        assert result.new.files == []

        assert result.old.path == ''
        assert result.old.files_count == 0
        assert result.old.files == []

        assert result.deltas == []

    def test_Delta_one_None(self):
        file_obj = models.File({'path': 'fake/path.txt'})

        first_None = deltacode.Delta(10, None, file_obj)
        second_None = deltacode.Delta(100, file_obj, None)

        assert first_None.score == 10
        assert second_None.score == 100

        assert first_None.factors == []
        assert second_None.factors == []

        expected_first = OrderedDict([
            ('factors', []),
            ('score', 10),
            ('new', None),
            ('old', OrderedDict([
                ('path', 'fake/path.txt'),
                ('type', ''),
                ('name', ''),
                ('size', ''),
                ('sha1', ''),
                ('original_path', '')
            ]))
        ])

        expected_second = OrderedDict([
            ('factors', []),
            ('score', 100),
            ('new', OrderedDict([
                ('path', 'fake/path.txt'),
                ('type', ''),
                ('name', ''),
                ('size', ''),
                ('sha1', ''),
                ('original_path', '')
            ])),
            ('old', None)
        ])

        assert first_None.to_dict() == expected_first
        assert second_None.to_dict() == expected_second

    def test_Delta_None_files(self):
        delta = deltacode.Delta(None, None, None)

        assert type(delta.new_file) == type(None)
        assert type(delta.old_file) == type(None)
        assert delta.score == None
        assert delta.factors == []
        assert delta.to_dict() == OrderedDict([('factors', []), ('score', None), ('new', None), ('old', None)])

    def test_DeltaCode_license_modified_low_score(self):
        new_scan = self.get_test_loc('deltacode/scan_modified_new_license_added_low_score.json')
        old_scan = self.get_test_loc('deltacode/scan_modified_old_license_added_low_score.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        result = DeltaCode(new_scan, old_scan, options)

        deltas = result.deltas

        assert len([i for i in deltas if i.score == 30]) == 0
        assert len([i for i in deltas if i.score == 20]) == 2

        assert [d.score for d in deltas if d.new_file.path == 'some/path/a/a1.py'] == [20]
        assert [d.score for d in deltas if d.new_file.path == 'some/path/b/b1.py'] == [20]

    def test_DeltaCode_license_modified(self):
        new_scan = self.get_test_loc('deltacode/scan_modified_new_license_added.json')
        old_scan = self.get_test_loc('deltacode/scan_modified_old_license_added.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        result = DeltaCode(new_scan, old_scan, options)

        deltas = result.deltas

        assert len([i for i in deltas if i.score == 30]) == 2
        assert len([i for i in deltas if i.score == 20]) == 1

    def test_DeltaCode_no_license_key_value(self):
        new_scan = self.get_test_loc('deltacode/scan_modified_new_no_license_key.json')
        old_scan = self.get_test_loc('deltacode/scan_modified_old_no_license_key.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        result = DeltaCode(new_scan, old_scan, options)

        deltas = result.deltas

        assert len([i for i in deltas if i.score == 30]) == 0
        assert len([i for i in deltas if i.score == 20]) == 2

    def test_DeltaCode_no_license_changes(self):
        new_scan = self.get_test_loc('deltacode/scan_modified_new_no_license_changes.json')
        old_scan = self.get_test_loc('deltacode/scan_modified_old_no_license_changes.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        result = DeltaCode(new_scan, old_scan, options)

        deltas = result.deltas

        assert len([i for i in deltas if i.score == 30]) == 0
        assert len([i for i in deltas if i.score == 20]) == 2

    def test_DeltaCode_errors_empty(self):
        new_scan = self.get_test_loc('deltacode/scan_1_file_moved_new.json')
        old_scan = self.get_test_loc('deltacode/scan_1_file_moved_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        result = DeltaCode(new_scan, old_scan, options)

        assert result.errors == []

    def test_Delta_modified_license_added(self):
        new_scan = self.get_test_loc('deltacode/scan_modified_new_license_added.json')
        old_scan = self.get_test_loc('deltacode/scan_modified_old_license_added.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        result = DeltaCode(new_scan, old_scan, options)

        deltas = result.deltas

        assert [d.score for d in deltas if d.new_file.path == 'some/path/a/a1.py'] == [30]
        assert [d.score for d in deltas if d.new_file.path == 'some/path/b/b1.py'] == [30]
        assert [d.score for d in deltas if d.new_file.path == 'some/path/c/c1.py'] == [20]

    def test_Delta_modified_license_added_low_score(self):
        new_scan = self.get_test_loc('deltacode/scan_modified_new_license_added_low_score.json')
        old_scan = self.get_test_loc('deltacode/scan_modified_old_license_added_low_score.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        result = DeltaCode(new_scan, old_scan, options)

        deltas = result.deltas

        assert [d.score for d in deltas if d.new_file.path == 'some/path/a/a1.py'] == [20]
        assert [d.score for d in deltas if d.new_file.path == 'some/path/b/b1.py'] == [20]

    def test_Delta_modified_no_license_changes(self):
        new_scan = self.get_test_loc('deltacode/scan_modified_new_no_license_changes.json')
        old_scan = self.get_test_loc('deltacode/scan_modified_old_no_license_changes.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        result = DeltaCode(new_scan, old_scan, options)

        deltas = result.deltas

        assert [d.score for d in deltas if d.new_file.path == 'some/path/a/a1.py'] == [20]
        assert [d.score for d in deltas if d.new_file.path == 'some/path/b/b1.py'] == [20]

    def test_Delta_modified_no_license_key(self):
        new_scan = self.get_test_loc('deltacode/scan_modified_new_no_license_key.json')
        old_scan = self.get_test_loc('deltacode/scan_modified_old_no_license_key.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        result = DeltaCode(new_scan, old_scan, options)

        deltas = result.deltas

        assert [d.score for d in deltas if d.new_file.path == 'some/path/a/a1.py'] == [20]
        assert [d.score for d in deltas if d.new_file.path == 'some/path/b/b1.py'] == [20]

    def test_Delta_to_dict_removed(self):
        old = models.File({
            'path': 'path/removed.txt',
            'type': 'file',
            'name': 'removed.txt',
            'size': 20,
            'sha1': 'a',
            'original_path': ''
        })

        expected = OrderedDict([
            ('factors', ['removed']),
            ('score', 10),
            ('new', None),
            ('old', OrderedDict([
                ('path', 'path/removed.txt'),
                ('type', 'file'),
                ('name', 'removed.txt'),
                ('size', 20),
                ('sha1', 'a'),
                ('original_path', '')
            ]))
        ])

        delta = deltacode.Delta(10, None, old)
        delta.factors.append('removed')

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

        expected = OrderedDict([
            ('factors', ['added']),
            ('score', 100),
            ('new', OrderedDict([
                ('path', 'path/added.txt'),
                ('type', 'file'),
                ('name', 'added.txt'),
                ('size', 20),
                ('sha1', 'a'),
                ('original_path', '')
            ])),
            ('old', None)
        ])

        delta = deltacode.Delta(100, new, None)
        delta.factors.append('added')

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

        expected = OrderedDict([
            ('factors', ['modified']),
            ('score', 20),
            ('new', OrderedDict([
                ('path', 'path/modified.txt'),
                ('type', 'file'),
                ('name', 'modified.txt'),
                ('size', 20),
                ('sha1', 'a'),
                ('original_path', '')
            ])),
            ('old', OrderedDict([
                ('path', 'path/modified.txt'),
                ('type', 'file'),
                ('name', 'modified.txt'),
                ('size', 21),
                ('sha1', 'b'),
                ('original_path', '')
            ]))
        ])

        delta = deltacode.Delta(20, new, old)
        delta.factors.append('modified')

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

        expected = OrderedDict([
            ('factors', ['unmodified']),
            ('score', 0),
            ('new', OrderedDict([
                ('path', 'path/unmodified.txt'),
                ('type', 'file'),
                ('name', 'unmodified.txt'),
                ('size', 20),
                ('sha1', 'a'),
                ('original_path', '')
            ])),
            ('old', OrderedDict([
                ('path', 'path/unmodified.txt'),
                ('type', 'file'),
                ('name', 'unmodified.txt'),
                ('size', 20),
                ('sha1', 'a'),
                ('original_path', '')
            ]))
        ])

        delta = deltacode.Delta(0, new, old)
        delta.factors.append('unmodified')

        assert delta.to_dict() == expected

    def test_Delta_to_dict_moved(self):
        new = models.File({
            'path': 'path_new/moved.txt',
            'type': 'file',
            'name': 'moved.txt',
            'size': 20,
            'sha1': 'a',
            'original_path': ''
        })
        old = models.File({
            'path': 'path_old/moved.txt',
            'type': 'file',
            'name': 'moved.txt',
            'size': 20,
            'sha1': 'a',
            'original_path': ''
        })

        expected = OrderedDict([
            ('factors', ['moved']),
            ('score', 0),
            ('new', OrderedDict([
                ('path', 'path_new/moved.txt'),
                ('type', 'file'),
                ('name', 'moved.txt'),
                ('size', 20),
                ('sha1', 'a'),
                ('original_path', '')
            ])),
            ('old', OrderedDict([
                ('path', 'path_old/moved.txt'),
                ('type', 'file'),
                ('name', 'moved.txt'),
                ('size', 20),
                ('sha1', 'a'),
                ('original_path', '')
            ]))
        ])

        delta = deltacode.Delta(0, new, old)
        delta.factors.append('moved')

        assert delta.to_dict() == expected

    def test_Delta_to_dict_empty(self):
        delta = deltacode.Delta()

        assert delta.to_dict() == OrderedDict([
            ('factors', []),
            ('score', 0),
            ('new', None),
            ('old', None)
        ])

    def test_Delta_create_object_removed(self):
        new = None
        old = models.File({'path': 'path/removed.txt'})

        delta = deltacode.Delta(10, new, old)
        delta.factors.append('removed')

        assert type(delta.new_file) == type(None)
        assert delta.old_file.path == 'path/removed.txt'
        assert 'removed' in delta.factors
        assert delta.score == 10

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
        new_scan = self.get_test_loc('deltacode/score_new_no_lic_info_new.json')
        old_scan = self.get_test_loc('deltacode/score_new_no_lic_info_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.score for d in deltas_object if d.new_file.path == 'default.txt'] == [0]
        assert [d.factors for d in deltas_object if d.new_file.path == 'default.txt'].pop() == ['unmodified']
        assert [d.to_dict().get('old').get('licenses') for d in deltas_object if d.new_file.path == 'default.txt'].pop() == None
        assert [d.to_dict().get('new').get('licenses') for d in deltas_object if d.new_file.path == 'default.txt'].pop() == None

        assert [d.old_file.sha1 for d in deltas_object if d.old_file.path == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if d.new_file.path == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if d.new_file.path == 'path.txt'] == [35]
        assert [d.factors for d in deltas_object if d.new_file.path == 'path.txt'].pop() == ['modified', 'license info removed']
        assert [d.to_dict().get('old').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'mit'),
                ('score', 50.0),
                ('short_name', None),
                ('category', None),
                ('owner', None)
            ])
        ]
        assert [d.to_dict().get('new').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == None

    def test_score_new_no_lic_info_below_cutoff_score(self):
        new_scan = self.get_test_loc('deltacode/score_new_no_lic_info_below_cutoff_score_new.json')
        old_scan = self.get_test_loc('deltacode/score_new_no_lic_info_below_cutoff_score_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.score for d in deltas_object if d.new_file.path == 'default.txt'] == [0]
        assert [d.factors for d in deltas_object if d.new_file.path == 'default.txt'].pop() == ['unmodified']
        assert [d.to_dict().get('old').get('licenses') for d in deltas_object if d.new_file.path == 'default.txt'].pop() == None
        assert [d.to_dict().get('new').get('licenses') for d in deltas_object if d.new_file.path == 'default.txt'].pop() == None

        assert [d.old_file.sha1 for d in deltas_object if d.old_file.path == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if d.new_file.path == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if d.new_file.path == 'path.txt'] == [35]
        assert [d.factors for d in deltas_object if d.new_file.path == 'path.txt'].pop() == ['modified', 'license info removed']
        assert [d.to_dict().get('old').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'mit'),
                ('score', 49.0),
                ('short_name', None),
                ('category', None),
                ('owner', None)
            ])
        ]
        assert [d.to_dict().get('new').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == None

    def test_score_old_no_lic_info(self):
        new_scan = self.get_test_loc('deltacode/score_old_no_lic_info_new.json')
        old_scan = self.get_test_loc('deltacode/score_old_no_lic_info_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.score for d in deltas_object if d.new_file.path == 'default.txt'] == [0]
        assert [d.factors for d in deltas_object if d.new_file.path == 'default.txt'].pop() == ['unmodified']
        assert [d.to_dict().get('old').get('licenses') for d in deltas_object if d.new_file.path == 'default.txt'].pop() == None
        assert [d.to_dict().get('new').get('licenses') for d in deltas_object if d.new_file.path == 'default.txt'].pop() == None

        assert [d.old_file.sha1 for d in deltas_object if d.old_file.path == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if d.new_file.path == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if d.new_file.path == 'path.txt'] == [40]
        assert [d.factors for d in deltas_object if d.new_file.path == 'path.txt'].pop() == ['modified', 'license info added']
        assert [d.to_dict().get('old').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == None
        assert [d.to_dict().get('new').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'mit'),
                ('score', 50.0),
                ('short_name', None),
                ('category', None),
                ('owner', None)
            ])
        ]

    def test_score_old_no_lic_info_below_cutoff_score(self):
        new_scan = self.get_test_loc('deltacode/score_old_no_lic_info_below_cutoff_score_new.json')
        old_scan = self.get_test_loc('deltacode/score_old_no_lic_info_below_cutoff_score_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.score for d in deltas_object if d.new_file.path == 'default.txt'] == [0]
        assert [d.factors for d in deltas_object if d.new_file.path == 'default.txt'].pop() == ['unmodified']
        assert [d.to_dict().get('old').get('licenses') for d in deltas_object if d.new_file.path == 'default.txt'].pop() == None
        assert [d.to_dict().get('new').get('licenses') for d in deltas_object if d.new_file.path == 'default.txt'].pop() == None

        assert [d.old_file.sha1 for d in deltas_object if d.old_file.path == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if d.new_file.path == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if d.new_file.path == 'path.txt'] == [40]
        assert [d.factors for d in deltas_object if d.new_file.path == 'path.txt'].pop() == ['modified', 'license info added']
        assert [d.to_dict().get('old').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == None
        assert [d.to_dict().get('new').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'mit'),
                ('score', 49.0),
                ('short_name', None),
                ('category', None),
                ('owner', None)
            ])
        ]

    def test_score_multiple_lic_keys(self):
        new_scan = self.get_test_loc('deltacode/score_multiple_lic_keys_new.json')
        old_scan = self.get_test_loc('deltacode/score_multiple_lic_keys_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.score for d in deltas_object if d.new_file.path == 'default.txt'] == [0]
        assert [d.factors for d in deltas_object if d.new_file.path == 'default.txt'].pop() == ['unmodified']
        assert [d.to_dict().get('old').get('licenses') for d in deltas_object if d.new_file.path == 'default.txt'].pop() == None
        assert [d.to_dict().get('new').get('licenses') for d in deltas_object if d.new_file.path == 'default.txt'].pop() == None

        assert [d.old_file.sha1 for d in deltas_object if d.old_file.path == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if d.new_file.path == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if d.new_file.path == 'path.txt'] == [30]
        assert [d.factors for d in deltas_object if d.new_file.path == 'path.txt'].pop() == ['modified', 'license change']
        assert [d.to_dict().get('old').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'mit'),
                ('score', 50.0),
                ('short_name', None),
                ('category', None),
                ('owner', None)
            ])
        ]
        assert [d.to_dict().get('new').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'gpl-2.0'),
                ('score', 100.0),
                ('short_name', None),
                ('category', None),
                ('owner', None)
            ]),
            OrderedDict([
                ('key', 'mit'),
                ('score', 30.0),
                ('short_name', None),
                ('category', None),
                ('owner', None)
            ])
        ]

    def test_score_new_lic_below_cutoff_score(self):
        new_scan = self.get_test_loc('deltacode/score_new_lic_below_cutoff_score_new.json')
        old_scan = self.get_test_loc('deltacode/score_new_lic_below_cutoff_score_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.score for d in deltas_object if d.new_file.path == 'default.txt'] == [0]
        assert [d.factors for d in deltas_object if d.new_file.path == 'default.txt'].pop() == ['unmodified']
        assert [d.to_dict().get('old').get('licenses') for d in deltas_object if d.new_file.path == 'default.txt'].pop() == None
        assert [d.to_dict().get('new').get('licenses') for d in deltas_object if d.new_file.path == 'default.txt'].pop() == None

        assert [d.old_file.sha1 for d in deltas_object if d.old_file.path == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if d.new_file.path == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if d.new_file.path == 'path.txt'] == [30]
        assert [d.factors for d in deltas_object if d.new_file.path == 'path.txt'].pop() == ['modified', 'license change']
        assert [d.to_dict().get('old').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'mit'),
                ('score', 95.0),
                ('short_name', None),
                ('category', None),
                ('owner', None)
            ])
        ]
        assert [d.to_dict().get('new').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'mit'),
                ('score', 45.0),
                ('short_name', None),
                ('category', None),
                ('owner', None)
            ])
        ]

    def test_score_old_lic_below_cutoff_score(self):
        new_scan = self.get_test_loc('deltacode/score_old_lic_below_cutoff_score_new.json')
        old_scan = self.get_test_loc('deltacode/score_old_lic_below_cutoff_score_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.score for d in deltas_object if d.new_file.path == 'default.txt'] == [0]
        assert [d.factors for d in deltas_object if d.new_file.path == 'default.txt'].pop() == ['unmodified']
        assert [d.to_dict().get('old').get('licenses') for d in deltas_object if d.new_file.path == 'default.txt'].pop() == None
        assert [d.to_dict().get('new').get('licenses') for d in deltas_object if d.new_file.path == 'default.txt'].pop() == None

        assert [d.old_file.sha1 for d in deltas_object if d.old_file.path == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if d.new_file.path == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if d.new_file.path == 'path.txt'] == [30]
        assert [d.factors for d in deltas_object if d.new_file.path == 'path.txt'].pop() == ['modified', 'license change']
        assert [d.to_dict().get('old').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'mit'),
                ('score', 45.0),
                ('short_name', None),
                ('category', None),
                ('owner', None)
            ])
        ]
        assert [d.to_dict().get('new').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'mit'),
                ('score', 95.0),
                ('short_name', None),
                ('category', None),
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

        assert [d.score for d in deltas_object if d.new_file.path == 'default.txt'] == [0]
        assert [d.factors for d in deltas_object if d.new_file.path == 'default.txt'].pop() == ['unmodified']
        assert [d.to_dict().get('old').get('licenses') for d in deltas_object if d.new_file.path == 'default.txt'].pop() == None
        assert [d.to_dict().get('new').get('licenses') for d in deltas_object if d.new_file.path == 'default.txt'].pop() == None

        assert [d.old_file.sha1 for d in deltas_object if d.old_file.path == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if d.new_file.path == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if d.new_file.path == 'path.txt'] == [20]
        assert [d.factors for d in deltas_object if d.new_file.path == 'path.txt'].pop() == ['modified']
        assert [d.to_dict().get('old').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'mit'),
                ('score', 95.0),
                ('short_name', None),
                ('category', None),
                ('owner', None)
            ])
        ]
        assert [d.to_dict().get('new').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'mit'),
                ('score', 95.0),
                ('short_name', None),
                ('category', None),
                ('owner', None)
            ])
        ]

    def test_score_new_multiple_keys_same_lic(self):
        new_scan = self.get_test_loc('deltacode/score_new_multiple_keys_same_lic_new.json')
        old_scan = self.get_test_loc('deltacode/score_new_multiple_keys_same_lic_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.score for d in deltas_object if d.new_file.path == 'default.txt'] == [0]
        assert [d.factors for d in deltas_object if d.new_file.path == 'default.txt'].pop() == ['unmodified']
        assert [d.to_dict().get('old').get('licenses') for d in deltas_object if d.new_file.path == 'default.txt'].pop() == None
        assert [d.to_dict().get('new').get('licenses') for d in deltas_object if d.new_file.path == 'default.txt'].pop() == None

        assert [d.old_file.sha1 for d in deltas_object if d.old_file.path == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if d.new_file.path == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if d.new_file.path == 'path.txt'] == [20]
        assert [d.factors for d in deltas_object if d.new_file.path == 'path.txt'].pop() == ['modified']
        assert [d.to_dict().get('old').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'mit'),
                ('score', 100.0),
                ('short_name', None),
                ('category', None),
                ('owner', None)
            ])
        ]
        assert [d.to_dict().get('new').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
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

    def test_score_multiple_lic_keys_new_below_cutoff_score(self):
        new_scan = self.get_test_loc('deltacode/score_multiple_lic_keys_new_below_cutoff_score_new.json')
        old_scan = self.get_test_loc('deltacode/score_multiple_lic_keys_new_below_cutoff_score_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.score for d in deltas_object if d.new_file.path == 'default.txt'] == [0]
        assert [d.factors for d in deltas_object if d.new_file.path == 'default.txt'].pop() == ['unmodified']
        assert [d.to_dict().get('old').get('licenses') for d in deltas_object if d.new_file.path == 'default.txt'].pop() == None
        assert [d.to_dict().get('new').get('licenses') for d in deltas_object if d.new_file.path == 'default.txt'].pop() == None

        assert [d.old_file.sha1 for d in deltas_object if d.old_file.path == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if d.new_file.path == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if d.new_file.path == 'path.txt'] == [20]
        assert [d.factors for d in deltas_object if d.new_file.path == 'path.txt'].pop() == ['modified']
        assert [d.to_dict().get('old').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'mit'),
                ('score', 100.0),
                ('short_name', None),
                ('category', None),
                ('owner', None)
            ])
        ]
        assert [d.to_dict().get('new').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'gpl-2.0'),
                ('score', 49.9),
                ('short_name', None),
                ('category', None),
                ('owner', None)
            ]),
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

    def test_score_multiple_lic_keys_old_below_cutoff_score(self):
        new_scan = self.get_test_loc('deltacode/score_multiple_lic_keys_old_below_cutoff_score_new.json')
        old_scan = self.get_test_loc('deltacode/score_multiple_lic_keys_old_below_cutoff_score_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.score for d in deltas_object if d.new_file.path == 'default.txt'] == [0]
        assert [d.factors for d in deltas_object if d.new_file.path == 'default.txt'].pop() == ['unmodified']
        assert [d.to_dict().get('old').get('licenses') for d in deltas_object if d.new_file.path == 'default.txt'].pop() == None
        assert [d.to_dict().get('new').get('licenses') for d in deltas_object if d.new_file.path == 'default.txt'].pop() == None

        assert [d.old_file.sha1 for d in deltas_object if d.old_file.path == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if d.new_file.path == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if d.new_file.path == 'path.txt'] == [20]
        assert [d.factors for d in deltas_object if d.new_file.path == 'path.txt'].pop() == ['modified']
        assert [d.to_dict().get('old').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'gpl-2.0'),
                ('score', 49.9),
                ('short_name', None),
                ('category', None),
                ('owner', None)
            ]),
            OrderedDict([
                ('key', 'mit'),
                ('score', 100.0),
                ('short_name', None),
                ('category', None),
                ('owner', None)
            ])
        ]
        assert [d.to_dict().get('new').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
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

    def test_score_single_lic_change(self):
        new_scan = self.get_test_loc('deltacode/score_single_lic_change_new.json')
        old_scan = self.get_test_loc('deltacode/score_single_lic_change_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.score for d in deltas_object if d.new_file.path == 'default.txt'] == [0]
        assert [d.factors for d in deltas_object if d.new_file.path == 'default.txt'].pop() == ['unmodified']
        assert [d.to_dict().get('old').get('licenses') for d in deltas_object if d.new_file.path == 'default.txt'].pop() == None
        assert [d.to_dict().get('new').get('licenses') for d in deltas_object if d.new_file.path == 'default.txt'].pop() == None

        assert [d.old_file.sha1 for d in deltas_object if d.old_file.path == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if d.new_file.path == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if d.new_file.path == 'path.txt'] == [30]
        assert [d.factors for d in deltas_object if d.new_file.path == 'path.txt'].pop() == ['modified', 'license change']
        assert [d.to_dict().get('old').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'mit'),
                ('score', 80.0),
                ('short_name', None),
                ('category', None),
                ('owner', None)
            ])
        ]
        assert [d.to_dict().get('new').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'gpl-2.0'),
                ('score', 70.0),
                ('short_name', None),
                ('category', None),
                ('owner', None)
            ])
        ]
