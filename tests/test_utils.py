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
import deltacode
from deltacode import utils
from deltacode import models


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

    def test_determine_license_diff_empty(self):
        test_delta = deltacode.Delta()

        utils.determine_license_diff(test_delta, set())

        assert test_delta.score == 0

    def test_determine_license_diff_non_modified(self):
        test_file = models.File({'path':'/test/path.txt', 'name': 'path.txt'})
        test_delta = deltacode.Delta(old_file=test_file)

        utils.determine_license_diff(test_delta, set())

        assert test_delta.score == 0
        assert len(test_delta.factors) == 0

    def test_determine_license_diff_no_license_key_value(self):
        test_file_new = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a',
            'original_path': ''
        })
        test_file_old = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a_modified',
            'original_path': ''
        })

        test_delta = deltacode.Delta(20, test_file_new, test_file_old)

        utils.determine_license_diff(test_delta, unique_categories)

        assert test_delta.score == 20
        assert len(test_delta.factors) == 0

    def test_determine_license_diff_no_license_changes(self):
        test_file_new = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a',
            'original_path': '',
            "licenses": [
                {
                    "key": "gpl-2.0",
                    "score": 70.0,
                    "short_name": "GPL 2.0",
                    "category": "Copyleft"
                }
            ]
        })
        test_file_old = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a_modified',
            'original_path': '',
            "licenses": [
                {
                    "key": "gpl-2.0",
                    "score": 70.0,
                    "short_name": "GPL 2.0",
                    "category": "Copyleft"
                }
            ]
        })

        test_delta = deltacode.Delta(20, test_file_new, test_file_old)

        utils.determine_license_diff(test_delta, unique_categories)

        assert test_delta.score == 20
        assert len(test_delta.factors) == 0

    def test_determine_license_diff_single_license_change(self):
        test_file_new = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a',
            'original_path': '',
            "licenses": [
                {
                    "key": "gpl-2.0",
                    "score": 70.0,
                    "short_name": "GPL 2.0",
                    "category": "Copyleft"
                }
            ]
        })
        test_file_old = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a_modified',
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

        test_delta = deltacode.Delta(20, test_file_new, test_file_old)

        utils.determine_license_diff(test_delta, unique_categories)

        assert test_delta.score == 50
        assert len(test_delta.factors) == 2
        for factor in ['license change', 'copyleft added']:
            assert factor in test_delta.factors

    def test_determine_license_diff_copyleft_license_info_added(self):
        test_file_new = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a',
            'original_path': '',
            "licenses": [
                {
                    "key": "gpl-2.0",
                    "score": 70.0,
                    "short_name": "GPL 2.0",
                    "category": "Copyleft"
                }
            ]
        })
        test_file_old = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a_modified',
            'original_path': '',
            "licenses": []
        })

        test_delta = deltacode.Delta(20, test_file_new, test_file_old)

        utils.determine_license_diff(test_delta, unique_categories)

        assert test_delta.score == 60
        assert len(test_delta.factors) == 2
        for factor in ['license info added', 'copyleft added']:
            assert factor in test_delta.factors

    def test_determine_license_diff_permissive_license_info_added(self):
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
        test_file_old = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a_modified',
            'original_path': '',
            "licenses": []
        })

        test_delta = deltacode.Delta(20, test_file_new, test_file_old)

        utils.determine_license_diff(test_delta, unique_categories)

        assert test_delta.score == 40
        assert len(test_delta.factors) == 1
        for factor in ['license info added']:
            assert factor in test_delta.factors

    def test_determine_license_diff_permissive_license_info_removed(self):
        test_file_new = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a',
            'original_path': '',
            "licenses": []
        })
        test_file_old = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a_modified',
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

        test_delta = deltacode.Delta(20, test_file_new, test_file_old)

        utils.determine_license_diff(test_delta, set())

        assert test_delta.score == 35
        assert len(test_delta.factors) == 1
        assert 'license info removed' in test_delta.factors

    def test_determine_license_diff_copyleft_license_info_removed(self):
        test_file_new = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a',
            'original_path': '',
            "licenses": []
        })
        test_file_old = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a_modified',
            'original_path': '',
            "licenses": [
                {
                    "key": "gpl-2.0",
                    "score": 70.0,
                    "short_name": "GPL 2.0",
                    "category": "Copyleft"
                }
            ]
        })

        test_delta = deltacode.Delta(20, test_file_new, test_file_old)

        utils.determine_license_diff(test_delta, set())

        assert test_delta.score == 35
        assert len(test_delta.factors) == 1
        assert 'license info removed' in test_delta.factors

    def test_determine_license_diff_one_license_added(self):
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
                },
                {
                    "key": "gpl-2.0",
                    "score": 70.0,
                    "short_name": "GPL 2.0",
                    "category": "Copyleft"
                }
            ]
        })
        test_file_old = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a_modified',
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

        test_delta = deltacode.Delta(20, test_file_new, test_file_old)

        utils.determine_license_diff(test_delta, unique_categories)

        assert test_delta.score == 50
        assert len(test_delta.factors) == 2
        for factor in ['license change', 'copyleft added']:
            assert factor in test_delta.factors

    def test_determine_license_diff_one_license_removed(self):
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
        test_file_old = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a_modified',
            'original_path': '',
            "licenses": [
                {
                    "key": "mit",
                    "score": 80.0,
                    "short_name": "MIT License",
                    "category": "Permissive"
                },
                {
                    "key": "gpl-2.0",
                    "score": 70.0,
                    "short_name": "GPL 2.0",
                    "category": "Copyleft"
                }
            ]
        })

        test_delta = deltacode.Delta(20, test_file_new, test_file_old)

        utils.determine_license_diff(test_delta, unique_categories)

        assert test_delta.score == 30
        assert len(test_delta.factors) == 1
        assert 'license change' in test_delta.factors

    def test_determine_license_diff_one_permissive_to_two_permissives(self):
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
                },
                {
                    "key": "apache-2.0",
                    "score": 40.0,
                    "short_name": "Apache 2.0",
                    "category": "Permissive"
                }
            ]
        })
        test_file_old = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a_modified',
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

        test_delta = deltacode.Delta(20, test_file_new, test_file_old)

        utils.determine_license_diff(test_delta, unique_categories)

        assert test_delta.score == 30
        assert len(test_delta.factors) == 1
        for factor in ['license change']:
            assert factor in test_delta.factors

    def test_determine_license_diff_two_permissives_to_one_permissive(self):
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
        test_file_old = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a_modified',
            'original_path': '',
            "licenses": [
                {
                    "key": "mit",
                    "score": 80.0,
                    "short_name": "MIT License",
                    "category": "Permissive"
                },
                {
                    "key": "apache-2.0",
                    "score": 40.0,
                    "short_name": "Apache 2.0",
                    "category": "Permissive"
                }
            ]
        })

        test_delta = deltacode.Delta(20, test_file_new, test_file_old)

        utils.determine_license_diff(test_delta, unique_categories)

        assert test_delta.score == 30
        assert len(test_delta.factors) == 1
        for factor in ['license change']:
            assert factor in test_delta.factors

    def test_determine_license_diff_one_permissive_to_six_copyleft_or_higher(self):
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
                },
                {
                    "key": "adapt-1.0",
                    "score": 15.0,
                    "short_name": "APL 1.0",
                    "category": "Copyleft",
                    "owner": "OSI - Open Source Initiative"
                },
                {
                    "key": "bittorrent-1.0",
                    "score": 100.0,
                    "short_name": "BitTorrent 1.0",
                    "category": "Copyleft Limited",
                    "owner": "BitTorrent, Inc."
                },
                {
                    "key": "bloomberg-blpapi",
                    "score": 100.0,
                    "short_name": "Bloomberg BLPAPI License",
                    "category": "Proprietary Free",
                    "owner": "Bloomberg Labs"
                },
                {
                    "key": "commercial-license",
                    "score": 55.0,
                    "short_name": "Commercial License",
                    "category": "Commercial",
                    "owner": "Unspecified"
                },
                {
                    "key": "wrox-download",
                    "score": 100.0,
                    "short_name": "Wrox Download Terms and Conditions",
                    "category": "Free Restricted",
                    "owner": "Wiley"
                },
                {
                    "key": "mozilla-ospl-1.0",
                    "score": 99.93,
                    "short_name": "Mozilla Open Software Patent License 1.0",
                    "category": "Patent License",
                    "owner": "Mozilla"
                }
            ]
        })
        test_file_old = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a_modified',
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

        test_delta = deltacode.Delta(20, test_file_new, test_file_old)

        utils.determine_license_diff(test_delta, unique_categories)

        assert test_delta.score == 150
        assert len(test_delta.factors) == 7

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
            assert factor in test_delta.factors

    def test_determine_license_diff_copyleft_to_different_copyleft(self):
        test_file_new = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a',
            'original_path': '',
            "licenses": [
                {
                    "key": "adapt-1.0",
                    "score": 15.0,
                    "short_name": "APL 1.0",
                    "category": "Copyleft",
                    "owner": "OSI - Open Source Initiative"
                }
            ]
        })
        test_file_old = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a_modified',
            'original_path': '',
            "licenses": [
                {
                    "key": "gpl-2.0",
                    "score": 70.0,
                    "short_name": "GPL 2.0",
                    "category": "Copyleft"
                }
            ]
        })

        test_delta = deltacode.Delta(20, test_file_new, test_file_old)

        utils.determine_license_diff(test_delta, unique_categories)

        assert test_delta.score == 30
        assert len(test_delta.factors) == 1
        assert 'license change' in test_delta.factors

    def test_determine_license_diff_copyleft_to_copyleft_limited(self):
        test_file_new = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a',
            'original_path': '',
            "licenses": [
                {
                    "key": "bittorrent-1.0",
                    "score": 100.0,
                    "short_name": "BitTorrent 1.0",
                    "category": "Copyleft Limited"
                }
            ]
        })
        test_file_old = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a_modified',
            'original_path': '',
            "licenses": [
                {
                    "key": "gpl-2.0",
                    "score": 70.0,
                    "short_name": "GPL 2.0",
                    "category": "Copyleft"
                }
            ]
        })

        test_delta = deltacode.Delta(20, test_file_new, test_file_old)

        utils.determine_license_diff(test_delta, unique_categories)

        assert test_delta.score == 30
        assert len(test_delta.factors) == 1
        for factor in ['license change']:
            assert factor in test_delta.factors

    def test_determine_copyright_diff_empty(self):
        test_delta = deltacode.Delta()

        utils.determine_copyright_diff(test_delta)

        assert test_delta.score == 0

    def test_determine_copyright_diff_non_modified(self):
        test_file = models.File({'path':'/test/path.txt', 'name': 'path.txt'})
        test_delta = deltacode.Delta(old_file=test_file)

        utils.determine_copyright_diff(test_delta)

        assert test_delta.score == 0
        assert len(test_delta.factors) == 0

    def test_determine_copyright_diff_no_copyright_key_value(self):
        test_file_new = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a',
            'original_path': ''
        })
        test_file_old = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a_modified',
            'original_path': ''
        })

        test_delta = deltacode.Delta(20, test_file_new, test_file_old)

        utils.determine_copyright_diff(test_delta)

        assert test_delta.score == 20
        assert len(test_delta.factors) == 0

    def test_determine_copyright_diff_no_copyright_changes(self):
        test_file_new = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a',
            'original_path': '',
            "copyrights": [
                {
                    "statements": [
                        "Copyright (c) 2017-2018 Francois Hennebique and others."
                    ],
                    "holders": [
                        "Francois Hennebique and others."
                    ]
                }
            ]
        })
        test_file_old = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a_modified',
            'original_path': '',
            "copyrights": [
                {
                    "statements": [
                        "Copyright (c) 2017-2018 Francois Hennebique and others."
                    ],
                    "holders": [
                        "Francois Hennebique and others."
                    ]
                }
            ]
        })

        test_delta = deltacode.Delta(20, test_file_new, test_file_old)

        utils.determine_copyright_diff(test_delta)

        assert test_delta.score == 20
        assert len(test_delta.factors) == 0

    def test_determine_copyright_diff_single_copyright_change(self):
        test_file_new = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a',
            'original_path': '',
            "copyrights": [
                {
                    "statements": [
                        "Copyright (c) 2015 Edouard-Leon Scott de Martinville."
                    ],
                    "holders": [
                        "Edouard-Leon Scott de Martinville."
                    ]
                }
            ]
        })
        test_file_old = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a_modified',
            'original_path': '',
            "copyrights": [
                {
                    "statements": [
                        "Copyright (c) 2017-2018 Francois Hennebique and others."
                    ],
                    "holders": [
                        "Francois Hennebique and others."
                    ]
                }
            ]
        })

        test_delta = deltacode.Delta(20, test_file_new, test_file_old)

        utils.determine_copyright_diff(test_delta)

        assert test_delta.score == 25
        assert len(test_delta.factors) == 1
        for factor in ['copyright change']:
            assert factor in test_delta.factors

    def test_determine_copyright_diff_copyright_info_added(self):
        test_file_new = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a',
            'original_path': '',
            "copyrights": [
                {
                    "statements": [
                        "Copyright (c) 2017-2018 Francois Hennebique and others."
                    ],
                    "holders": [
                        "Francois Hennebique and others."
                    ]
                }
            ]
        })
        test_file_old = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a_modified',
            'original_path': '',
            "copyrights": []
        })

        test_delta = deltacode.Delta(20, test_file_new, test_file_old)

        utils.determine_copyright_diff(test_delta)

        assert test_delta.score == 30
        assert len(test_delta.factors) == 1
        for factor in ['copyright info added']:
            assert factor in test_delta.factors

    def test_determine_copyright_diff_copyright_info_removed(self):
        test_file_new = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a',
            'original_path': '',
            "copyrights": []
        })
        test_file_old = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a_modified',
            'original_path': '',
            "copyrights": [
                {
                    "statements": [
                        "Copyright (c) 2017-2018 Francois Hennebique and others."
                    ],
                    "holders": [
                        "Francois Hennebique and others."
                    ]
                }
            ]
        })

        test_delta = deltacode.Delta(20, test_file_new, test_file_old)

        utils.determine_copyright_diff(test_delta)

        assert test_delta.score == 30
        assert len(test_delta.factors) == 1
        assert 'copyright info removed' in test_delta.factors

    def test_determine_copyright_diff_one_copyright_added(self):
        test_file_new = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a',
            'original_path': '',
            "copyrights": [
                {
                    "statements": [
                        "Copyright (c) 2017-2018 Francois Hennebique and others."
                    ],
                    "holders": [
                        "Francois Hennebique and others."
                    ]
                },
                {
                    "statements": [
                        "Copyright (c) 2015 Edouard-Leon Scott de Martinville."
                    ],
                    "holders": [
                        "Edouard-Leon Scott de Martinville."
                    ]
                }
            ]
        })
        test_file_old = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a_modified',
            'original_path': '',
            "copyrights": [
                {
                    "statements": [
                        "Copyright (c) 2017-2018 Francois Hennebique and others."
                    ],
                    "holders": [
                        "Francois Hennebique and others."
                    ]
                }
            ]
        })

        test_delta = deltacode.Delta(20, test_file_new, test_file_old)

        utils.determine_copyright_diff(test_delta)

        assert test_delta.score == 25
        assert len(test_delta.factors) == 1
        for factor in ['copyright change']:
            assert factor in test_delta.factors

    def test_determine_copyright_diff_one_copyright_removed(self):
        test_file_new = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a',
            'original_path': '',
            "copyrights": [
                {
                    "statements": [
                        "Copyright (c) 2017-2018 Francois Hennebique and others."
                    ],
                    "holders": [
                        "Francois Hennebique and others."
                    ]
                }
            ]
        })
        test_file_old = models.File({
            'path':'/test/path.txt',
            'name': 'path.txt',
            'sha1': 'a_modified',
            'original_path': '',
            "copyrights": [
                {
                    "statements": [
                        "Copyright (c) 2017-2018 Francois Hennebique and others."
                    ],
                    "holders": [
                        "Francois Hennebique and others."
                    ]
                },
                {
                    "statements": [
                        "Copyright (c) 2015 Edouard-Leon Scott de Martinville."
                    ],
                    "holders": [
                        "Edouard-Leon Scott de Martinville."
                    ]
                }
            ]
        })

        test_delta = deltacode.Delta(20, test_file_new, test_file_old)

        utils.determine_copyright_diff(test_delta)

        assert test_delta.score == 25
        assert len(test_delta.factors) == 1
        for factor in ['copyright change']:
            assert factor in test_delta.factors

    # xxx license/copyright tests to resume here.

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

        added_delta = deltacode.Delta(100, new_added, None)
        added_deltas = [added_delta]

        old_removed = models.File({'path': 'path/different.txt', 'sha1': 'b', 'name': 'different.txt'})

        removed_delta = deltacode.Delta(10, None, old_removed)
        removed_deltas = [removed_delta]

        result = utils.check_moved(added_sha1, added_deltas, removed_sha1, removed_deltas)

        assert result == False

    def test_DeltaCode_check_moved_1_sha1_match(self):
        added_sha1 = 'a'
        removed_sha1 = 'a'

        new_added = models.File({'path': 'path/same.txt', 'sha1': 'a', 'name': 'same.txt'})

        added_delta = deltacode.Delta(100, new_added, None)
        added_deltas = [added_delta]

        old_removed = models.File({'path': 'path/same.txt', 'sha1': 'a', 'name': 'same.txt'})

        removed_delta = deltacode.Delta(10, None, old_removed)
        removed_deltas = [removed_delta]

        result = utils.check_moved(added_sha1, added_deltas, removed_sha1, removed_deltas)

        assert result == True

    def test_DeltaCode_check_moved_1_sha1_match_different_names(self):
        added_sha1 = 'a'
        removed_sha1 = 'a'

        new_added = models.File({'path': 'path/same.txt', 'sha1': 'a', 'name': 'same.txt'})

        added_delta = deltacode.Delta(100, new_added, None)
        added_deltas = [added_delta]

        old_removed = models.File({'path': 'path/different.txt', 'sha1': 'a', 'name': 'different.txt'})

        removed_delta = deltacode.Delta(10, None, old_removed)
        removed_deltas = [removed_delta]

        result = utils.check_moved(added_sha1, added_deltas, removed_sha1, removed_deltas)

        assert result == None

    def test_DeltaCode_check_moved_2_sha1_matches(self):
        added_sha1 = 'a'
        removed_sha1 = 'a'

        new_added_01 = models.File({'path': 'pathA/same.txt', 'sha1': 'a', 'name': 'same.txt'})
        new_added_02 = models.File({'path': 'pathB/same.txt', 'sha1': 'a', 'name': 'same.txt'})

        added_delta_01 = deltacode.Delta(100, new_added_01, None)
        added_delta_02 = deltacode.Delta(100, new_added_02, None)
        added_deltas = [added_delta_01, added_delta_02]

        old_removed = models.File({'path': 'path/same.txt', 'sha1': 'a', 'name': 'same.txt'})

        removed_delta = deltacode.Delta(10, None, old_removed)
        removed_deltas = [removed_delta]

        result = utils.check_moved(added_sha1, added_deltas, removed_sha1, removed_deltas)

        assert result == False
