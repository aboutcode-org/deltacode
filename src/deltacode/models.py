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

from __future__ import absolute_import

from collections import OrderedDict

import json


class Scan(object):
    """
    Process the files contained in an incoming ScanCode scan to test whether
    they are valid, retrieve the scan's 'files_count' value, create a list of
    File objects, and generate a dictionary of File objects indexed by a
    selected key.
    """
    def __init__(self, path=''):
        if path is None:
            path = ''

        self.errors = []

        if not self.is_valid_scan(path):
            self.path = ''
            self.files_count = 0
            self.files = []
            self.options = {}
        else:
            self.path = path
            self.files_count = self.get_files_count(path)
            self.files = self.load_files(path)
            self.options = self.get_options(path)

    def get_options(self, path):
        """
        Collect the ScanCode options contained in the incoming ScanCode file.
        """
        # TODO: handle this exception during #171
        try:
            scan = json.loads(open(path).read())
        except IOError:
            return

        scan = json.loads(open(path).read())

        options = scan.get('scancode_options')
        if not options:
            # Handle new(er) scancode options
            headers = scan.get('headers')
            if headers:
                options = headers[0].get('options')

        return options

    def is_valid_scan(self, location):
        """
        In conjunction with test_deltacode.py, test the incoming files to
        ensure that they are well-formed JSON and otherwise satisfy the
        requirements to be run in DeltaCode (e.g., ScanCode version, proper
        ScanCode options etc.).
        """
        try:
            scan = json.loads(open(location).read())
        except IOError:
            return

        scan = json.loads(open(location).read())

        version = scan.get('scancode_version')
        if not version:
            # handle new(er) scancode version location
            headers = scan.get('headers')
            if headers:
                version = headers[0].get('tool_version')
        
        options = scan.get('scancode_options')
        if not options:
            headers = scan.get('headers')
            if headers:
                options = headers[0].get('options')

        if not version:
            raise ScanException('JSON file: {} is missing the ScanCode version.'.format(location))

        if int(version.split('.').pop(0)) < 2:
            raise ScanException('JSON file: {} was created with an old version of ScanCode.'.format(location))

        if not options.get('--info'):
            raise ScanException('JSON file: {} is missing the ScanCode --info attribute.'.format(location))

        return True

    def get_files_count(self, path):
        """
        Retrieve a scan's 'files_count' value.
        """
        if not self.is_valid_scan(path):
            # TODO: raise some error
            return

        with open(path) as jsonf:
            scan = jsonf.read()

        scan = json.loads(scan)

        files_count = scan.get('files_count')
        if not files_count:
            headers = scan.get('headers')
            if headers:
                files_count = headers[0].get('extra_data', {}).get('files_count')

        return files_count

    def load_files(self, path):
        """
        Return a list of File objects from a scanfile at 'path',
        json format.
        """
        if not self.is_valid_scan(path):
            # TODO: raise some error
            return

        with open(path) as jsonf:
            scan = jsonf.read()

        return [File(f) for f in json.loads(scan).get('files')]

    def index_files(self, index_key='path'):
        """
        Return a dictionary of a list of File objects indexed by the key passed via
        the 'key' variable.  If no 'key' variable is passed, the dict is
        keyed by the File object's 'path' variable.  This function does not
        currently catch the AttributeError exception.
        """
        index = OrderedDict()

        for f in self.files:
            key = getattr(f, index_key)

            if index.get(key) is None:
                index[key] = []
                index[key].append(f)
            else:
                index[key].append(f)

        return index


class File(object):
    """
    File object created from an ABCD formatted 'file' dictionary.
    """
    def __init__(self, dictionary={}):
        self.path = dictionary.get('path', '')
        self.type = dictionary.get('type', '')
        self.name = dictionary.get('name', '')
        self.size = dictionary.get('size', '')
        self.sha1 = dictionary.get('sha1', '')
        self.fingerprint = dictionary.get('fingerprint', '')
        self.original_path = ''
        self.licenses = self.get_licenses(dictionary) if dictionary.get('licenses') else []
        self.copyrights = self.get_copyrights(dictionary) if dictionary.get('copyrights') else []

    def get_licenses(self, dictionary):
        if dictionary.get('licenses') == []:
            return []
        else:
            return [License(l) for l in dictionary.get('licenses')]

    def has_licenses(self):
        if len(self.licenses) > 0:
            return True

    def get_copyrights(self, dictionary):
        if dictionary.get('copyrights') == []:
            return []
        else:
            return [Copyright(l) for l in dictionary.get('copyrights')]

    def has_copyrights(self):
        if len(self.copyrights) > 0:
            return True

    def to_dict(self):
        d = OrderedDict([
            ('path', self.path),
            ('type', self.type),
            ('name', self.name),
            ('size', self.size),
            ('sha1', self.sha1),
            ('fingerprint', self.fingerprint),
            ('original_path', self.original_path),
        ])

        if self.licenses:
            d['licenses'] = [l.to_dict() for l in self.licenses]
        else:
            d['licenses'] = []

        if self.copyrights:
            d['copyrights'] = [l.to_dict() for l in self.copyrights]
        else:
            d['copyrights'] = []

        return d

    def size_difference(self, other_file):
        """
        Return the difference between the size of the instant File object and
        a second File object to which it is being compared.
        """
        return self.size - other_file.size

    def __repr__(self):
        """
        Return string containing a printable representation of the File object.
        """
        return "%s" % self.__dict__


class License(object):
    """
    License object created from the 'license' field in an ABCD formatted 'file'
    dictionary.
    """
    def __init__(self, dictionary={}):
        self.key = dictionary.get('key')
        self.language = dictionary.get('language')
        self.short_name = dictionary.get('short_name')
        self.name = dictionary.get('name')
        self.category = dictionary.get('category')
        self.owner = dictionary.get('owner')
        self.homepage_url = dictionary.get('homepage_url')
        self.notes = dictionary.get('notes')
        self.is_builtin = dictionary.get('is_builtin')
        self.is_exception = dictionary.get('is_exception')
        self.is_unknown = dictionary.get('is_unknown')
        self.is_generic = dictionary.get('is_generic')
        self.spdx_license_key = dictionary.get('spdx_license_key')
        self.other_spdx_license_keys = dictionary.get('other_spdx_license_keys')
        self.osi_license_key = dictionary.get('osi_license_key')
        self.text_urls = dictionary.get('text_urls')
        self.osi_url = dictionary.get('osi_url')
        self.faq_url = dictionary.get('faq_url')
        self.other_urls = dictionary.get('other_urls')
        self.key_aliases = dictionary.get('key_aliases')
        self.minimum_coverage = dictionary.get('minimum_coverage')
        self.standard_notice = dictionary.get('standard_notice')
        self.ignorable_copyrights = dictionary.get('ignorable_copyrights')
        self.ignorable_holders = dictionary.get('ignorable_holders')
        self.ignorable_authors = dictionary.get('ignorable_authors')
        self.ignorable_urls = dictionary.get('ignorable_urls')
        self.ignorable_emails = dictionary.get('ignorable_emails')
        self.text = dictionary.get('text')
        self.scancode_url = dictionary.get('scancode_url')
        self.licensedb_url = dictionary.get('licensedb_url')
        self.spdx_url = dictionary.get('spdx_url')

    def to_dict(self):
        """
        Given a License object, return an OrderedDict with the full
        set of fields from the ScanCode 'license' value.
        """
        d = OrderedDict([
            ('key', self.key),
            ('language', self.language),
            ('short_name', self.short_name),
            ('name', self.name),
            ('category', self.category),
            ('owner', self.owner),
            ('homepage_url', self.homepage_url),
            ('notes', self.notes),
            ('is_builtin', self.is_builtin),
            ('is_exception', self.is_exception),
            ('is_unknown', self.is_unknown),
            ('is_generic', self.is_generic),
            ('spdx_license_key', self.spdx_license_key),
            ('other_spdx_license_keys', self.other_spdx_license_keys),
            ('osi_license_key', self.osi_license_key),
            ('text_urls', self.text_urls),
            ('osi_url', self.osi_url),
            ('faq_url', self.faq_url),
            ('other_urls', self.other_urls),
            ('key_aliases', self.key_aliases),
            ('minimum_coverage', self.minimum_coverage),
            ('standard_notice', self.standard_notice),
            ('ignorable_copyrights', self.ignorable_copyrights),
            ('ignorable_holders', self.ignorable_holders),
            ('ignorable_authors', self.ignorable_authors),
            ('ignorable_urls', self.ignorable_urls),
            ('ignorable_emails', self.ignorable_emails),
            ('text', self.text),
            ('scancode_url', self.scancode_url),
            ('licensedb_url', self.licensedb_url),
            ('spdx_url', self.spdx_url)
        ])

        return d

    def __repr__(self):
        """
        Return string containing a printable representation of the License
        object.
        """
        return "%s" % self.__dict__


class Copyright(object):
    """
    Copyright object created from the 'copyrights' field in an ABCD formatted
    'file' dictionary.
    """
    def __init__(self, dictionary={}):
        self.statements = dictionary.get('statements')
        self.holders = dictionary.get('holders')

    def to_dict(self):
        """
        Given a Copyright object, return an OrderedDict with the full
        set of fields from the ScanCode 'copyrights' value.
        """
        d = OrderedDict([
            ('statements', self.statements),
            ('holders', self.holders)
        ])

        return d

    def __repr__(self):
        """
        Return string containing a printable representation of the Copyright
        object.
        """
        return "%s" % self.__dict__


class ScanException(Exception):
    """
    Named exception for JSON file (1) containing no 'scancode_version'
    attribute, (2) containing old version of ScanCode, or (3) containing no
    'scancode_options'/'--info' attribute.
    """
    pass
