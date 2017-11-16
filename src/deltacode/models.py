#
#  Copyright (c) 2017 nexB Inc. and others. All rights reserved.
#
from __future__ import absolute_import

from collections import OrderedDict

import json


class Scan:
    """
    Processes the files contained in an incoming ScanCode scan to test whether
    they are valid, retrieve the scan's 'files_count' value, create a list of
    File objects, and generate a dictionary of File objects indexed by a
    selected key.
    """
    def __init__(self, path=''):
        self.path = '' if path is None else path
        self.files_count = self.get_files_count(self.path)
        self.files = self.load_files(self.path)
        self.options = self.get_options(self.path)

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
            raise ScancodeVersionAttributeException

        if int(scan.get('scancode_version').split('.').pop(0)) < 2:
            raise ScancodeOldVersionException

        if not scan.get('scancode_options').get('--info'):
            raise ScancodeInfoAttributeException

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

        files = [File(f) for f in json.loads(scan).get('files')]

        # make sure we have same number of File objects as in the scan.
        assert len(files) == self.files_count

        return files

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


class File:
    """
    File object created from an ABCD formatted 'file' dictionary.
    """
    def __init__(self, dictionary={}):
        self.path = dictionary.get('path')
        self.type = dictionary.get('type')
        self.name = dictionary.get('name')
        self.size = dictionary.get('size')
        self.sha1 = dictionary.get('sha1')
        self.original_path = ''
        self.licenses = self.get_licenses(dictionary)

    def get_licenses(self, dictionary):
        if dictionary.get('licenses') == None:
            return None

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


class License:
    """
    License object created from the 'license' field in an ABCD formatted 'file' dictionary.
    """
    def __init__(self, dictionary={}):
        self.key = dictionary.get('key')
        self.score = dictionary.get('score')
        self.short_name = dictionary.get('short_name')
        self.category = dictionary.get('category')
        self.owner = dictionary.get('owner')
        self.homepage_url = dictionary.get('homepage_url')
        self.text_url = dictionary.get('text_url')
        self.reference_url = dictionary.get('reference_url')
        self.spdx_license_key = dictionary.get('spdx_license_key')
        self.spdx_url = dictionary.get('spdx_url')
        self.start_line = dictionary.get('start_line')
        self.end_line = dictionary.get('end_line')
        self.matched_rule = dictionary.get('matched_rule')

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
            ('owner', self.owner),
            ('homepage_url', self.homepage_url),
            ('text_url', self.text_url),
            ('reference_url', self.reference_url),
            ('spdx_license_key', self.spdx_license_key),
            ('spdx_url', self.spdx_url),
            ('start_line', self.start_line),
            ('end_line', self.end_line),
            ('matched_rule', self.matched_rule),
        ])

        return d

    def __repr__(self):
        """
        Return string containing a printable representation of the File object.
        """
        return "%s" % self.__dict__


class ScancodeVersionAttributeException(Exception):
    """
    Named exception for JSON file containing no 'scancode_version' attribute.
    """
    pass


class ScancodeOldVersionException(Exception):
    """
    Named exception for JSON file containing old version of ScanCode.
    """
    pass


class ScancodeInfoAttributeException(Exception):
    """
    Named exception for JSON file containing no 'scancode_options'/'--info'
    attribute.
    """
    pass
