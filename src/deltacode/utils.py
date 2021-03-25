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

from __future__ import absolute_import, division

from bitarray import bitarray
from collections import defaultdict
from bitarray import bitdiff

import binascii
import os

from commoncode import paths
from typing import OrderedDict

def update_from_license_info(delta, unique_categories):
    """
    Increase an 'added' or 'modified' Delta object's 'score' attribute and add
    one or more appropriate categories to its 'factors' attribute if there has
    been a license change and depending on the nature of that change.
    """
    if delta.is_added():
        update_added_from_license_info(delta, unique_categories)

    if delta.is_modified():
        update_modified_from_license_info(delta, unique_categories)


def update_added_from_license_info(delta, unique_categories):
    """
    Increase an 'added' Delta object's 'score' attribute and add
    one or more categories to its 'factors' attribute if there has
    been a license change.
    """
    
    try:
        new_licenses = delta.new_file.licenses or []

        new_categories = set(license['category'] for license in new_licenses)
        if delta.new_file.licenses:
            delta.update(20, 'license info added')
            for category in new_categories:
                # no license ==> 'Copyleft Limited'or higher
                if category in unique_categories:
                    delta.update(20, category.lower() + ' added')
                # no license ==> 'Permissive' or 'Public Domain'
                else:
                    delta.update(0, category.lower() + ' added')
            return
    except AttributeError :
        # this situation arises when the ScannedResource object has no license field for it
        pass


def update_modified_from_license_info(delta, unique_categories):
    """
    Increase a 'modified' Delta object's 'score' attribute and add
    one or more categories to its 'factors' attribute if there has
    been a license change.
    """
    try:

        if not delta.new_file.licenses and delta.old_file.licenses:
            delta.update(15, 'license info removed')
            return

        new_licenses = delta.new_file.licenses or []
        old_licenses = delta.old_file.licenses or []

        new_categories = set(license.get('category','') for license in new_licenses)
        old_categories = set(license.get('category','') for license in old_licenses)

        if delta.new_file.licenses and not delta.old_file.licenses:
            delta.update(20, 'license info added')

            for category in new_categories:
                # no license ==> 'Copyleft Limited'or higher
                if category in unique_categories:
                    delta.update(20, category.lower() + ' added')
                # no license ==> 'Permissive' or 'Public Domain'
                else:
                    delta.update(0, category.lower() + ' added')
            return

        new_keys = set(license['key'] for license in delta.new_file.licenses)
        old_keys = set(license['key'] for license in delta.old_file.licenses)

        if new_keys != old_keys:

            delta.update(10, 'license change')
            for category in new_categories - old_categories:
                unique_categories_in_old_file = len(old_categories & unique_categories)
                # 'Permissive' or 'Public Domain' ==> 'Copyleft Limited' or higher
                if unique_categories_in_old_file == 0 and category in unique_categories:
                    delta.update(20, category.lower() + ' added')
                # at least 1 category in the old file was 'Copyleft Limited' or higher ==> 'Copyleft Limited' or higher
                elif unique_categories_in_old_file != 0 and category in unique_categories:
                    delta.update(10, category.lower() + ' added')
                # 'Permissive' or 'Public Domain' ==> 'Permissive' or 'Public Domain' if not in old_categories
                elif category not in unique_categories:
                    delta.update(0, category.lower() + ' added')
    except AttributeError:
        # this situation arises when the ScannedResource object has no license field for it
        pass

def update_from_copyright_info(delta):
    """
    Increase an 'added' or 'modified' Delta object's 'score' attribute and add
    one or more appropriate categories to its 'factors' attribute if there has
    been a copyright change and depending on the nature of that change.
    """
    if delta.is_added():
        update_added_from_copyright_info(delta)

    if delta.is_modified():
        update_modified_from_copyright_info(delta)

def update_added_from_copyright_info(delta):
    """
    Increase an 'added' Delta object's 'score' attribute and add
    one or more categories to its 'factors' attribute if there has
    been a copyright change.
    """
    if delta.new_file.has_copyrights():
        delta.update(10, 'copyright info added')
        return


def update_modified_from_copyright_info(delta):
    """
    Increase a 'modified' Delta object's 'score' attribute and add
    one or more categories to its 'factors' attribute if there has
    been a copyright change.
    """

    try:
        new_copyrights = delta.new_file.copyrights or []
        old_copyrights = delta.old_file.copyrights or []
        if delta.new_file.copyrights and not delta.old_file.copyrights:
            delta.update(10, 'copyright info added')
            return
        if not delta.new_file.copyrights and delta.old_file.copyrights:
            delta.update(10, 'copyright info removed')
            return
        new_holders = set(holder for copyright in new_copyrights for holder in copyright['holders'])
        old_holders = set(holder for copyright in old_copyrights for holder in copyright['holders'])
        if new_holders != old_holders:
            delta.update(5, 'copyright change')
    except AttributeError:
        # this situation arises when the ScannedResource object has no copyright field for it
        pass


def collect_errors(deltacode):
    errors = []
    errors.extend(deltacode.new_files_errors)
    errors.extend(deltacode.old_files_errors)
    errors.extend(deltacode.errors)

    return errors


def deltas(deltacode, all_delta_types=False):
    """
    Return a generator of Delta dictionaries for JSON serialized ouput.  Omit
    all unmodified Delta objects unless the user selects the '-a'/'--all'
    option.
    """
    for delta in deltacode.deltas:
        if all_delta_types is True:
            yield delta.to_dict(deltacode)
        elif not delta.is_unmodified():
            yield delta.to_dict(deltacode)

def calculate_percent(value, total):
    """
    Return the rounded value percentage of total.
    """
    try :
        ratio = (value / total) * 100
        return round(ratio, 2)
    except ZeroDivisionError:
        return 0

class AlignmentException(Exception):
    """
    Named exception for alignment errors.
    """
    pass

def align_trees(a_files, b_files):
    """
    Given two sequences of File objects 'a' and 'b', return a tuple of
    two integers that represent the number path segments to remove
    respectively from a File path in 'a' or a File path in 'b' to obtain the
    equal paths for two files that are the same in 'a' and 'b'.
    """
    # we need to find one uniquly named file that exists in 'a' and 'b'.
    a_names = defaultdict(list)
    for a_file in a_files:
        a_names[a_file[0].name].append(a_file)
    a_uniques = {k: v[0] for k, v in a_names.items() if len(v) == 1}

    b_names = defaultdict(list)
    for b_file in b_files:
        b_names[b_file[0].name].append(b_file)
    b_uniques = {k: v[0] for k, v in b_names.items() if len(v) == 1}

    candidate_found = False
    for a_name, a_unique in a_uniques.items():
        if a_name not in b_uniques:
            continue
        b_unique = b_uniques.get(a_name)
        if a_unique and a_unique[0].sha1 == b_unique[0].sha1:
            candidate_found = True
            break

    if not candidate_found:
        raise AlignmentException
    if a_unique[0].path == b_unique[0].path:
        return 0, 0

    common_suffix, common_segments = paths.common_path_suffix(a_unique[0].path, b_unique[0].path)
    a_segments = len(paths.split(a_unique[0].path))
    b_segments = len(paths.split(b_unique[0].path))

    return a_segments - common_segments, b_segments - common_segments


def fix_trees(a_files, b_files):
    """
    Given two sequences of File objects 'a' and 'b', use the tuple of two
    integers returned by align_trees() to remove the number of path segments
    required to create equal paths for two files that are the same in 'a' and
    'b'.
    """
    a_offset, b_offset = align_trees(a_files, b_files)
    original_path_a = OrderedDict()
    original_path_b  = OrderedDict()
    for a_file in a_files:
        original_path = a_file[0].path
        a_file[1] = a_file[0].path
        a_file[0].path = '/'.join(paths.split(a_file[0].path)[a_offset:])
        original_path_a[a_file[0].path] = original_path
    for b_file in b_files:
        original_path = b_file[0].path
        b_file[1] = b_file[0].path
        b_file[0].path = '/'.join(paths.split(b_file[0].path)[b_offset:])
        original_path_b[b_file[0].path] = original_path
    return original_path_a , original_path_b

def index_files(files ,index_key = 'path'):
    """
    Return a dictionary of a list of File objects indexed by the key passed via
    the 'key' variable.  If no 'key' variable is passed, the dict is
    keyed by the File object's 'path' variable.  This function does not
    currently catch the AttributeError exception.
    """
    index = {}
    for f in files:

        key = str(getattr(f[0], index_key))

        if index.get(key) is None:
            index[key] = []
            index[key].append(f[0])
        else:
            index[key].append(f[0])
    return index

def check_moved(added_sha1, added_deltas, removed_sha1, removed_deltas):
    """
    Return True if there is only one pair of matching 'added' and 'removed'
    Delta objects and their respective File objects have the same 'name' attribute.
    """
    if added_sha1 != removed_sha1:
        return False
    if len(added_deltas) != 1 or len(removed_deltas) != 1:
        return False
    if added_deltas[0].new_file.name == removed_deltas[0].old_file.name:
        return True


def get_notice():
    """
    Retrieve the notice text from the NOTICE file for display in the JSON output.
    """
    notice_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'NOTICE')
    notice_text = open(notice_path).read()

    delimiter = '\n\n\n'
    [notice_text, extra_notice_text] = notice_text.split(delimiter, 1)
    extra_notice_text = delimiter + extra_notice_text

    delimiter = '\n\n  '
    [notice_text, acknowledgment_text] = notice_text.split(delimiter, 1)
    acknowledgment_text = delimiter + acknowledgment_text

    notice = acknowledgment_text.strip().replace('  ', '')

    return notice


def hamming_distance(fingerprint1, fingerprint2):
    """
    Return hamming distance between two given fingerprints.
    Hamming distance is the difference in the bits of two binary string.
    Files with fingerprints whose hamming distance are less tends to be more similar.
    """
    distance = bitdiff(fingerprint1, fingerprint2)
    result = int(distance)

    return result

def bitarray_from_hex(fingerprint_hex):
    """
    Return bitarray from a hex string.
    """
    bytes = binascii.unhexlify(fingerprint_hex)
    result = bitarray_from_bytes(bytes)

    return result

def bitarray_from_bytes(b):
    """
    Return bitarray from a byte string, interpreted as machine values.
    """
    a = bitarray()
    a.frombytes(b)

    return a