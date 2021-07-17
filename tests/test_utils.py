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

from __future__ import absolute_import, print_function, unicode_literals, division

import codecs
from collections import OrderedDict
import json
import os

import pytest
import unicodecsv

from click.testing import CliRunner

from commoncode.testcase import FileBasedTesting
from commoncode.resource import VirtualCodebase
import deltacode
from deltacode import utils
from deltacode import DeltaCode


unique_categories = set([
    'Commercial',
    'Copyleft',
    'Copyleft Limited',
    'Free Restricted',
    'Patent License',
    'Proprietary Free'
])


class TestUtils(FileBasedTesting):

    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_update_from_license_info_empty(self):
        test_delta = deltacode.Delta()

        utils.update_from_license_info(test_delta, set())

        assert test_delta.score == 0

    @pytest.mark.xfail(reason='Tests no longer required having None paths')
    def test_update_from_license_info_non_modified(self):
        test_file = models.File({'path':'/test/path.txt', 'name': 'path.txt'})
        test_delta = deltacode.Delta(old_file=test_file)

        utils.update_from_license_info(test_delta, set())

        assert test_delta.score == 0
        assert len(test_delta.factors) == 0

    def test_update_from_license_info_no_license_key_value(self):
        test_file_new = self.get_test_loc('utils/update_from_license_info_no_license_key_value_new.json')
        test_file_old = self.get_test_loc('utils/update_from_license_info_no_license_key_value_old.json')

        results = DeltaCode(test_file_new, test_file_old, {})

        deltas = results.deltas[0]

        assert deltas.score == 20
        assert len(deltas.factors) == 0

    def test_update_from_license_info_no_license_changes(self):
        test_scan_new = self.get_test_loc('utils/update_from_license_info_no_license_changes_new.json')
        test_scan_old = self.get_test_loc('utils/update_from_license_info_no_license_changes_old.json')

        result = DeltaCode(test_scan_new, test_scan_old, {})

        deltas = result.deltas[0]

        assert deltas.score == 20
        assert len(deltas.factors) == 0

    def test_update_from_license_info_single_license_change(self):
        test_file_new = self.get_test_loc('utils/update_from_license_info_single_license_change_new.json')
        test_file_old = self.get_test_loc('utils/update_from_license_info_single_license_change_old.json')

        results = DeltaCode(test_file_new, test_file_old, {})

        expected_factors = [
            'license change',
            'copyleft added'
        ]
        
        deltas = results.deltas[0]

        assert deltas.score == 50
        assert len(deltas.factors) == 2
        for factor in expected_factors:
            assert factor in deltas.factors

    def test_update_from_license_info_copyleft_license_info_added(self):
        test_file_new = self.get_test_loc('utils/update_from_license_info_copyleft_license_info_added_new.json')
        test_file_old = self.get_test_loc('utils/update_from_license_info_copyleft_license_info_added_old.json')

        results = DeltaCode(test_file_new, test_file_old, {})

        deltas = results.deltas[0]

        expected_factors = [
            'license info added',
            'copyleft added'
        ]

        assert deltas.score == 60
        assert len(deltas.factors) == 2
        for factor in expected_factors:
            assert factor in deltas.factors

    def test_update_from_license_info_permissive_license_info_added(self):
        test_file_new = self.get_test_loc('utils/update_from_license_info_permissive_license_info_added_new.json')
        test_file_old = self.get_test_loc('utils/update_from_license_info_permissive_license_info_added_old.json')


        results = DeltaCode(test_file_new, test_file_old, {})

        deltas = results.deltas[0]

        assert deltas.score == 40
        assert len(deltas.factors) == 2
        assert 'license info added' in deltas.factors
        assert 'permissive added' in deltas.factors

    def test_update_from_license_info_permissive_license_info_removed(self):
        test_file_new = self.get_test_loc('utils/update_from_license_info_permissive_license_info_removed_new.json')
        test_file_old = self.get_test_loc('utils/update_from_license_info_permissive_license_info_removed_old.json')


        results = DeltaCode(test_file_new, test_file_old, {})

        deltas = results.deltas[0]

        assert deltas.score == 35
        assert len(deltas.factors) == 1
        assert 'license info removed' in deltas.factors

    def test_update_from_license_info_copyleft_license_info_removed(self):
        test_file_new = self.get_test_loc('utils/update_from_license_info_copyleft_license_info_removed_new.json')
        test_file_old = self.get_test_loc('utils/update_from_license_info_copyleft_license_info_removed_old.json')


        results = DeltaCode(test_file_new, test_file_old, {})

        deltas = results.deltas[0]

        assert deltas.score == 35
        assert len(deltas.factors) == 1
        assert 'license info removed' in deltas.factors

    def test_update_from_license_info_one_license_added(self):
        test_file_new = self.get_test_loc('utils/update_from_license_info_one_license_added_new.json')
        test_file_old = self.get_test_loc('utils/update_from_license_info_one_license_added_old.json')

        results = DeltaCode(test_file_new, test_file_old, {})

        deltas = results.deltas[0]

        expected_factors = [
            'license change',
            'copyleft added'
        ]

        assert deltas.score == 50
        assert len(deltas.factors) == 2
        for factor in expected_factors:
            assert factor in deltas.factors

    def test_update_from_license_info_one_license_removed(self):
        test_file_new = self.get_test_loc('utils/update_from_license_info_one_license_removed_new.json')
        test_file_old = self.get_test_loc('utils/update_from_license_info_one_license_removed_old.json')


        results = DeltaCode(test_file_new, test_file_old, {})

        deltas = results.deltas[0]

        assert deltas.score == 30
        assert len(deltas.factors) == 1
        assert 'license change' in deltas.factors

    def test_update_from_license_info_one_permissive_to_two_permissives(self):
        test_file_new = self.get_test_loc('utils/update_from_license_info_one_permissive_to_two_permissives_new.json')
        test_file_old = self.get_test_loc('utils/update_from_license_info_one_permissive_to_two_permissives_old.json')

        results = DeltaCode(test_file_new, test_file_old, {})

        deltas = results.deltas[0]

        assert deltas.score == 30
        assert len(deltas.factors) == 1
        assert 'license change' in deltas.factors

    def test_update_from_license_info_two_permissives_to_one_permissive(self):
        test_file_new = self.get_test_loc('utils/update_from_license_info_one_permissive_to_two_permissives_new.json')
        test_file_old = self.get_test_loc('utils/update_from_license_info_one_permissive_to_two_permissives_old.json')

        results = DeltaCode(test_file_new, test_file_old, {})

        deltas = results.deltas[0]

        assert deltas.score == 30
        assert len(deltas.factors) == 1
        assert 'license change' in deltas.factors

    def test_update_from_license_info_one_permissive_to_six_copyleft_or_higher(self):
        test_file_new = self.get_test_loc('utils/update_from_license_info_one_permissive_to_six_copyleft_or_higher_new.json')
        test_file_old = self.get_test_loc('utils/update_from_license_info_one_permissive_to_six_copyleft_or_higher_old.json')


        results = DeltaCode(test_file_new, test_file_old, {})

        deltas = results.deltas[0]

        assert deltas.score == 150
        assert len(deltas.factors) == 7

        expected_factors = [
            'license change',
            'commercial added',
            'copyleft added',
            'copyleft limited added',
            'free restricted added',
            'patent license added',
            'proprietary free added'
        ]

        for factor in expected_factors:
            assert factor in deltas.factors

    def test_update_from_license_info_copyleft_to_different_copyleft(self):
        test_file_new = self.get_test_loc('utils/update_from_license_info_copyleft_to_different_copyleft_new.json')
        test_file_old = self.get_test_loc('utils/update_from_license_info_copyleft_to_different_copyleft_old.json')


        results = DeltaCode(test_file_new, test_file_old, {})

        deltas = results.deltas[0]

        assert deltas.score == 30
        assert len(deltas.factors) == 1
        assert 'license change' in deltas.factors

    def test_update_from_license_info_copyleft_to_copyleft_limited(self):
        test_file_new = self.get_test_loc('utils/update_from_license_info_copyleft_to_copyleft_limited_new.json')
        test_file_old = self.get_test_loc('utils/update_from_license_info_copyleft_to_copyleft_limited_old.json')

        results = DeltaCode(test_file_new, test_file_old, {})

        deltas = results.deltas[0]

        assert deltas.score == 40
        assert len(deltas.factors) == 2
        assert 'license change' in deltas.factors
        assert 'copyleft limited added' in deltas.factors

    @pytest.mark.xfail(reason='Tests no longer required having None paths')
    def test_update_from_license_info_file_added_permissive_license(self):
        test_file_new = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a',
            'original_path': '',
            "licenses": [
                {
                    "key": "mit",
                    "score": 80.0,
                    "short_name": "MIT License",
                    "category": "Permissive"
                }
            ]
        })

        test_delta = deltacode.Delta(100, test_file_new, None)

        utils.update_added_from_license_info(test_delta, unique_categories)

        assert test_delta.score == 120
        assert len(test_delta.factors) == 2

        assert 'license info added' in test_delta.factors
        assert 'permissive added' in test_delta.factors

    @pytest.mark.xfail(reason='Tests no longer required having None paths')
    def test_update_from_license_info_file_added_commercial_and_copyleft_licenses(self):
        test_file_new = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a',
            'original_path': '',
            "licenses": [
                {
                    "key": "commercial-license",
                    "score": 55.0,
                    "short_name": "Commercial License",
                    "category": "Commercial",
                    "owner": "Unspecified"
                },
                {
                    "key": "adapt-1.0",
                    "score": 15.0,
                    "short_name": "APL 1.0",
                    "category": "Copyleft",
                    "owner": "OSI - Open Source Initiative"
                }
            ]
        })

        test_delta = deltacode.Delta(100, test_file_new, None)

        utils.update_added_from_license_info(test_delta, unique_categories)

        assert test_delta.score == 160
        assert len(test_delta.factors) == 3

        assert 'license info added' in test_delta.factors

        expected_factors = [
            'license info added',
            'commercial added',
            'copyleft added'
        ]

        for factor in expected_factors:
            assert factor in test_delta.factors

    @pytest.mark.xfail(reason='Tests no longer required having None paths')
    def test_update_from_copyright_info_empty(self):
        test_delta = deltacode.Delta()

        utils.update_from_copyright_info(test_delta)

        assert test_delta.score == 0

    def test_update_from_copyright_info_non_modified(self):
        test_file_new = self.get_test_loc('utils/update_from_copyright_info_non_modified_new.json')
        test_file_old = self.get_test_loc('utils/update_from_copyright_info_non_modified_old.json')

        test_delta = DeltaCode(test_file_new, test_file_old, {})

        assert len(test_delta.deltas) == 1
        assert test_delta.deltas[0].status == "unmodified"

    def test_update_from_copyright_info_no_copyright_key_value(self):
        test_file_new = self.get_test_loc('utils/update_from_copyright_info_no_copyright_key_value_new.json')
        test_file_old = self.get_test_loc('utils/update_from_copyright_info_no_copyright_key_value_old.json')


        results = DeltaCode(test_file_new, test_file_old, {})

        deltas = results.deltas[0]

        assert deltas.score == 20
        assert len(deltas.factors) == 0

    def test_update_from_copyright_info_no_copyright_changes(self):
        test_file_new = self.get_test_loc('utils/update_from_copyright_info_no_copyright_changes_new.json')
        test_file_old = self.get_test_loc('utils/update_from_copyright_info_no_copyright_changes_old.json')


        results = DeltaCode(test_file_new, test_file_old, {})

        deltas = results.deltas[0]

        assert deltas.score == 20
        assert len(deltas.factors) == 0

    def test_update_from_copyright_info_single_copyright_change(self):
        test_file_new = self.get_test_loc('utils/update_from_copyright_info_single_copyright_change_new.json')
        test_file_old = self.get_test_loc('utils/update_from_copyright_info_single_copyright_change_old.json')

        results = DeltaCode(test_file_new, test_file_old, {})

        deltas = results.deltas[0]

        assert deltas.score == 25
        assert len(deltas.factors) == 1
        assert 'copyright change' in deltas.factors

    def test_update_from_copyright_info_single_copyright_change_holders_only(self):
        test_scan_new = self.get_test_loc("utils/update_from_copyright_info_single_copyright_change_holders_only_new.json")
        test_scan_old = self.get_test_loc("utils/update_from_copyright_info_single_copyright_change_holders_only_old.json")


        results = DeltaCode(test_scan_new, test_scan_old, {})
        deltas = results.deltas[0]

        assert deltas.score == 25
        assert len(deltas.factors) == 1
        assert 'copyright change' in deltas.factors

    def test_update_from_copyright_info_single_copyright_change_statements_only(self):
        test_scan_new = self.get_test_loc('utils/update_from_copyright_info_single_copyright_change_statements_only_new.json')
        test_scan_old = self.get_test_loc('utils/update_from_copyright_info_single_copyright_change_statements_only_old.json')

        results = DeltaCode(test_scan_new, test_scan_old, {})

        deltas = results.deltas[0]

        assert deltas.score == 20
        assert len(deltas.factors) == 0
        assert 'copyright change' not in deltas.factors

    def test_update_from_copyright_info_copyright_info_added(self):
        test_scan_new = self.get_test_loc('utils/update_from_copyright_info_copyright_info_added_new.json')
        test_scan_old = self.get_test_loc('utils/update_from_copyright_info_copyright_info_added_old.json')


        results = DeltaCode(test_scan_new, test_scan_old, {})

        deltas = results.deltas[0]
    
        assert deltas.score == 30
        assert len(deltas.factors) == 1
        assert 'copyright info added' in deltas.factors

    def test_update_from_copyright_info_copyright_info_removed(self):
        test_scan_new = self.get_test_loc('utils/update_from_copyright_info_copyright_info_removed_new.json')
        test_scan_old = self.get_test_loc('utils/update_from_copyright_info_copyright_info_removed_old.json')


        results = DeltaCode(test_scan_new, test_scan_old, {})

        deltas = results.deltas[0]

        assert deltas.score == 30
        assert len(deltas.factors) == 1
        assert 'copyright info removed' in deltas.factors

    def test_update_from_copyright_info_one_copyright_added(self):
        test_scan_new = self.get_test_loc('utils/update_from_copyright_info_one_copyright_added_new.json')
        test_scan_old = self.get_test_loc('utils/update_from_copyright_info_one_copyright_added_old.json')

        results = DeltaCode(test_scan_new, test_scan_old, {})

        deltas = results.deltas[0]

        assert deltas.score == 25
        assert len(deltas.factors) == 1
        assert 'copyright change' in deltas.factors

    def test_update_from_copyright_info_one_copyright_removed(self):
        test_scan_new = self.get_test_loc('utils/update_from_copyright_info_one_copyright_removed_new.json')
        test_scan_old = self.get_test_loc('utils/update_from_copyright_info_one_copyright_removed_old.json')


        results = DeltaCode(test_scan_new, test_scan_old, {})

        deltas = results.deltas[0]

        assert deltas.score == 25
        assert len(deltas.factors) == 1
        assert 'copyright change' in deltas.factors

    def test_update_from_copyright_info_file_added_one_copyright(self):
        test_scan_new = self.get_test_loc('utils/update_from_copyright_info_file_added_one_copyright_new.json')
        test_scan_old = self.get_test_loc('utils/update_from_copyright_info_file_added_one_copyright_old.json')


        test_delta = DeltaCode(test_scan_new, test_scan_old, {})

        deltas = test_delta.deltas[0]

        assert deltas.score == 110
        assert len(deltas.factors) == 1
        assert 'copyright info added' in deltas.factors

    def test_update_from_lic_copy_info_copyright_and_license_info_added(self):
        test_scan_new = self.get_test_loc('utils/update_from_lic_copy_info_copyright_and_license_info_added_new.json')
        test_scan_old = self.get_test_loc('utils/update_from_lic_copy_info_copyright_and_license_info_added_old.json')


        results = DeltaCode(test_scan_new, test_scan_old, {})
        
        deltas = results.deltas[0]

        expected_factors = [
            'license info added',
            'copyleft added',
            'copyright info added'
        ]

        assert deltas.score == 70
        assert len(deltas.factors) == 3
        for factor in expected_factors:
            assert factor in deltas.factors

    def test_update_from_lic_copy_info_copyright_and_license_info_removed(self):
        test_file_new = self.get_test_loc('utils/update_from_lic_copy_info_copyright_and_license_info_removed_new.json')
        test_file_old = self.get_test_loc('utils/update_from_lic_copy_info_copyright_and_license_info_removed_old.json')


        test_delta = DeltaCode(test_file_new, test_file_old, {})

        deltas = test_delta.deltas[0]

        expected_factors = [
            'license info removed',
            'copyright info removed'
        ]

        assert deltas.score == 45
        assert len(deltas.factors) == 2
        for factor in expected_factors:
            assert factor in deltas.factors

    def test_update_from_lic_copy_info_copyright_info_added_license_info_removed(self):
        test_file_new = self.get_test_loc('utils/update_from_lic_copy_info_copyright_info_added_license_info_removed_new.json')
        test_file_old = self.get_test_loc('utils/update_from_lic_copy_info_copyright_info_added_license_info_removed_old.json')


        test_delta = DeltaCode(test_file_new, test_file_old, {})

        deltas = test_delta.deltas[0]

        expected_factors = [
            'license info removed',
            'copyright info added'
        ]

        assert deltas.score == 45
        assert len(deltas.factors) == 2
        for factor in expected_factors:
            assert factor in deltas.factors

    def test_update_from_lic_copy_info_license_info_added_copyright_info_removed(self):
        test_file_new = self.get_test_loc('utils/update_from_lic_copy_info_license_info_added_copyright_info_removed_new.json')
        test_file_old = self.get_test_loc('utils/update_from_lic_copy_info_license_info_added_copyright_info_removed_old.json')


        test_delta = DeltaCode(test_file_new, test_file_old, {})
        
        expected_factors = [
            'license info added',
            'copyleft added',
            'copyright info removed'
        ]

        deltas = test_delta.deltas[0]

        assert deltas.score == 70
        assert len(deltas.factors) == 3
        for factor in expected_factors:
            assert factor in deltas.factors

    def test_update_from_lic_copy_info_copyright_change_no_license_change(self):
        test_file_new = self.get_test_loc('utils/update_from_lic_copy_info_copyright_change_no_license_change_new.json')
        test_file_old = self.get_test_loc('utils/update_from_lic_copy_info_copyright_change_no_license_change_old.json')


        test_delta = DeltaCode(test_file_new, test_file_old, {})

        deltas = test_delta.deltas[0]

        assert deltas.score == 25
        assert len(deltas.factors) == 1
        assert 'copyright change' in deltas.factors

    def test_update_from_lic_copy_info_license_change_no_copyright_change(self):
        test_file_new = self.get_test_loc('utils/update_from_lic_copy_info_license_change_no_copyright_change_new.json')
        test_file_old = self.get_test_loc('utils/update_from_lic_copy_info_license_change_no_copyright_change_old.json')


        test_delta = DeltaCode(test_file_new, test_file_old, {})

        expected_factors = [
            'license change',
            'copyleft added'
        ]

        deltas = test_delta.deltas[0]

        assert deltas.score == 50
        assert len(deltas.factors) == 2
        for factor in expected_factors:
            assert factor in deltas.factors

    def test_update_from_lic_copy_info_file_added_copyright_and_permissive_license(self):
        test_file_new = self.get_test_loc('utils/update_from_lic_copy_info_file_added_copyright_and_permissive_license_new.json')
        test_file_old = self.get_test_loc('utils/update_from_lic_copy_info_file_added_copyright_and_permissive_license_old.json')


        deltacode = DeltaCode(test_file_new, test_file_old, {})

        expected_factors = [
            'license info added',
            'permissive added',
            'copyright info added'
        ]
        
        delta = deltacode.deltas[0]

        assert delta.score == 130
        assert len(delta.factors) == 3
        for factor in expected_factors:
            assert factor in delta.factors

    def test_update_from_lic_copy_info_file_added_copyright_and_commercial_and_copyleft_licenses(self):
        test_file_new = self.get_test_loc('utils/update_from_lic_copy_info_file_added_copyright_and_commercial_and_copyleft_licenses_new.json')
        test_file_old = self.get_test_loc('utils/update_from_lic_copy_info_file_added_copyright_and_commercial_and_copyleft_licenses_old.json')


        deltacode = DeltaCode(test_file_new, test_file_old, {})

        expected_factors = [
            'license info added',
            'commercial added',
            'copyleft added',
            'copyright info added'
        ]

        delta = deltacode.deltas[0]

        assert delta.score == 170
        assert len(delta.factors) == 4
        for factor in expected_factors:
            assert factor in delta.factors

    def test_align_trees_simple(self):
        test_scan_new = self.get_test_loc('utils/align-trees-simple-new.json')
        # Our old scan uses --full-root option in scancode
        test_scan_old = self.get_test_loc('utils/align-trees-simple-old.json')

        new_scan = VirtualCodebase(test_scan_new)
        old_scan = VirtualCodebase(test_scan_old)

        result_seg_new, result_seg_old = utils.align_trees(new_scan, old_scan)

        assert result_seg_new == 0
        # Our old scan uses --full-root option in scancode, hence the 5 segments that
        # can be removed.
        assert result_seg_old == 5

    def test_align_tress_zlib_failing(self):
        test_scan_new = self.get_test_loc('utils/align-trees-zlib-failing-new.json')
        test_scan_old = self.get_test_loc('utils/align-trees-zlib-failing-old.json')

        new_scan = VirtualCodebase(test_scan_new)
        old_scan = VirtualCodebase(test_scan_old)

        # test that the exception is raised
        with pytest.raises(utils.AlignmentException):
            result_seg_new, result_seg_old = utils.align_trees(new_scan, old_scan)
