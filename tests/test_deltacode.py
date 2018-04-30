#
# Copyright (c) 2017-2018 nexB Inc. and others. All rights reserved.
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

        delta.align_scans()

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
            'DeltaCode Warning: new_visited(33) != new_total(42). Assuming old scancode format.',
            'DeltaCode Warning: old_visited(33) != old_total(40). Assuming old scancode format.',
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
                ('original_path', ''),
                ('licenses', []),
                ('copyrights', [])
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
                ('original_path', ''),
                ('licenses', []),
                ('copyrights', [])
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

    def test_DeltaCode_license_modified(self):
        new_scan = self.get_test_loc('deltacode/scan_modified_new_license_added.json')
        old_scan = self.get_test_loc('deltacode/scan_modified_old_license_added.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        result = DeltaCode(new_scan, old_scan, options)

        deltas = result.deltas

        assert len([i for i in deltas if i.score == 50]) == 0
        assert len([i for i in deltas if i.score == 40]) == 0
        assert len([i for i in deltas if i.score == 30]) == 2
        assert len([i for i in deltas if i.score == 20]) == 1

        assert [d.score for d in deltas if d.new_file.path == 'some/path/a/a1.py'] == [30]
        assert [d.score for d in deltas if d.new_file.path == 'some/path/b/b1.py'] == [30]
        assert [d.score for d in deltas if d.new_file.path == 'some/path/c/c1.py'] == [20]

        assert [d.factors for d in deltas if d.new_file.path == 'some/path/a/a1.py'].pop() == ['modified', 'license change']
        assert [d.factors for d in deltas if d.new_file.path == 'some/path/b/b1.py'].pop() == ['modified', 'license change']
        assert [d.factors for d in deltas if d.new_file.path == 'some/path/c/c1.py'].pop() == ['modified']

    def test_DeltaCode_errors_empty(self):
        new_scan = self.get_test_loc('deltacode/scan_1_file_moved_new.json')
        old_scan = self.get_test_loc('deltacode/scan_1_file_moved_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        result = DeltaCode(new_scan, old_scan, options)

        assert result.errors == []

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
            ('score', 0),
            ('new', None),
            ('old', OrderedDict([
                ('path', 'path/removed.txt'),
                ('type', 'file'),
                ('name', 'removed.txt'),
                ('size', 20),
                ('sha1', 'a'),
                ('original_path', ''),
                ('licenses', []),
                ('copyrights', [])
            ]))
        ])

        delta = deltacode.Delta(0, None, old)
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
                ('original_path', ''),
                ('licenses', []),
                ('copyrights', [])
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
                ('original_path', ''),
                ('licenses', []),
                ('copyrights', [])
            ])),
            ('old', OrderedDict([
                ('path', 'path/modified.txt'),
                ('type', 'file'),
                ('name', 'modified.txt'),
                ('size', 21),
                ('sha1', 'b'),
                ('original_path', ''),
                ('licenses', []),
                ('copyrights', [])
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
                ('original_path', ''),
                ('licenses', []),
                ('copyrights', [])
            ])),
            ('old', OrderedDict([
                ('path', 'path/unmodified.txt'),
                ('type', 'file'),
                ('name', 'unmodified.txt'),
                ('size', 20),
                ('sha1', 'a'),
                ('original_path', ''),
                ('licenses', []),
                ('copyrights', [])
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
                ('original_path', ''),
                ('licenses', []),
                ('copyrights', [])
            ])),
            ('old', OrderedDict([
                ('path', 'path_old/moved.txt'),
                ('type', 'file'),
                ('name', 'moved.txt'),
                ('size', 20),
                ('sha1', 'a'),
                ('original_path', ''),
                ('licenses', []),
                ('copyrights', [])
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
        new_scan = self.get_test_loc('deltacode/score_new_no_lic_info_new.json')
        old_scan = self.get_test_loc('deltacode/score_new_no_lic_info_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

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
        assert [d.to_dict().get('new').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == []

    def test_score_old_no_lic_info(self):
        new_scan = self.get_test_loc('deltacode/score_old_no_lic_info_new.json')
        old_scan = self.get_test_loc('deltacode/score_old_no_lic_info_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.old_file.sha1 for d in deltas_object if d.old_file.path == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if d.new_file.path == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if d.new_file.path == 'path.txt'] == [40]
        assert [d.factors for d in deltas_object if d.new_file.path == 'path.txt'].pop() == ['modified', 'license info added']
        assert [d.to_dict().get('old').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == []
        assert [d.to_dict().get('new').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'mit'),
                ('score', 50.0),
                ('short_name', 'MIT License'),
                ('category', 'Permissive'),
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

        assert [d.old_file.sha1 for d in deltas_object if d.old_file.path == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if d.new_file.path == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if d.new_file.path == 'path.txt'] == [30]
        assert [d.factors for d in deltas_object if d.new_file.path == 'path.txt'].pop() == ['modified', 'license change']
        assert [d.to_dict().get('old').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'mit'),
                ('score', 50.0),
                ('short_name', 'MIT License'),
                ('category', 'Permissive'),
                ('owner', None)
            ])
        ]
        assert [d.to_dict().get('new').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
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

    def test_score_single_copyright_change(self):
        new_scan = self.get_test_loc('deltacode/score_single_copyright_change_new.json')
        old_scan = self.get_test_loc('deltacode/score_single_copyright_change_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.old_file.sha1 for d in deltas_object if d.old_file.path == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if d.new_file.path == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if d.new_file.path == 'path.txt'] == [25]
        assert [d.factors for d in deltas_object if d.new_file.path == 'path.txt'].pop() == ['modified', 'copyright change']
        assert [d.to_dict().get('old').get('copyrights') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('statements', ['Copyright (c) 1995-2005, 2014, 2016 Jean-loup Gailly, Mark Adler']),
                ('holders', ['Jean-loup Gailly, Mark Adler'])
            ])
        ]
        assert [d.to_dict().get('new').get('copyrights') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('statements', ['Copyright (c) 2016 Mark Adler']),
                ('holders', ['Mark Adler'])
            ])
        ]

        assert len([i for i in deltas_object if i.score == 30]) == 0
        assert len([i for i in deltas_object if i.score == 25]) == 1
        assert len([i for i in deltas_object if i.score == 20]) == 0

    def test_score_copyright_info_added(self):
        new_scan = self.get_test_loc('deltacode/score_copyright_info_added_new.json')
        old_scan = self.get_test_loc('deltacode/score_copyright_info_added_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.old_file.sha1 for d in deltas_object if d.old_file.path == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if d.new_file.path == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if d.new_file.path == 'path.txt'] == [30]
        assert [d.factors for d in deltas_object if d.new_file.path == 'path.txt'].pop() == ['modified', 'copyright info added']
        assert [d.to_dict().get('old').get('copyrights') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == []
        assert [d.to_dict().get('new').get('copyrights') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('statements', ['Copyright (c) 2016 Mark Adler']),
                ('holders', ['Mark Adler'])
            ])
        ]

        assert len([i for i in deltas_object if i.score == 35]) == 0
        assert len([i for i in deltas_object if i.score == 30]) == 1
        assert len([i for i in deltas_object if i.score == 20]) == 0

    def test_score_copyright_info_removed(self):
        new_scan = self.get_test_loc('deltacode/score_copyright_info_removed_new.json')
        old_scan = self.get_test_loc('deltacode/score_copyright_info_removed_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.old_file.sha1 for d in deltas_object if d.old_file.path == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if d.new_file.path == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if d.new_file.path == 'path.txt'] == [30]
        assert [d.factors for d in deltas_object if d.new_file.path == 'path.txt'].pop() == ['modified', 'copyright info removed']
        assert [d.to_dict().get('old').get('copyrights') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('statements', ['Copyright (c) 2016 Mark Adler']),
                ('holders', ['Mark Adler'])
            ])
        ]
        assert [d.to_dict().get('new').get('copyrights') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == []

        assert len([i for i in deltas_object if i.score == 30]) == 1
        assert len([i for i in deltas_object if i.score == 20]) == 0

    def test_score_no_copyright_info(self):
        new_scan = self.get_test_loc('deltacode/score_no_copyright_info_new.json')
        old_scan = self.get_test_loc('deltacode/score_no_copyright_info_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.old_file.sha1 for d in deltas_object if d.old_file.path == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if d.new_file.path == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if d.new_file.path == 'path.txt'] == [20]
        assert [d.factors for d in deltas_object if d.new_file.path == 'path.txt'].pop() == ['modified']
        assert [d.to_dict().get('old').get('copyrights') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == []
        assert [d.to_dict().get('new').get('copyrights') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == []

        assert len([i for i in deltas_object if i.score == 30]) == 0
        assert len([i for i in deltas_object if i.score == 20]) == 1

    def test_score_no_copyright_changes(self):
        new_scan = self.get_test_loc('deltacode/score_no_copyright_changes_new.json')
        old_scan = self.get_test_loc('deltacode/score_no_copyright_changes_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.old_file.sha1 for d in deltas_object if d.old_file.path == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if d.new_file.path == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if d.new_file.path == 'path.txt'] == [20]
        assert [d.factors for d in deltas_object if d.new_file.path == 'path.txt'].pop() == ['modified']
        assert [d.to_dict().get('old').get('copyrights') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('statements', ['Copyright (c) 2016 Mark Adler']),
                ('holders', ['Mark Adler'])
            ])
        ]
        assert [d.to_dict().get('new').get('copyrights') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('statements', ['Copyright (c) 2016 Mark Adler']),
                ('holders', ['Mark Adler'])
            ])
        ]

        assert len([i for i in deltas_object if i.score == 30]) == 0
        assert len([i for i in deltas_object if i.score == 20]) == 1

    def test_score_no_copyright_key(self):
        new_scan = self.get_test_loc('deltacode/score_no_copyright_key_new.json')
        old_scan = self.get_test_loc('deltacode/score_no_copyright_key_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.old_file.sha1 for d in deltas_object if d.old_file.path == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if d.new_file.path == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if d.new_file.path == 'path.txt'] == [20]
        assert [d.factors for d in deltas_object if d.new_file.path == 'path.txt'].pop() == ['modified']
        assert [d.to_dict().get('old').get('copyrights') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == []
        assert [d.to_dict().get('new').get('copyrights') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == []

        assert len([i for i in deltas_object if i.score == 30]) == 0
        assert len([i for i in deltas_object if i.score == 20]) == 1

    def test_score_copyright_and_license_info_added(self):
        new_scan = self.get_test_loc('deltacode/score_copyright_and_license_info_added_new.json')
        old_scan = self.get_test_loc('deltacode/score_copyright_and_license_info_added_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.old_file.sha1 for d in deltas_object if d.old_file.path == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if d.new_file.path == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if d.new_file.path == 'path.txt'] == [50]
        assert [d.factors for d in deltas_object if d.new_file.path == 'path.txt'].pop() == ['modified', 'license info added', 'copyright info added']
        assert [d.to_dict().get('old').get('copyrights') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == []
        assert [d.to_dict().get('new').get('copyrights') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('statements', ['Copyright (c) 2016 Mark Adler']),
                ('holders', ['Mark Adler'])
            ])
        ]
        assert [d.to_dict().get('old').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == []
        assert [d.to_dict().get('new').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'gpl-1.0-plus'),
                ('score', 20.0),
                ('short_name', 'GPL 1.0 or later'),
                ('category', 'Copyleft'),
                ('owner', "Free Software Foundation (FSF)")
            ])
        ]

        assert len([i for i in deltas_object if i.score == 70]) == 0
        assert len([i for i in deltas_object if i.score == 50]) == 1
        assert len([i for i in deltas_object if i.score == 30]) == 0
        assert len([i for i in deltas_object if i.score == 20]) == 0

    def test_score_copyright_and_license_info_removed(self):
        new_scan = self.get_test_loc('deltacode/score_copyright_and_license_info_removed_new.json')
        old_scan = self.get_test_loc('deltacode/score_copyright_and_license_info_removed_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.old_file.sha1 for d in deltas_object if d.old_file.path == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if d.new_file.path == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if d.new_file.path == 'path.txt'] == [45]
        assert [d.factors for d in deltas_object if d.new_file.path == 'path.txt'].pop() == ['modified', 'license info removed', 'copyright info removed']
        assert [d.to_dict().get('old').get('copyrights') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('statements', ['Copyright (c) 2016 Mark Adler']),
                ('holders', ['Mark Adler'])
            ])
        ]
        assert [d.to_dict().get('new').get('copyrights') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == []
        assert [d.to_dict().get('old').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'gpl-1.0-plus'),
                ('score', 20.0),
                ('short_name', 'GPL 1.0 or later'),
                ('category', 'Copyleft'),
                ('owner', "Free Software Foundation (FSF)")
            ])
        ]
        assert [d.to_dict().get('new').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == []

        assert len([i for i in deltas_object if i.score == 55]) == 0
        assert len([i for i in deltas_object if i.score == 45]) == 1
        assert len([i for i in deltas_object if i.score == 30]) == 0
        assert len([i for i in deltas_object if i.score == 20]) == 0

    def test_score_copyright_info_added_license_info_removed(self):
        new_scan = self.get_test_loc('deltacode/score_copyright_info_added_license_info_removed_new.json')
        old_scan = self.get_test_loc('deltacode/score_copyright_info_added_license_info_removed_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.old_file.sha1 for d in deltas_object if d.old_file.path == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if d.new_file.path == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if d.new_file.path == 'path.txt'] == [45]
        assert [d.factors for d in deltas_object if d.new_file.path == 'path.txt'].pop() == ['modified', 'license info removed', 'copyright info added']
        assert [d.to_dict().get('old').get('copyrights') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == []
        assert [d.to_dict().get('new').get('copyrights') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('statements', ['Copyright (c) 2016 Mark Adler']),
                ('holders', ['Mark Adler'])
            ])
        ]
        assert [d.to_dict().get('old').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'gpl-3.0-plus'),
                ('score', 100.0),
                ('short_name', 'GPL 3.0 or later'),
                ('category', 'Copyleft'),
                ('owner', "Free Software Foundation (FSF)")
            ])
        ]
        assert [d.to_dict().get('new').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == []

        assert len([i for i in deltas_object if i.score == 55]) == 0
        assert len([i for i in deltas_object if i.score == 50]) == 0
        assert len([i for i in deltas_object if i.score == 45]) == 1
        assert len([i for i in deltas_object if i.score == 30]) == 0
        assert len([i for i in deltas_object if i.score == 20]) == 0

    def test_score_license_info_added_copyright_info_removed(self):
        new_scan = self.get_test_loc('deltacode/score_license_info_added_copyright_info_removed_new.json')
        old_scan = self.get_test_loc('deltacode/score_license_info_added_copyright_info_removed_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.old_file.sha1 for d in deltas_object if d.old_file.path == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if d.new_file.path == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if d.new_file.path == 'path.txt'] == [50]
        assert [d.factors for d in deltas_object if d.new_file.path == 'path.txt'].pop() == ['modified', 'license info added', 'copyright info removed']
        assert [d.to_dict().get('old').get('copyrights') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('statements', ['Copyright (c) 2016 Mark Adler']),
                ('holders', ['Mark Adler'])
            ])
        ]
        assert [d.to_dict().get('new').get('copyrights') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == []
        assert [d.to_dict().get('old').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == []
        assert [d.to_dict().get('new').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'gpl-3.0-plus'),
                ('score', 100.0),
                ('short_name', 'GPL 3.0 or later'),
                ('category', 'Copyleft'),
                ('owner', "Free Software Foundation (FSF)")
            ])
        ]

        assert len([i for i in deltas_object if i.score == 70]) == 0
        assert len([i for i in deltas_object if i.score == 50]) == 1
        assert len([i for i in deltas_object if i.score == 45]) == 0
        assert len([i for i in deltas_object if i.score == 30]) == 0
        assert len([i for i in deltas_object if i.score == 20]) == 0

    def test_score_copyright_change_no_license_change(self):
        new_scan = self.get_test_loc('deltacode/score_copyright_change_no_license_change_new.json')
        old_scan = self.get_test_loc('deltacode/score_copyright_change_no_license_change_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.old_file.sha1 for d in deltas_object if d.old_file.path == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if d.new_file.path == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if d.new_file.path == 'path.txt'] == [25]
        assert [d.factors for d in deltas_object if d.new_file.path == 'path.txt'].pop() == ['modified', 'copyright change']
        assert [d.to_dict().get('old').get('copyrights') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('statements', ['Copyright (c) 2016 Mark Adler']),
                ('holders', ['Mark Adler'])
            ])
        ]
        assert [d.to_dict().get('new').get('copyrights') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('statements', ['Copyright (c) 2016 Alfred E. Neuman']),
                ('holders', ['Alfred E. Neuman'])
            ])
        ]
        assert [d.to_dict().get('old').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'gpl-3.0-plus'),
                ('score', 100.0),
                ('short_name', 'GPL 3.0 or later'),
                ('category', 'Copyleft'),
                ('owner', "Free Software Foundation (FSF)")
            ])
        ]
        assert [d.to_dict().get('new').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
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
        new_scan = self.get_test_loc('deltacode/score_license_change_no_copyright_change_new.json')
        old_scan = self.get_test_loc('deltacode/score_license_change_no_copyright_change_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.old_file.sha1 for d in deltas_object if d.old_file.path == 'path.txt'] == ['b']
        assert [d.new_file.sha1 for d in deltas_object if d.new_file.path == 'path.txt'] == ['b_modified']

        assert [d.score for d in deltas_object if d.new_file.path == 'path.txt'] == [30]
        assert [d.factors for d in deltas_object if d.new_file.path == 'path.txt'].pop() == ['modified', 'license change']
        assert [d.to_dict().get('old').get('copyrights') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('statements', ['Copyright (c) 2016 Mark Adler']),
                ('holders', ['Mark Adler'])
            ])
        ]
        assert [d.to_dict().get('new').get('copyrights') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('statements', ['Copyright (c) 2016 Mark Adler']),
                ('holders', ['Mark Adler'])
            ])
        ]
        assert [d.to_dict().get('old').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
            OrderedDict([
                ('key', 'gpl-3.0-plus'),
                ('score', 100.0),
                ('short_name', 'GPL 3.0 or later'),
                ('category', 'Copyleft'),
                ('owner', "Free Software Foundation (FSF)")
            ])
        ]
        assert [d.to_dict().get('new').get('licenses') for d in deltas_object if d.new_file.path == 'path.txt'].pop() == [
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
        new_scan = self.get_test_loc('deltacode/score_license_change_no_copyright_change_new.json')
        old_scan = self.get_test_loc('deltacode/score_license_change_no_copyright_change_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.score for d in deltas_object if d.new_file.path == 'path.txt'] == [30]
        assert [d.factors for d in deltas_object if d.new_file.path == 'path.txt'].pop() == ['modified', 'license change']

        for d in deltas_object:
            if d.new_file.path == 'path.txt':
                d.update(25, 'This is a test of a license change')

        assert [d.score for d in deltas_object if d.new_file.path == 'path.txt'] == [55]
        assert [d.factors for d in deltas_object if d.new_file.path == 'path.txt'].pop() == ['modified', 'license change', 'This is a test of a license change']

    def test_Delta_to_dict_multiple_copyright_statements_and_holders(self):
        new = {
            'path': 'path/modified.txt',
            'type': 'file',
            'name': 'modified.txt',
            'size': 21,
            'sha1': 'a_modified',
            'original_path': '',
            'licenses': [],
            'copyrights': [
                {
                    "statements": [
                        "Copyright (c) 1995-2005, 2014, 2016 Jean-loup Gailly, Mark Adler",
                        "Copyright (c) 1998 by Andreas R. Kleinert",
                        "Copyright (c) 2002-2004 Dmitriy Anisimkov",
                        "Copyright (c) 1998, 2007 Brian Raiter",
                        "Copyright (c) 1997,99 Borland Corp.",
                        "(c) Copyright Henrik Ravn 2004",
                        "Copyright (c) 1995-2010 Jean-loup Gailly, Brian Raiter and Gilles Vollant.",
                        "Copyright (c) 2003 Chris Anderson",
                        "Copyright (c) 1997 Christian Michelsen Research as Advanced Computing",
                        "Copyright (c) 2009-2010 Mathias Svensson http://result42.com",
                        "Copyright (c) 1990-2000 Info-ZIP.",
                        "Copyright (c) 1995-2005, 2014, 2016 Jean-loup Gailly, Mark Adler",
                        "Copyright (c) 1998 by Andreas R. Kleinert",
                        "Copyright (c) 2002-2004 Dmitriy Anisimkov",
                        "Copyright (c) 1998, 2007 Brian Raiter",
                        "Copyright (c) 1997,99 Borland Corp.",
                        "(c) Copyright Henrik Ravn 2004",
                        "Copyright (c) 1995-2010 Jean-loup Gailly, Brian Raiter and Gilles Vollant.",
                        "Copyright (c) 2003 Chris Anderson",
                        "Copyright (c) 1997 Christian Michelsen Research as Advanced Computing",
                        "Copyright (c) 2009-2010 Mathias Svensson http://result42.com",
                        "Copyright (c) 1990-2000 Info-ZIP."
                    ],
                    "holders": [
                        "Jean-loup Gailly, Mark Adler",
                        "Andreas R. Kleinert",
                        "Dmitriy Anisimkov",
                        "Brian Raiter",
                        "Borland Corp.",
                        "Henrik Ravn",
                        "Jean-loup Gailly, Brian Raiter, Gilles Vollant",
                        "Chris Anderson",
                        "Christian Michelsen Research as Advanced Computing",
                        "Mathias Svensson",
                        "Info-ZIP",
                        "Jean-loup Gailly, Mark Adler",
                        "Andreas R. Kleinert",
                        "Dmitriy Anisimkov",
                        "Brian Raiter",
                        "Borland Corp.",
                        "Henrik Ravn",
                        "Jean-loup Gailly, Brian Raiter, Gilles Vollant",
                        "Chris Anderson",
                        "Christian Michelsen Research as Advanced Computing",
                        "Mathias Svensson",
                        "Info-ZIP"
                    ],
                    "authors": []
                }
            ]
        }

        old = {
            'path': 'path/modified.txt',
            'type': 'file',
            'name': 'modified.txt',
            'size': 20,
            'sha1': 'a',
            'original_path': '',
            'licenses': [],
            'copyrights': [
                {
                    "statements": [
                        "Copyright (c) 2018 Jane Doe"
                    ],
                    "holders": [
                        "Jane Doe"
                    ],
                    "authors": []
                }
            ]
        }

        expected = OrderedDict([
            ('factors', ['modified']),
            ('score', 20),
            ('new', OrderedDict([
                ('path', 'path/modified.txt'),
                ('type', 'file'),
                ('name', 'modified.txt'),
                ('size', 21),
                ('sha1', 'a_modified'),
                ('original_path', ''),
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
                ('original_path', ''),
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

        result_new = models.File(new)
        result_old = models.File(old)

        delta = deltacode.Delta(20, result_new, result_old)
        delta.factors.append('modified')

        assert delta.to_dict() == expected

    def test_Delta_to_dict_Copyright_unusual_characters(self):
        new_scan = self.get_test_loc('deltacode/scan_unusual_characters_new.json')
        old_scan = self.get_test_loc('deltacode/scan_unusual_characters_old.json')

        options = OrderedDict([
            ('--all-delta-types', False)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.factors for d in deltas_object if d.new_file.path == 'a1.py'].pop() == ['modified', 'license change', 'copyright change']

        holders_list = [c.holders.pop() for d in deltas_object if d.new_file.path == 'a1.py' for c in d.new_file.copyrights]

        assert 'Francois Hennebique and others.' in holders_list
        assert 'Ottomar Anschutz.' in holders_list
        assert 'Christiane Nusslein-Volhard.' in holders_list
        assert 'Behram Kursunoglu.' in holders_list

        statements_list = [c.statements.pop() for d in deltas_object if d.new_file.path == 'a1.py' for c in d.new_file.copyrights]

        assert 'Copyright (c) 2017-2018 Francois Hennebique and others.' in statements_list
        assert 'Copyright (c) 1999 Ottomar Anschutz.' in statements_list
        assert 'Copyright (c) 2015-18 Christiane Nusslein-Volhard.' in statements_list
        assert 'Copyright (c) 1999 Behram Kursunoglu.' in statements_list

        assert [d.score for d in deltas_object if d.new_file.path == 'a1.py'] == [35]
        assert [d.score for d in deltas_object if d.new_file.path == 'a2.py'] == [0]

    def test_DeltaCode_sort_order(self):
        new_scan = self.get_test_loc('deltacode/scan_sorted01_new.json')
        old_scan = self.get_test_loc('deltacode/scan_sorted01_old.json')

        options = OrderedDict([
            ('--all-delta-types', True)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        expected = [
            ['added', 'license info added', 'copyright info added'],
            ['modified'],
            ['moved'],
            ['removed'],
            ['unmodified'],
            ['unmodified'],
            ['unmodified']
        ]

        unexpected = [
            ['added'],
            ['modified'],
            ['unmodified'],
            ['unmodified'],
            ['unmodified'],
            ['removed'],
            ['moved']
        ]

        factors = [d.factors for d in deltas_object]

        assert factors == expected
        assert factors != unexpected

    def test_DeltaCode_no_lic_to_all_notable_lic(self):
        new_scan = self.get_test_loc('deltacode/no_lic_to_all_notable_lic_new.json')
        old_scan = self.get_test_loc('deltacode/no_lic_to_all_notable_lic_old.json')

        options = OrderedDict([
            ('--all-delta-types', True)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.score for d in deltas_object if d.new_file.path == 'a1.py'] == [50]
        assert [d.score for d in deltas_object if d.new_file.path == 'a2.py'] == [0]

        assert sorted([d.factors for d in deltas_object if d.new_file.path == 'a1.py'].pop()) == sorted(['modified', 'license info added', 'copyright info added'])
        assert [d.factors for d in deltas_object if d.new_file.path == 'a2.py'].pop() == ['unmodified']

    def test_DeltaCode_apache_to_all_notable_lic(self):
        new_scan = self.get_test_loc('deltacode/apache_to_all_notable_lic_new.json')
        old_scan = self.get_test_loc('deltacode/apache_to_all_notable_lic_old.json')

        options = OrderedDict([
            ('--all-delta-types', True)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.score for d in deltas_object if d.new_file.path == 'a1.py'] == [35]
        assert [d.score for d in deltas_object if d.new_file.path == 'a2.py'] == [0]

        assert sorted([d.factors for d in deltas_object if d.new_file.path == 'a1.py'].pop()) == sorted(['modified', 'license change', 'copyright change'])
        assert [d.factors for d in deltas_object if d.new_file.path == 'a2.py'].pop() == ['unmodified']

    def test_DeltaCode_copyleft_etc_to_prop_free_and_commercial(self):
        new_scan = self.get_test_loc('deltacode/copyleft_etc_to_prop_free_and_commercial_new.json')
        old_scan = self.get_test_loc('deltacode/copyleft_etc_to_prop_free_and_commercial_old.json')

        options = OrderedDict([
            ('--all-delta-types', True)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.score for d in deltas_object if d.new_file.path == 'a1.py'] == [30]
        assert [d.score for d in deltas_object if d.new_file.path == 'a2.py'] == [0]

        assert [d.factors for d in deltas_object if d.new_file.path == 'a1.py'].pop() == ['modified', 'license change']
        assert [d.factors for d in deltas_object if d.new_file.path == 'a2.py'].pop() == ['unmodified']

    def test_DeltaCode_permissive_add_public_domain(self):
        new_scan = self.get_test_loc('deltacode/permissive_add_public_domain_new.json')
        old_scan = self.get_test_loc('deltacode/permissive_add_public_domain_old.json')

        options = OrderedDict([
            ('--all-delta-types', True)
        ])

        deltacode_object = DeltaCode(new_scan, old_scan, options)

        deltas_object = deltacode_object.deltas

        assert [d.score for d in deltas_object if d.new_file.path == 'a1.py'] == [30]
        assert [d.score for d in deltas_object if d.new_file.path == 'a2.py'] == [0]

        assert [d.factors for d in deltas_object if d.new_file.path == 'a1.py'].pop() == ['modified', 'license change']
        assert [d.factors for d in deltas_object if d.new_file.path == 'a2.py'].pop() == ['unmodified']
