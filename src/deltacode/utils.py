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

from collections import defaultdict

import os


from commoncode import paths


def update_from_license_info(delta, unique_categories):
    """
    Increase an 'added' or 'modified' Delta object's 'score' attribute and
    annotate its 'factors' attribute if there has been a license change and
    depending on the nature of that change.
    """
    if delta.is_added():
        update_added_from_license_info(delta, unique_categories)

    if delta.is_modified():
        update_modified_from_license_info(delta, unique_categories)


def update_added_from_license_info(delta, unique_categories):
    """
    Increase an 'added' Delta object's 'score' attribute and annotate its
    'factors' attribute if there has been a license change.
    """
    new_licenses = delta.new_file.licenses or []
    new_categories = set(license.category for license in new_licenses)

    if delta.new_file.has_licenses():
        # delta.update(20, 'license info added')
        #
        # for category in new_categories:
        #     # no license ==> 'Copyleft Limited'or higher
        #     if category in unique_categories:
        #         delta.update(20, category.lower() + ' added')
        #     # no license ==> 'Permissive' or 'Public Domain'
        #     else:
        #         delta.update(0, category.lower() + ' added')
        delta.update(score=20, factor='license info added')
        return


def update_modified_from_license_info(delta, unique_categories):
    """
    Increase a 'modified' Delta object's 'score' attribute and annotate its
    'factors' attribute if there has been a license change.
    """
    if not delta.new_file.has_licenses() and delta.old_file.has_licenses():
        delta.update(score=15, factor='license info removed')
        return

    new_licenses = delta.new_file.licenses or []
    old_licenses = delta.old_file.licenses or []

    if delta.new_file.has_licenses() and not delta.old_file.has_licenses():
         delta.update(score=20, factor='license info added')
    return

    new_keys = set(license.key for license in new_licenses)
    old_keys = set(license.key for license in old_licenses)

    if new_keys != old_keys:
        delta.update(score=10, factor='license change')


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
    new_copyrights = delta.new_file.copyrights or []
    old_copyrights = delta.old_file.copyrights or []

    if delta.new_file.has_copyrights() and not delta.old_file.has_copyrights():
        delta.update(10, 'copyright info added')
        return
    if not delta.new_file.has_copyrights() and delta.old_file.has_copyrights():
        delta.update(10, 'copyright info removed')
        return

    new_holders = set(holder for copyright in new_copyrights for holder in copyright.holders)
    old_holders = set(holder for copyright in old_copyrights for holder in copyright.holders)

    if new_holders != old_holders:
        delta.update(5, 'copyright change')


def collect_errors(deltacode):
    errors = []
    errors.extend(deltacode.new.errors)
    errors.extend(deltacode.old.errors)
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
            yield delta.to_dict()
        elif not delta.is_unmodified():
            yield delta.to_dict()


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
        a_names[a_file.name].append(a_file)
    a_uniques = {k: v[0] for k, v in a_names.items() if len(v) == 1}

    b_names = defaultdict(list)
    for b_file in b_files:
        b_names[b_file.name].append(b_file)
    b_uniques = {k: v[0] for k, v in b_names.items() if len(v) == 1}

    candidate_found = False
    for a_name, a_unique in a_uniques.items():
        if a_name not in b_uniques:
            continue
        b_unique = b_uniques.get(a_name)
        if a_unique and a_unique.sha1 == b_unique.sha1:
            candidate_found = True
            break

    if not candidate_found:
        raise AlignmentException
    if a_unique.path == b_unique.path:
        return 0, 0

    common_suffix, common_segments = paths.common_path_suffix(a_unique.path, b_unique.path)
    a_segments = len(paths.split(a_unique.path))
    b_segments = len(paths.split(b_unique.path))

    return a_segments - common_segments, b_segments - common_segments


def fix_trees(a_files, b_files):
    """
    Given two sequences of File objects 'a' and 'b', use the tuple of two
    integers returned by align_trees() to remove the number of path segments
    required to create equal paths for two files that are the same in 'a' and
    'b'.
    """
    a_offset, b_offset = align_trees(a_files, b_files)
    for a_file in a_files:
        a_file.original_path = a_file.path
        a_file.path = '/'.join(paths.split(a_file.path)[a_offset:])

    for b_file in b_files:
        b_file.original_path = b_file.path
        b_file.path = '/'.join(paths.split(b_file.path)[b_offset:])


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
