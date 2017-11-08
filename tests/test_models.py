from __future__ import absolute_import, print_function, unicode_literals, division


import os

import pytest

from click.testing import CliRunner

from commoncode.testcase import FileBasedTesting
from deltacode import models

class TestModels(FileBasedTesting):

    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_Scan_ecos_failing_scans(self):
        new_scan = self.get_test_loc('models/ecos-failed-counts-assertion-new.json')
        old_scan = self.get_test_loc('models/ecos-failed-counts-assertion-old.json')
        
        new = models.Scan(new_scan)
        old = models.Scan(old_scan)

        new_index = new.index_files()
        old_index = old.index_files()

        assert new.files_count == 11408
        assert old.files_count == 8631
        
        assert len(new.files) == new.files_count
        assert len(old.files) == old.files_count
        
        assert len(new_index.keys()) == new.files_count
        assert len(old_index.keys()) == old.files_count

        for f in new.files:
            assert f.type == 'file' or f.type == 'directory'
        
        for f in old.files:
            assert f.type == 'file' or f.type == 'directory'

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

        assert index.get('path1/a') == test_files[0]
        assert index.get('path1/b') == test_files[1]

    def test_Scan_index_files_key_path(self):
        test_files = [models.File({'path': 'path1/a'}), models.File({'path': 'path1/b'})]

        scan = models.Scan()
        scan.files = test_files

        index = scan.index_files('path')

        assert index.get('path1/a') == test_files[0]
        assert index.get('path1/b') == test_files[1]

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

        assert index.get('3340d86b1da9323067db8022f86dc97cfccee1d0').path == 'path1/b/foo'

    def test_Scan_index_files_key_sha1_multiple_copies(self):
        test_file = self.get_test_loc('models/scan/multiple_copies_01-i_scan.json')

        scan = models.Scan(test_file)

        index = scan.index_files('sha1')

        assert index.get('84b647771481d39dd3a53f6dc210c26abac37748').path == 'multiple_copies_01/a_nested_copy/level_2/a1.py'
        assert index.get('310797523e47db8481aeb06f1634317285115091').path == 'multiple_copies_01/a_nested_copy/level_2/a2.py'
        assert index.get('fd5d3589c825f448546d7dcec36da3e567d35fe9').path == 'multiple_copies_01/a_nested_copy/level_2/a3.py'
        assert index.get('6f71666c46446c29d3f45feef5419ae76fb86a5b').path == 'multiple_copies_01/a_nested_copy/level_2/a4.py'

    def test_Scan_index_files_key_name_multiple_copies(self):
        test_file = self.get_test_loc('models/scan/multiple_copies_01-i_scan.json')

        scan = models.Scan(test_file)

        index = scan.index_files('name')

        assert index.get('a1.py').sha1 == '84b647771481d39dd3a53f6dc210c26abac37748'
        assert index.get('a2.py').sha1 == '310797523e47db8481aeb06f1634317285115091'
        assert index.get('a3.py').sha1 == 'fd5d3589c825f448546d7dcec36da3e567d35fe9'
        assert index.get('a4.py').sha1 == '6f71666c46446c29d3f45feef5419ae76fb86a5b'

    def test_Scan_index_files_large_openssl_key_path(self):
        test_file = self.get_test_loc('models/scan/openssl-1.1.0f-clip_scan.json')

        scan = models.Scan(test_file)

        index = scan.index_files('path')

        assert index.get('openssl-1.1.0f/crypto/rc2').sha1 == None
        assert index.get('openssl-1.1.0f/crypto/include/internal/x509_int.h').sha1 == '874a41f075ca5b348baa60f802da50a4ca176104'
        assert index.get('openssl-1.1.0f/crypto/ec/asm/ecp_nistz256-armv4.pl').sha1 == '132eac80c01eb0c0b79dc26909d6cd2aafd17936'
        assert index.get('openssl-1.1.0f/test/testreq2.pem').sha1 == '1c21cfdc959a9b1a51011a1df50e71fc0c306bcb'

    def test_Scan_index_files_large_openssl_key_sha1(self):
        test_file = self.get_test_loc('models/scan/openssl-1.1.0f-clip_scan.json')

        scan = models.Scan(test_file)

        index = scan.index_files('sha1')

        assert index.get('478330af84ea74932db60e35533215de649a06c4').path == 'openssl-1.1.0f/apps/pca-cert.srl'
        assert index.get('cd5cb64b8c0d5654b5a768d820a2b1ec03ec365a').path == 'openssl-1.1.0f/demos/smime/cacert.pem'
        assert index.get('6f4461b4797f7521bb72a9ba87d50735c1523dbe').path == 'openssl-1.1.0f/demos/smime/cakey.pem'
        assert index.get('112a4fb8f81d81db9a235165afabfc74f6f7c2b4').path == 'openssl-1.1.0f/demos/smime/signer.pem'

    def test_Scan_index_files_large_openssl_key_name(self):
        test_file = self.get_test_loc('models/scan/openssl-1.1.0f-clip_scan.json')

        scan = models.Scan(test_file)

        index = scan.index_files('name')

        assert index.get('dh1024.pem').sha1 == 'da4ca87ebe296b9a3da0ce36416425cb28b4ec1c'
        assert index.get('dh2048.pem').sha1 == '70de2a72fd6288024189d43c0797c2fbbd4dfc6d'
        assert index.get('dh4096.pem').sha1 == '770c50e94578ac0e2b97c7d77796d28c23013f1c'
        assert index.get('server.pem').sha1 == 'fe88dcba1740f5e4044dfe70027e2d1d3c2c2ce1'

    def test_Scan_index_files_large_dropbear_key_path(self):
        test_file = self.get_test_loc('models/scan/dropbear-2017.75-clip_scan.json')

        scan = models.Scan(test_file)

        index = scan.index_files('path')

        assert index.get('dropbear-2017.75/libtomcrypt/src/modes/cfb/cfb_encrypt.c').sha1 == '62874f53fd3fe84ff5062f99f83a692d23df0202'
        assert index.get('dropbear-2017.75/dss.h').sha1 == '721745c2dfe0b74aee8633713e7bba3217f2a214'
        assert index.get('dropbear-2017.75/libtomcrypt/src/ciphers/twofish/twofish.c').sha1 == 'ac05244fa207ef9f1705245c2949ccc13b859c2c'
        assert index.get('dropbear-2017.75/libtomcrypt/src/pk/asn1/der/octet/der_encode_octet_string.c').sha1 == '6592dbb32aa23b9ee5a9a015075490d2a4dc4e31'

    def test_Scan_index_files_large_dropbear_key_sha1(self):
        test_file = self.get_test_loc('models/scan/dropbear-2017.75-clip_scan.json')

        scan = models.Scan(test_file)

        index = scan.index_files('sha1')

        assert index.get(None).path == 'dropbear-2017.75/libtommath/logs/invmod.log'
        assert index.get('71cb8d2a576df3157730d5353eb81f6d6feb328c').path == 'dropbear-2017.75/libtomcrypt/src/encauth/gcm/gcm_add_iv.c'
        assert index.get('c4fc19b67598f44c4a09513850b109ff29addecc').path == 'dropbear-2017.75/libtomcrypt/TODO'
        assert index.get('a39de0a5566cafb2c28310f1f266ed201a48cbbb').path == 'dropbear-2017.75/libtomcrypt/src/modes/ecb/ecb_decrypt.c'

    def test_Scan_index_files_large_dropbear_key_name(self):
        test_file = self.get_test_loc('models/scan/dropbear-2017.75-clip_scan.json')

        scan = models.Scan(test_file)

        index = scan.index_files('name')

        assert index.get('TODO').sha1 == 'c4fc19b67598f44c4a09513850b109ff29addecc'
        assert index.get('multi.c').sha1 == '87a54063934ac017536b964cb410c4443cf0be66'
        assert index.get('ecc.c').sha1 == '3d8dca5b8b51156a3e07123e4124c4530ba0421e'
        assert index.get('ecc_test.c').sha1 == '658153d8d04178fbb19dca7848bf1575a44010e4'

    def test_Scan_index_files_large_zlib_key_path(self):
        test_file = self.get_test_loc('models/scan/zlib-1.2.11-clip_scan.json')

        scan = models.Scan(test_file)

        index = scan.index_files('path')

        assert index.get('zlib-1.2.11/contrib/ada/readme.txt').sha1 == '1fd4ae8ee39ef80117dca454e1951ecaf0d1d290'
        assert index.get('zlib-1.2.11/zutil.c').sha1 == '2f1fcc93488ac84acf984415b6ea0bd63c72aa49'
        assert index.get('zlib-1.2.11/contrib/dotzlib/DotZLib/UnitTests.cs').sha1 == '8d35d4a5b28e472f5618185c295d1964c1459d07'
        assert index.get('zlib-1.2.11/contrib/untgz/Makefile.msc').sha1 == '3d3a312c38dd7e3316ddb553e894734f42d28205'

    def test_Scan_index_files_large_zlib_key_sha1(self):
        test_file = self.get_test_loc('models/scan/zlib-1.2.11-clip_scan.json')

        scan = models.Scan(test_file)

        index = scan.index_files('sha1')

        assert index.get('0ef05b0d12bf2cfbbf1aa84cff0e8dcf4fc5b731').path == 'zlib-1.2.11/zconf.h.in'
        assert index.get('ddf83b34d4c7d41ace39f96b5cb13fb390c8d2eb').path == 'zlib-1.2.11/contrib/pascal/zlibd32.mak'
        assert index.get('2d3f0ee9f7cc18feff62eb78f064f4b4f45415d9').path == 'zlib-1.2.11/contrib/vstudio/vc14/zlib.rc'
        assert index.get('e67b5d0e28bda140346388d087b2c13cf7680a1f').path == 'zlib-1.2.11/contrib/vstudio/vc9/zlib.rc'

    def test_Scan_index_files_large_zlib_key_name(self):
        test_file = self.get_test_loc('models/scan/zlib-1.2.11-clip_scan.json')

        scan = models.Scan(test_file)

        index = scan.index_files('name')

        assert index.get('zfstream.h').sha1 == '351a3f5bfb93196701cc86b27db866a18ca54105'
        assert index.get('make_vms.com').sha1 == '79d9e7c5d124fbcf79bff4509b51c09600b33a34'
        assert index.get('zlibd32.mak').sha1 == 'ddf83b34d4c7d41ace39f96b5cb13fb390c8d2eb'
        assert index.get('readme.txt').sha1 == '066affe7fd1e8a9e54ef08d63abee644bb821c03'

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
