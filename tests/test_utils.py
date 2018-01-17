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

import pytest
import unicodecsv

from click.testing import CliRunner

from commoncode.testcase import FileBasedTesting
import deltacode
from deltacode import utils
from deltacode import models


class TestUtils(FileBasedTesting):

    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_align_trees_simple(self):
        test_scan_new = self.get_test_loc('utils/align-trees-simple-new.json')
        # Our old scan uses --full-root option in scancode
        test_scan_old = self.get_test_loc('utils/align-trees-simple-old.json')

        new_scan = models.Scan(test_scan_new)
        old_scan = models.Scan(test_scan_old)

        result_seg_new, result_seg_old = utils.align_trees(new_scan.files, old_scan.files)

        assert result_seg_new == 0
        # Our old scan uses --full-root option in scancode, hence the 5 segments that
        # can be removed.
        assert result_seg_old == 5

    def test_align_tress_zlib_failing(self):
        test_scan_new = self.get_test_loc('utils/align-trees-zlib-failing-new.json')
        test_scan_old = self.get_test_loc('utils/align-trees-zlib-failing-old.json')

        new_scan = models.Scan(test_scan_new)
        old_scan = models.Scan(test_scan_old)

        # test that the exception is raised
        with pytest.raises(utils.AlignmentException):
            result_seg_new, result_seg_old = utils.align_trees(new_scan.files, old_scan.files)

    def test_DeltaCode_check_moved_no_sha1_match(self):
        added_sha1 = 'a'
        removed_sha1 = 'b'

        new_added = models.File({'path': 'path/same.txt', 'sha1': 'a', 'name': 'same.txt'})

        added_delta = deltacode.Delta(new_added, None, 'added')
        added_deltas = [added_delta]

        old_removed = models.File({'path': 'path/different.txt', 'sha1': 'b', 'name': 'different.txt'})

        removed_delta = deltacode.Delta(None, old_removed, 'removed')
        removed_deltas = [removed_delta]

        result = utils.check_moved(added_sha1, added_deltas, removed_sha1, removed_deltas)

        assert result == False

    def test_DeltaCode_check_moved_1_sha1_match(self):
        added_sha1 = 'a'
        removed_sha1 = 'a'

        new_added = models.File({'path': 'path/same.txt', 'sha1': 'a', 'name': 'same.txt'})

        added_delta = deltacode.Delta(new_added, None, 'added')
        added_deltas = [added_delta]

        old_removed = models.File({'path': 'path/same.txt', 'sha1': 'a', 'name': 'same.txt'})

        removed_delta = deltacode.Delta(None, old_removed, 'removed')
        removed_deltas = [removed_delta]

        result = utils.check_moved(added_sha1, added_deltas, removed_sha1, removed_deltas)

        assert result == True

    def test_DeltaCode_check_moved_1_sha1_match_different_names(self):
        added_sha1 = 'a'
        removed_sha1 = 'a'

        new_added = models.File({'path': 'path/same.txt', 'sha1': 'a', 'name': 'same.txt'})

        added_delta = deltacode.Delta(new_added, None, 'added')
        added_deltas = [added_delta]

        old_removed = models.File({'path': 'path/different.txt', 'sha1': 'a', 'name': 'different.txt'})

        removed_delta = deltacode.Delta(None, old_removed, 'removed')
        removed_deltas = [removed_delta]

        result = utils.check_moved(added_sha1, added_deltas, removed_sha1, removed_deltas)

        assert result == None

    def test_DeltaCode_check_moved_2_sha1_matches(self):
        added_sha1 = 'a'
        removed_sha1 = 'a'

        new_added_01 = models.File({'path': 'pathA/same.txt', 'sha1': 'a', 'name': 'same.txt'})
        new_added_02 = models.File({'path': 'pathB/same.txt', 'sha1': 'a', 'name': 'same.txt'})

        added_delta_01 = deltacode.Delta(new_added_01, None, 'added')
        added_delta_02 = deltacode.Delta(new_added_02, None, 'added')
        added_deltas = [added_delta_01, added_delta_02]

        old_removed = models.File({'path': 'path/same.txt', 'sha1': 'a', 'name': 'same.txt'})

        removed_delta = deltacode.Delta(None, old_removed, 'removed')
        removed_deltas = [removed_delta]

        result = utils.check_moved(added_sha1, added_deltas, removed_sha1, removed_deltas)

        assert result == False
