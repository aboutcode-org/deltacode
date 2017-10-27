#
#  Copyright (c) 2017 nexB Inc. and others. All rights reserved.
#
from __future__ import absolute_import

from collections import defaultdict


from commoncode import paths


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
        setattr(a_file, 'original_path', a_file.path)
        a_file.path = '/'.join(paths.split(a_file.path)[a_offset:])

    for b_file in b_files:
        setattr(b_file, 'original_path', b_file.path)
        b_file.path = '/'.join(paths.split(b_file.path)[b_offset:])
