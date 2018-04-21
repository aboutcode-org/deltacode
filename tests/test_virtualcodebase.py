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
# from deltacode import DeltaCode
from deltacode import models

from deltacode.virtualcodebase import DeltaCode_VC


class TestVirtualCodebase(FileBasedTesting):

    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_loading(self):
        new_scan = self.get_test_loc('virtualcodebase/vc_load.json')
        old_scan = self.get_test_loc('virtualcodebase/vc_load.json')

        expected = DeltaCode_VC(new_scan, old_scan, {'--all-delta-types': True})

        assert expected.new_codebase is not None
        print(list(expected.new_codebase.walk())[0])

    def test_determine_delta_all_unmodified(self):
        new_scan = self.get_test_loc('virtualcodebase/determine_delta_all_unmodified.json')
        old_scan = self.get_test_loc('virtualcodebase/determine_delta_all_unmodified.json')

        expected = DeltaCode_VC(new_scan, old_scan, {'--all-delta-types': True})

    def test_1_file_moved(self):
        # New scans created 4/11/18 with latest ScanCode version:
        new_scan = self.get_test_loc('virtualcodebase/1_file_moved_new.json')
        old_scan = self.get_test_loc('virtualcodebase/1_file_moved_old.json')

        expected = DeltaCode_VC(new_scan, old_scan, {'--all-delta-types': True})

        results_new = list(expected.new_codebase.walk())
        results_old = list(expected.old_codebase.walk())

        # TODO: Break these into separate tests?

        assert expected.errors == []
        assert len(results_new) == 11
        assert len(results_old) == 11

        assert [resource.pid for resource in results_new if resource.rid == 0] == [None]

        assert [resource.pid for resource in results_new if resource.rid == 10] == [5]
        assert [resource.path for resource in results_new if resource.rid == 10] == ['1_file_moved_new/b/b4.py']
        assert [resource.name for resource in results_new if resource.rid == 10] == ['b4.py']
        assert [resource.is_file for resource in results_new if resource.rid == 10] == [True]
        assert [resource.size for resource in results_new if resource.rid == 10] == [200]
        assert [resource.has_children() for resource in results_new if resource.rid == 10] == [False]
        assert [resource.has_siblings(expected.new_codebase) for resource in results_new if resource.rid == 10] == [True]

        assert (1, '1_file_moved_new/a', 'a') in [(sibling.rid, sibling.path, sibling.name) for resource in results_new if resource.has_siblings(expected.new_codebase) for sibling in resource.siblings(expected.new_codebase) if resource.rid == 5]

        assert (10, '1_file_moved_new/b/b4.py', 'b4.py') in [(sibling.rid, sibling.path, sibling.name) for resource in results_new if resource.has_siblings(expected.new_codebase) for sibling in resource.siblings(expected.new_codebase) if resource.rid == 6]

        assert [len(resource.licenses) for resource in results_new if resource.rid == 10] == [1]
        assert 'apache-2.0' in [license.get('key') for license in resource.licenses]

        assert [len(resource.copyrights) for resource in results_new if resource.rid == 10] == [1]
        assert ['Copyright (c) 2017 Acme Software Inc. and others.'] in [copyright.get('statements') for copyright in resource.copyrights]

        expected_structure = [
            ('1_file_moved_new', False),
                ('a', False),
                    ('a1.py', True),
                    ('a2.py', True),
                    ('a3.py', True),
                ('b', False),
                    ('a4.py', True),
                    ('b1.py', True),
                    ('b2.py', True),
                    ('b3.py', True),
                    ('b4.py', True)
        ]

        assert expected_structure == [(r.name, r.is_file) for r in results_new]
        print('\n\nexpected = {}\n'.format(expected))
        print('\n\nexpected.deltas = {}\n'.format(expected.deltas))
        for d in expected.deltas:
            print('\n\nfor d in expected.deltas, d = {}\n'.format(d))
            # print('for d in expected.deltas, d.new_file.path = {}\n'.format(d.new_file.path))
            # print('for d in expected.deltas, d.old_file.path = {}\n'.format(d.old_file.path))
            print('for d in expected.deltas, d.new_resource.path = {}\n'.format(d.new_resource.path))
            print('for d in expected.deltas, d.old_resource.path = {}\n'.format(d.old_resource.path))
            print('for d in expected.deltas, d.factors = {}\n'.format(d.factors))
            print('for d in expected.deltas, d.score = {}\n'.format(d.score))
