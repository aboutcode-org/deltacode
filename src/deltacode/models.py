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

        return options

    def is_valid_scan(self, location):
        """
        In conjunction with test_deltacode.py, test the incoming files to
        ensure that they are well-formed JSON and otherwise satisfy the
        requirements to be run in DeltaCode (e.g., ScanCode version, proper
        ScanCode options etc.).
        """
        # TODO: handle this exception during #171
        try:
            scan = json.loads(open(location).read())
        except IOError:
            return

        scan = json.loads(open(location).read())

        if not scan.get('scancode_version'):
            msg = ('JSON file \'' + location + '\' is missing the \'scancode_version\' attribute.')
            raise ScanException(msg)

        if int(scan.get('scancode_version').split('.').pop(0)) < 2:
            msg = ('JSON file \'' + location + '\' was created with an old version of ScanCode.')
            raise ScanException(msg)

        if not scan.get('scancode_options').get('--info'):
            msg = ('JSON file \'' + location + '\' is missing the \'scancode_options/--info\' attribute.')
            raise ScanException(msg)

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

        return scan.get('files_count')

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
        index = {}

        for f in self.files:
            key = getattr(f, index_key)

            if index.get(key) == None:
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
        self.original_path = ''
        self.licenses = self.get_licenses(dictionary) if dictionary.get('licenses') else []

    def get_licenses(self, dictionary):
        if dictionary.get('licenses') == []:
            return []
        else:
            return [License(l) for l in dictionary.get('licenses')]

    def to_dict(self):
        d = OrderedDict([
            ('path', self.path),
            ('type', self.type),
            ('name', self.name),
            ('size', self.size),
            ('sha1', self.sha1),
            ('original_path', self.original_path),
        ])

        if self.licenses:
            d['licenses'] = [l.to_dict() for l in self.licenses]

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
    License object created from the 'license' field in an ABCD formatted 'file' dictionary.
    """
    def __init__(self, dictionary={}):
        self.key = dictionary.get('key')
        self.score = dictionary.get('score')
        self.short_name = dictionary.get('short_name')
        self.category = dictionary.get('category')
        self.owner = dictionary.get('owner')

    def to_dict(self):
        """
        Given a License object, return an OrderedDict with the full
        set of fields from the ScanCode 'license' value.
        """
        d = OrderedDict([
            ('key', self.key),
            ('score', self.score),
            ('short_name', self.short_name),
            ('category', self.category),
            ('owner', self.owner)
        ])

        return d

    def __repr__(self):
        """
        Return string containing a printable representation of the License object.
        """
        return "%s" % self.__dict__


class ScanException(Exception):
    """
    Named exception for JSON file (1) containing no 'scancode_version'
    attribute, (2) containing old version of ScanCode, or (3) containing no
    'scancode_options'/'--info' attribute.
    """
    pass
