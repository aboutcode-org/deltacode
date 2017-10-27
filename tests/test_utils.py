#
#  Copyright (c) 2015 nexB Inc. and others. All rights reserved.
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
