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

import json
import os

import pytest

from click.testing import CliRunner

from commoncode.testcase import FileBasedTesting
from deltacode import DeltaCode
from deltacode import models

class TestModels(FileBasedTesting):

    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_Scan_load_files_fails_when_files_not_equal(self):
        test_file = self.get_test_loc('models/scan/files-mismatch.json')

        result = models.Scan(test_file)

        expected_result = ["The number of files calculated with 'len(files)' does not equal the ScanCode 'files_count' value for the scan with path = " + test_file + "."]

        assert result.errors == expected_result

    def test_Scan_load_files_fails_when_counts_not_equal(self):
        test_file = self.get_test_loc('models/scan/files-count-mismatch.json')

        result = models.Scan(test_file)

        expected_result = ["The number of files calculated with 'len(files)' does not equal the ScanCode 'files_count' value for the scan with path = " + test_file + "."]

        assert result.errors == expected_result

    def test_Scan_index_files_simple(self):
        test_files = [models.File({'path': 'path1/a'}), models.File({'path': 'path1/b'})]

        scan = models.Scan()
        scan.files = test_files

        index = scan.index_files()

        assert index.get('path1/a') == [test_files[0]]
        assert index.get('path1/b') == [test_files[1]]

    def test_Scan_index_files_key_path(self):
        test_files = [models.File({'path': 'path1/a'}), models.File({'path': 'path1/b'})]

        scan = models.Scan()
        scan.files = test_files

        index = scan.index_files('path')

        assert index.get('path1/a') == [test_files[0]]
        assert index.get('path1/b') == [test_files[1]]

    def test_Scan_index_files_key_missing(self):
        test_files = [models.File({'path': 'path1/a'}), models.File({'path': 'path1/b'})]

        scan = models.Scan()
        scan.files = test_files

        with pytest.raises(AttributeError):
            index = scan.index_files('missing')

    def test_Scan_index_files_key_sha1_foo(self):
        test_files = [models.File({'path': 'path1/a/foo', 'sha1': '3340d86b1da9323067db8022f86dc97cfccee1d0'}),
                      models.File({'path': 'path1/b/foo', 'sha1': '3340d86b1da9323067db8022f86dc97cfccee1d0'})]

        scan = models.Scan()
        scan.files = test_files

        index = scan.index_files('sha1')

        result = test_files

        assert len(index.get('3340d86b1da9323067db8022f86dc97cfccee1d0')) == 2
        assert index.get('3340d86b1da9323067db8022f86dc97cfccee1d0') == result

    def test_Scan_index_files_key_sha1_multiple_copies(self):
        test_file = self.get_test_loc('models/scan/multiple_copies_01-i_scan.json')

        scan = models.Scan(test_file)

        index = scan.index_files('sha1')

        assert len(index.get('84b647771481d39dd3a53f6dc210c26abac37748')) == 3
        assert len(index.get('310797523e47db8481aeb06f1634317285115091')) == 3
        assert len(index.get('fd5d3589c825f448546d7dcec36da3e567d35fe9')) == 3
        assert len(index.get('6f71666c46446c29d3f45feef5419ae76fb86a5b')) == 3

        for each in index.get('84b647771481d39dd3a53f6dc210c26abac37748'):
            assert each.sha1 == '84b647771481d39dd3a53f6dc210c26abac37748'

        for each in index.get('310797523e47db8481aeb06f1634317285115091'):
            assert each.sha1 == '310797523e47db8481aeb06f1634317285115091'

        for each in index.get('fd5d3589c825f448546d7dcec36da3e567d35fe9'):
            assert each.sha1 == 'fd5d3589c825f448546d7dcec36da3e567d35fe9'

        for each in index.get('6f71666c46446c29d3f45feef5419ae76fb86a5b'):
            assert each.sha1 == '6f71666c46446c29d3f45feef5419ae76fb86a5b'

    def test_Scan_index_files_key_name_multiple_copies(self):
        test_file = self.get_test_loc('models/scan/multiple_copies_01-i_scan.json')

        scan = models.Scan(test_file)

        index = scan.index_files('name')

        assert len(index.get('a1.py')) == 3
        assert len(index.get('a2.py')) == 3
        assert len(index.get('a3.py')) == 3
        assert len(index.get('a4.py')) == 3

        for each in index.get('a1.py'):
            assert each.name == 'a1.py'

        for each in index.get('a2.py'):
            assert each.name == 'a2.py'

        for each in index.get('a3.py'):
            assert each.name == 'a3.py'

        for each in index.get('a4.py'):
            assert each.name == 'a4.py'

    def test_Scan_index_files_large_openssl_key_path(self):
        test_file = self.get_test_loc('models/scan/openssl-1.1.0f-clip_scan.json')

        scan = models.Scan(test_file)

        index = scan.index_files('path')
        assert len(index.get('openssl-1.1.0f/crypto/rc2')) == 1
        assert len(index.get('openssl-1.1.0f/crypto/include/internal/x509_int.h')) == 1
        assert len(index.get('openssl-1.1.0f/crypto/ec/asm/ecp_nistz256-armv4.pl')) == 1
        assert len(index.get('openssl-1.1.0f/test/testreq2.pem')) == 1

    def test_Scan_index_files_large_openssl_key_sha1(self):
        test_file = self.get_test_loc('models/scan/openssl-1.1.0f-clip_scan.json')

        scan = models.Scan(test_file)

        index = scan.index_files('sha1')

        assert len(index.get('478330af84ea74932db60e35533215de649a06c4')) == 2
        for each in index.get('478330af84ea74932db60e35533215de649a06c4'):
            assert each.sha1 == '478330af84ea74932db60e35533215de649a06c4'

        assert len(index.get('cd5cb64b8c0d5654b5a768d820a2b1ec03ec365a')) == 2
        for each in index.get('cd5cb64b8c0d5654b5a768d820a2b1ec03ec365a'):
            assert each.sha1 == 'cd5cb64b8c0d5654b5a768d820a2b1ec03ec365a'

    def test_Scan_index_files_large_openssl_key_name(self):
        test_file = self.get_test_loc('models/scan/openssl-1.1.0f-clip_scan.json')

        scan = models.Scan(test_file)

        index = scan.index_files('name')

        assert len(index.get('dh1024.pem')) == 2
        for each in index.get('dh1024.pem'):
            assert each.name == 'dh1024.pem'

        assert len(index.get('dh2048.pem')) == 2
        for each in index.get('dh2048.pem'):
            assert each.name == 'dh2048.pem'

    def test_Scan_index_files_large_dropbear_key_path(self):
        test_file = self.get_test_loc('models/scan/dropbear-2017.75-clip_scan.json')

        scan = models.Scan(test_file)

        index = scan.index_files('path')

        assert len(index.get('dropbear-2017.75/libtomcrypt/src/modes/cfb/cfb_encrypt.c')) == 1
        assert index.get('dropbear-2017.75/libtomcrypt/src/modes/cfb/cfb_encrypt.c')[0].path == 'dropbear-2017.75/libtomcrypt/src/modes/cfb/cfb_encrypt.c'

        assert len(index.get('dropbear-2017.75/dss.h')) == 1
        assert index.get('dropbear-2017.75/dss.h')[0].path == 'dropbear-2017.75/dss.h'

    def test_Scan_index_files_large_dropbear_key_sha1(self):
        test_file = self.get_test_loc('models/scan/dropbear-2017.75-clip_scan.json')

        scan = models.Scan(test_file)

        index = scan.index_files('sha1')

        assert len(index.get(None)) == 78
        for each in index.get(None):
            assert each.sha1 == None

        assert len(index.get('71cb8d2a576df3157730d5353eb81f6d6feb328c')) == 1
        for each in index.get('71cb8d2a576df3157730d5353eb81f6d6feb328c'):
            assert each.sha1 == '71cb8d2a576df3157730d5353eb81f6d6feb328c'

    def test_Scan_index_files_large_dropbear_key_name(self):
        test_file = self.get_test_loc('models/scan/dropbear-2017.75-clip_scan.json')

        scan = models.Scan(test_file)

        index = scan.index_files('name')

        assert len(index.get('TODO')) == 2
        for each in index.get('TODO'):
            assert each.name == 'TODO'

        assert len(index.get('multi.c')) == 2
        for each in index.get('multi.c'):
            assert each.name == 'multi.c'

    def test_Scan_index_files_large_zlib_key_path(self):
        test_file = self.get_test_loc('models/scan/zlib-1.2.11-clip_scan.json')

        scan = models.Scan(test_file)

        index = scan.index_files('path')

        assert len(index.get('zlib-1.2.11/contrib/ada/readme.txt')) == 1
        for each in index.get('zlib-1.2.11/contrib/ada/readme.txt'):
            assert each.path == 'zlib-1.2.11/contrib/ada/readme.txt'

        assert len(index.get('zlib-1.2.11/zutil.c')) == 1
        for each in index.get('zlib-1.2.11/zutil.c'):
            assert each.path == 'zlib-1.2.11/zutil.c'

    def test_Scan_index_files_large_zlib_key_sha1(self):
        test_file = self.get_test_loc('models/scan/zlib-1.2.11-clip_scan.json')

        scan = models.Scan(test_file)

        index = scan.index_files('sha1')

        assert len(index.get('0ef05b0d12bf2cfbbf1aa84cff0e8dcf4fc5b731')) == 2
        for each in index.get('0ef05b0d12bf2cfbbf1aa84cff0e8dcf4fc5b731'):
            assert each.sha1 == '0ef05b0d12bf2cfbbf1aa84cff0e8dcf4fc5b731'

        assert len(index.get('ddf83b34d4c7d41ace39f96b5cb13fb390c8d2eb')) == 2
        for each in index.get('ddf83b34d4c7d41ace39f96b5cb13fb390c8d2eb'):
            assert each.sha1 == 'ddf83b34d4c7d41ace39f96b5cb13fb390c8d2eb'

    def test_Scan_index_files_large_zlib_key_name(self):
        test_file = self.get_test_loc('models/scan/zlib-1.2.11-clip_scan.json')

        scan = models.Scan(test_file)

        index = scan.index_files('name')

        assert len(index.get('zfstream.h')) == 2
        for each in index.get('zfstream.h'):
            assert each.name == 'zfstream.h'

        assert len(index.get('make_vms.com')) == 2
        for each in index.get('make_vms.com'):
            assert each.name == 'make_vms.com'

    def test_Scan_get_options_license_yes(self):
        test_file = self.get_test_loc('models/scan/samples-clip-json-pp.json')

        scan = models.Scan(test_file)

        assert scan.options['--license'] == True
        assert scan.options['--license-score'] == 0
        assert scan.options['--format'] == 'json-pp'
        assert scan.options['--package'] == True
        assert scan.options['--copyright'] == True
        assert scan.options['--info'] == True

    def test_Scan_get_options_license_no(self):
        test_file = self.get_test_loc('models/scan/samples-i-no-json-pp.json')

        scan = models.Scan(test_file)

        assert scan.options.get('--license', None) == None
        assert scan.options['--license-score'] == 0
        assert scan.options['--format'] == 'json'
        assert scan.options.get('--package', None) == None
        assert scan.options.get('--copyright', None) == None
        assert scan.options['--info'] == True

    def test_Scan_valid_scanfile(self):
        valid_paths = [
            self.get_test_loc('models/scan/well-formed-scan.json'),
            self.get_test_loc('models/scan/this-is-json.txt')
        ]

        valid_results = [models.Scan(f) for f in valid_paths]

        for result, path in zip(valid_results, valid_paths):
            assert result.path == path
            assert result.files != None
            assert result.files_count != None and isinstance(result.files_count, int)

    def test_Scan_malformed_json(self):
        invalid_path = self.get_test_loc('models/scan/malformed.json')
        with pytest.raises(ValueError):
            invalid_result = models.Scan(invalid_path)

    def test_Scan_empty_text(self):
        invalid_path = self.get_test_loc('models/scan/empty.txt')
        with pytest.raises(ValueError):
            invalid_result = models.Scan(invalid_path)

    def test_Scan_empty_json(self):
        invalid_path = self.get_test_loc('models/scan/empty.json')

        with pytest.raises(models.ScanException) as e:
            invalid_result = models.Scan(invalid_path)

        normalized_path = os.path.abspath(invalid_path)
        assert str(e.value) == 'JSON file \'' + normalized_path + '\' is missing the \'scancode_version\' attribute.'

    def test_Scan_old_version(self):
        invalid_path = self.get_test_loc('models/scan/old-version.json')

        with pytest.raises(models.ScanException) as e:
            invalid_result = models.Scan(invalid_path)

        normalized_path = os.path.abspath(invalid_path)
        assert str(e.value) == 'JSON file \'' + normalized_path + '\' was created with an old version of ScanCode.'

    def test_Scan_info_not_selected(self):
        invalid_path = self.get_test_loc('models/scan/info-not-selected.json')

        with pytest.raises(models.ScanException) as e:
            invalid_result = models.Scan(invalid_path)

        normalized_path = os.path.abspath(invalid_path)
        assert str(e.value) == 'JSON file \'' + normalized_path + '\' is missing the \'scancode_options/--info\' attribute.'

    def test_Scan_invalid_path(self):
        test_path = '/some/invalid/path.json'

        result = models.Scan(test_path)

        assert result.path == ''
        assert result.files_count == 0
        assert result.files == []
        assert result.options == {}

    def test_Scan_empty_path(self):
        result = models.Scan('')

        assert result.path == ''
        assert result.files_count == 0
        assert result.files == []
        assert result.options == {}

    def test_Scan_None_path(self):
        result = models.Scan(None)

        assert result.path == ''
        assert result.files_count == 0
        assert result.files == []
        assert result.options == {}

    def test_License_to_dict_simple(self):
        data = {
            "key": "apache-2.0",
            "score": 80.0,
            "short_name": "Apache 2.0",
            "category": "Permissive",
            "owner": "Apache Software Foundation",
            "homepage_url": "http://www.apache.org/licenses/",
            "text_url": "http://www.apache.org/licenses/LICENSE-2.0",
            "reference_url": "https://enterprise.dejacode.com/urn/urn:dje:license:apache-2.0",
            "spdx_license_key": "Apache-2.0",
            "spdx_url": "https://spdx.org/licenses/Apache-2.0",
            "start_line": 3,
            "end_line": 3,
            "matched_rule": {
                "identifier": "apache-2.0_57.RULE",
                "license_choice": False,
                "licenses": [
                    "apache-2.0"
                ]
            }
        }

        expected = {
            'key': 'apache-2.0',
            'score': 80.0,
            'short_name': 'Apache 2.0',
            'category': 'Permissive',
            'owner': 'Apache Software Foundation'
        }

        result = models.License(data).to_dict()

        assert result == expected
        with pytest.raises(AttributeError):
            assert result.spdx_license_key == "Apache-2.0"

    def test_License_to_dict_empty(self):
        result = models.License().to_dict()

        for k,v in result.items():
            assert v == None

    def test_License_object_simple(self):
        data = {
            "key": "apache-2.0",
            "score": 80.0,
            "short_name": "Apache 2.0",
            "category": "Permissive",
            "owner": "Apache Software Foundation",
            "homepage_url": "http://www.apache.org/licenses/",
            "text_url": "http://www.apache.org/licenses/LICENSE-2.0",
            "dejacode_url": "https://enterprise.dejacode.com/urn/urn:dje:license:apache-2.0",
            "spdx_license_key": "Apache-2.0",
            "spdx_url": "https://spdx.org/licenses/Apache-2.0",
            "start_line": 3,
            "end_line": 3,
            "matched_rule": {
                "identifier": "apache-2.0_57.RULE",
                "license_choice": False,
                "licenses": [
                    "apache-2.0"
                ]
            }
        }

        result = models.License(data)

        assert result.key == 'apache-2.0'
        assert result.score == 80
        assert result.category == 'Permissive'
        with pytest.raises(AttributeError):
            assert result.spdx_license_key == "Apache-2.0"

    def test_License_object_empty(self):
        result = models.License()

        for attr, value in vars(result).items():
            assert value == None

    def test_File_to_dict_simple_w_license(self):
        data = {
            'path': 'a/b/file1.txt',
            'type': 'file',
            'name': 'file1.txt',
            'size': 20,
            'sha1': '26d82f1931cbdbd83c2a6871b2cecd5cbcc8c26b',
            'licenses': [
                {
                    "key": "apache-2.0",
                    "score": 80.0,
                    "short_name": "Apache 2.0",
                    "category": "Permissive",
                    "owner": "Apache Software Foundation",
                    "homepage_url": "http://www.apache.org/licenses/",
                    "text_url": "http://www.apache.org/licenses/LICENSE-2.0",
                    "reference_url": "https://enterprise.dejacode.com/urn/urn:dje:license:apache-2.0",
                    "spdx_license_key": "Apache-2.0",
                    "spdx_url": "https://spdx.org/licenses/Apache-2.0",
                    "start_line": 3,
                    "end_line": 3,
                    "matched_rule": {
                        "identifier": "apache-2.0_57.RULE",
                        "license_choice": False,
                        "licenses": [
                            "apache-2.0"
                        ]
                    }
                }
            ],
        }

        expected = {
            'path': 'a/b/file1.txt',
            'type': 'file',
            'name': 'file1.txt',
            'size': 20,
            'sha1': '26d82f1931cbdbd83c2a6871b2cecd5cbcc8c26b',
            'original_path': '',
           'licenses': [
               {
                   "key": "apache-2.0",
                   "score": 80.0,
                   "short_name": "Apache 2.0",
                   "category": "Permissive",
                   "owner": "Apache Software Foundation"
               }
           ]
        }

        result = models.File(data).to_dict()

        assert result == expected
        with pytest.raises(AttributeError):
            assert result.spdx_license_key == "Apache-2.0"

    def test_File_to_dict_simple(self):
        data = {
            'path': 'a/b/file1.txt',
            'type': 'file',
            'name': 'file1.txt',
            'size': 20,
            'sha1': '26d82f1931cbdbd83c2a6871b2cecd5cbcc8c26b',
        }

        expected = {
            'path': 'a/b/file1.txt',
            'type': 'file',
            'name': 'file1.txt',
            'size': 20,
            'sha1': '26d82f1931cbdbd83c2a6871b2cecd5cbcc8c26b',
            'original_path': ''
        }

        result = models.File(data).to_dict()

        assert result == expected

    def test_File_to_dict_empty(self):
        empty_file = models.File()

        expected = {
            'path': '',
            'type': '',
            'name': '',
            'size': '',
            'sha1': '',
            'original_path': ''
        }

        result = empty_file.to_dict()
        assert result == expected

    def test_File_create_object_license_one(self):
        data = {
            'path': 'a/b/file1.txt',
            'type': 'file',
            'name': 'file1.txt',
            'size': 20,
            'sha1': '26d82f1931cbdbd83c2a6871b2cecd5cbcc8c26b',
            'licenses': [
                {
                    "key": "apache-2.0",
                    "score": 80.0,
                    "short_name": "Apache 2.0",
                    "category": "Permissive",
                    "owner": "Apache Software Foundation",
                    "homepage_url": "http://www.apache.org/licenses/",
                    "text_url": "http://www.apache.org/licenses/LICENSE-2.0",
                    "reference_url": "https://enterprise.dejacode.com/urn/urn:dje:license:apache-2.0",
                    "spdx_license_key": "Apache-2.0",
                    "spdx_url": "https://spdx.org/licenses/Apache-2.0",
                    "start_line": 3,
                    "end_line": 3,
                    "matched_rule": {
                        "identifier": "apache-2.0_57.RULE",
                        "license_choice": False,
                        "licenses": [
                            "apache-2.0"
                        ]
                    }
                }
            ],
        }

        result = models.File(data)

        assert 'a/b/file1.txt' == result.path
        assert 'file' == result.type
        assert 'file1.txt' == result.name
        assert 20 == result.size
        assert '26d82f1931cbdbd83c2a6871b2cecd5cbcc8c26b' == result.sha1
        assert len(result.licenses) == 1
        assert result.licenses[0].key == 'apache-2.0'
        with pytest.raises(AttributeError):
            assert result.spdx_license_key == "Apache-2.0"

    def test_File_create_object_license_none(self):
        data = {
            'path': 'a/b/file1.txt',
            'type': 'file',
            'name': 'file1.txt',
            'size': 20,
            'sha1': '26d82f1931cbdbd83c2a6871b2cecd5cbcc8c26b',
            'licenses': [],
        }

        result = models.File(data)

        assert 'a/b/file1.txt' == result.path
        assert 'file' == result.type
        assert 'file1.txt' == result.name
        assert 20 == result.size
        assert '26d82f1931cbdbd83c2a6871b2cecd5cbcc8c26b' == result.sha1
        assert [] == result.licenses

    def test_File_create_object_license_missing(self):
        data = {
            'path': 'a/b/file1.txt',
            'type': 'file',
            'name': 'file1.txt',
            'size': 20,
            'sha1': '26d82f1931cbdbd83c2a6871b2cecd5cbcc8c26b',
        }

        result = models.File(data)

        assert [] == result.licenses

    def test_File_empty(self):
        empty_file = models.File()

        assert empty_file.path == ''
        assert empty_file.type == ''
        assert empty_file.name == ''
        assert empty_file.size == ''
        assert empty_file.sha1 == ''
        assert empty_file.licenses == []

    def test_File_create_object(self):
        data = {
            'path': 'a/b/file1.txt',
            'type': 'file',
            'name': 'file1.txt',
            'size': 20,
            'sha1': '26d82f1931cbdbd83c2a6871b2cecd5cbcc8c26b',
        }

        result = models.File(data)

        assert 'a/b/file1.txt' == result.path
        assert 'file' == result.type
        assert 'file1.txt' == result.name
        assert 20 == result.size
        assert '26d82f1931cbdbd83c2a6871b2cecd5cbcc8c26b' == result.sha1

    def test_File_size_difference(self):
        a = {'path': '', 'name': '', 'sha1':'', 'size': 4096}
        b = {'path': '', 'name': '', 'sha1':'', 'size': 4096}
        a_file = models.File(a)
        b_file = models.File(b)
        assert 0 == a_file.size_difference(b_file)
        b['size'] = 2048
        b_file = models.File(b)
        assert 2048 == a_file.size_difference(b_file)
        b['size'] = 8192
        b_file = models.File(b)
        assert -4096 == a_file.size_difference(b_file)
