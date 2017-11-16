from __future__ import absolute_import, print_function, unicode_literals, division

import json
import os

import pytest

from click.testing import CliRunner

from commoncode.testcase import FileBasedTesting
from deltacode import DeltaCode
from deltacode import models


def get_to_dict_original_path(data, scan, path):
    """
    Takes (1) an OrderedDict that contains a nested OrderedDict of Delta
    objects, (2) the identifier of which of a pair of scans is being queried
    (i.e., 'old' or 'new'), and (3) the value of the 'path' key, and returns
    the value of the related 'original_path' key, which is then compared below
    in the set of assertions testing that the 'original_path' key/value pair
    is present and that the value is correct.
    """
    for categories in data['deltas']:
        for deltaObjects in data['deltas'][categories]:
            if deltaObjects[scan] and deltaObjects[scan]['path'] == path:
                return deltaObjects[scan]['original_path']


class TestModels(FileBasedTesting):

    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_Scan_load_files_fails_when_files_not_equal(self):
        test_file = self.get_test_loc('models/scan/files-mismatch.json')

        with pytest.raises(AssertionError):
            result = models.Scan(test_file)

    def test_Scan_load_files_fails_when_counts_not_equal(self):
        test_file = self.get_test_loc('models/scan/files-count-mismatch.json')

        with pytest.raises(AssertionError):
            result = models.Scan(test_file)

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

        with pytest.raises(models.ScancodeVersionAttributeException):
            invalid_result = models.Scan(invalid_path)

    def test_Scan_old_version(self):
        invalid_path = self.get_test_loc('models/scan/old-version.json')

        with pytest.raises(models.ScancodeOldVersionException):
            invalid_result = models.Scan(invalid_path)

    def test_Scan_info_not_selected(self):
        invalid_path = self.get_test_loc('models/scan/info-not-selected.json')

        with pytest.raises(models.ScancodeInfoAttributeException):
            invalid_result = models.Scan(invalid_path)

    def test_Scan_invalid_path(self):
        test_path = '/some/invalid/path.json'

        result = models.Scan(test_path)

        assert result.path == '/some/invalid/path.json'
        assert result.files_count == None
        assert result.files == None
        assert result.options == None

    def test_Scan_empty_path(self):
        result = models.Scan('')

        assert result.path == ''
        assert result.files_count == None
        assert result.files == None
        assert result.options == None

    def test_Scan_None_path(self):
        result = models.Scan(None)

        assert result.path == ''
        assert result.files_count == None
        assert result.files == None
        assert result.options == None

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

    def test_to_dict_original_path_full_root(self):
        test_scan_new = self.get_test_loc('models/scan/align-trees-simple-new.json')
        # Our old scan uses --full-root option in scancode
        test_scan_old = self.get_test_loc('models/scan/align-trees-simple-old.json')

        delta = DeltaCode(test_scan_new, test_scan_old)
        data = delta.to_dict()

        assert get_to_dict_original_path(data, 'new', 'samples/JGroups/EULA') == \
                                 'samples/JGroups/EULA'
        assert get_to_dict_original_path(data, 'old', 'samples/JGroups/EULA') == \
                                 '/Users/sesser/code/nexb/scancode-toolkit/samples/JGroups/EULA'

        assert get_to_dict_original_path(data, 'new', 'samples/zlib/dotzlib/LICENSE_1_0.txt') == \
                                 'samples/zlib/dotzlib/LICENSE_1_0.txt'
        assert get_to_dict_original_path(data, 'old', 'samples/zlib/dotzlib/LICENSE_1_0.txt') == \
                                 '/Users/sesser/code/nexb/scancode-toolkit/samples/zlib/dotzlib/LICENSE_1_0.txt'

    def test_to_dict_original_path_added1(self):
        test_scan_new = self.get_test_loc('models/scan/new_added1.json')
        test_scan_old = self.get_test_loc('models/scan/old_added1.json')

        delta = DeltaCode(test_scan_new, test_scan_old)
        data = delta.to_dict()

        assert get_to_dict_original_path(data, 'new', 'a/a3.py') == \
                                 'codebase_01_1_file_added/a/a3.py'
        assert get_to_dict_original_path(data, 'old', 'a/a3.py') == \
                                 'codebase_01/a/a3.py'

        assert get_to_dict_original_path(data, 'new', 'b/b4.py') == \
                                 'codebase_01_1_file_added/b/b4.py'
        assert get_to_dict_original_path(data, 'old', 'b/b4.py') == \
                                 'codebase_01/b/b4.py'

        assert get_to_dict_original_path(data, 'new', 'a/a2.py') == \
                                 'codebase_01_1_file_added/a/a2.py'
        assert get_to_dict_original_path(data, 'old', 'a/a2.py') == \
                                 'codebase_01/a/a2.py'

    def test_to_dict_original_path_zlib(self):
        test_scan_new = self.get_test_loc('models/scan/zlib-1.2.11-clip_scan.json')
        test_scan_old = self.get_test_loc('models/scan/zlib-1.2.9-clip_scan.json')

        delta = DeltaCode(test_scan_new, test_scan_old)
        data = delta.to_dict()

        assert get_to_dict_original_path(data, 'new', 'contrib/ada/read.adb') == \
                                 'zlib-1.2.11/contrib/ada/read.adb'
        assert get_to_dict_original_path(data, 'old', 'contrib/ada/read.adb') == \
                                 'zlib-1.2.9/contrib/ada/read.adb'

        assert get_to_dict_original_path(data, 'new', 'contrib/masmx86/bld_ml32.bat') == \
                                 'zlib-1.2.11/contrib/masmx86/bld_ml32.bat'
        assert get_to_dict_original_path(data, 'old', 'contrib/masmx86/bld_ml32.bat') == \
                                 'zlib-1.2.9/contrib/masmx86/bld_ml32.bat'

        assert get_to_dict_original_path(data, 'new', 'contrib/masmx64/readme.txt') == \
                                 'zlib-1.2.11/contrib/masmx64/readme.txt'
        assert get_to_dict_original_path(data, 'old', 'contrib/masmx64/readme.txt') == \
                                 'zlib-1.2.9/contrib/masmx64/readme.txt'

    def test_to_dict_original_path_dropbear(self):
        test_scan_new = self.get_test_loc('models/scan/dropbear-2017.75-clip_scan.json')
        test_scan_old = self.get_test_loc('models/scan/dropbear-2016.74-clip_scan.json')

        delta = DeltaCode(test_scan_new, test_scan_old)
        data = delta.to_dict()

        assert get_to_dict_original_path(data, 'new', 'dbutil.h') == \
                                 'dropbear-2017.75/dbutil.h'
        assert get_to_dict_original_path(data, 'old', 'dbutil.h') == \
                                 'dropbear-2016.74/dbutil.h'

        assert get_to_dict_original_path(data, 'new', 'libtomcrypt/src/encauth/gcm/gcm_reset.c') == \
                                 'dropbear-2017.75/libtomcrypt/src/encauth/gcm/gcm_reset.c'
        assert get_to_dict_original_path(data, 'old', 'libtomcrypt/src/encauth/gcm/gcm_reset.c') == \
                                 'dropbear-2016.74/libtomcrypt/src/encauth/gcm/gcm_reset.c'

        assert get_to_dict_original_path(data, 'new', 'install-sh') == \
                                 'dropbear-2017.75/install-sh'
        assert get_to_dict_original_path(data, 'old', 'install-sh') == \
                                 'dropbear-2016.74/install-sh'

    def test_to_dict_original_path_openssl(self):
        test_scan_new = self.get_test_loc('models/scan/openssl-1.1.0f-clip_scan.json')
        test_scan_old = self.get_test_loc('models/scan/openssl-1.1.0e-clip_scan.json')

        delta = DeltaCode(test_scan_new, test_scan_old)
        data = delta.to_dict()

        assert get_to_dict_original_path(data, 'new', 'crypto/ec/ecdh_ossl.c') == \
                                 'openssl-1.1.0f/crypto/ec/ecdh_ossl.c'
        assert get_to_dict_original_path(data, 'old', 'crypto/ec/ecdh_ossl.c') == \
                                 'openssl-1.1.0e/crypto/ec/ecdh_ossl.c'

        assert get_to_dict_original_path(data, 'new', 'test/recipes/80-test_ssl_old.t') == \
                                 'openssl-1.1.0f/test/recipes/80-test_ssl_old.t'
        assert get_to_dict_original_path(data, 'old', 'test/recipes/80-test_ssl_old.t') == \
                                 'openssl-1.1.0e/test/recipes/80-test_ssl_old.t'

        assert get_to_dict_original_path(data, 'new', 'doc/apps/ts.pod') == \
                                 'openssl-1.1.0f/doc/apps/ts.pod'
        assert get_to_dict_original_path(data, 'old', 'doc/apps/ts.pod') == \
                                 'openssl-1.1.0e/doc/apps/ts.pod'
