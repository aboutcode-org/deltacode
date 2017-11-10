#
#  Copyright (c) 2017 nexB Inc. and others. All rights reserved.
#
from __future__ import absolute_import

from collections import OrderedDict

from deltacode.models import Scan
from deltacode import utils

__version__ = '0.0.1.beta'


class DeltaCode:
    """
    Handles the basic operations on a pair of incoming ScanCode scans (in JSON
    format) and the Delta objects created from a comparison of the files (in
    the form of File objects) contained in those scans.
    """
    def __init__(self, new_path, old_path):
        self.new = Scan(new_path)
        self.old = Scan(old_path)
        self.deltas = self.determine_delta()

    def align_scan(self):
        """
        Seeks to align the paths of a pair of files (File objects) in the pair
        of incoming scans so that the attributes and other characteristics of
        the files can be compared with one another.  Calls utils.fix_trees(),
        which calls utils.align_trees().
        """
        try:
            utils.fix_trees(self.new.files, self.old.files)
        except utils.AlignmentException:
            for f in self.new.files:
                f.original_path = f.path
            for f in self.old.files:
                f.original_path = f.path

    def determine_delta(self):
        """
        Given new and old scans, return an OrderedDict of Delta objects grouping
        the objects under the keys 'added', 'modified', 'removed' or 'unmodified'.
        Returns None if no File objects can be loaded from either scan.
        """
        if self.new.files is None or self.old.files is None:
            return None

        deltas = OrderedDict([
            ('added', []),
            ('removed', []),
            ('modified', []),
            ('unmodified', [])
        ])

        # align scan and create our index
        self.align_scan()
        new_index = self.new.index_files()
        old_index = self.old.index_files()

        # TODO: handle this better, maybe a counts object or something.
        # gathering counts to ensure no files lost or missing from our 'deltas' set
        new_nonfiles = 0
        old_nonfiles = 0
        modified = 0
        unmodified = 0

        # perform the deltas
        for path, new_file in new_index.items():
            if new_file.type != 'file':
                new_nonfiles += 1
                continue

            try:
                delta_old_file = old_index[path]
            except KeyError:
                added = Delta(new_file, None, 'added')
                deltas['added'].append(added)
                continue

            # at this point, we have a delta_old_file.
            # we need to determine wheather this is identical,
            # or a modification.
            if new_file.sha1 == delta_old_file.sha1:
                delta = Delta(new_file, delta_old_file, 'unmodified')
                deltas['unmodified'].append(delta)
                unmodified += 1
                continue
            else:
                delta = Delta(new_file, delta_old_file, 'modified')
                deltas['modified'].append(delta)
                modified += 1

        # now time to find the added.
        for path, old_file in old_index.items():
            if old_file.type != 'file':
                old_nonfiles += 1
                continue

            try:
                new_index[path]
            except KeyError:
                removed = Delta(None, old_file, 'removed')
                deltas['removed'].append(removed)
                continue

        # make sure everything is accounted for
        deltaCount = len(deltas['added']) + len(deltas['modified']) + len(deltas['removed']) + len(deltas['unmodified'])
        assert deltaCount == ((self.new.files_count - new_nonfiles) +
                              (self.old.files_count - old_nonfiles) - modified - unmodified)

        return deltas

    def get_stats(self):
        """
        Given a list of Delta objects, return a 'counts' dictionary keyed by
        category -- i.e., the keys of the determine_delta() OrderedDict of
        Delta objects -- that contains the count as a value for each category.
        """
        added, modified, removed, unmodified = 0, 0, 0, 0

        added = len(self.deltas['added'])
        modified = len(self.deltas['modified'])
        removed = len(self.deltas['removed'])
        unmodified = len(self.deltas['unmodified'])

        return OrderedDict([('added', added), ('modified', modified), ('removed', removed), ('unmodified', unmodified)])

    def to_dict(self):
        """
        Given an OrderedDict of Delta objects, return an OrderedDict with a
        'deltacode_version' field, a 'deltacode_stats' field, a 'deltas_count'
        field, and a 'deltas' field containing a list of our Delta objects.
        """
        dict = OrderedDict()
        dict['deltacode_version'] = __version__
        dict['deltacode_stats'] = self.get_stats()

        added = len(self.deltas['added'])
        modified = len(self.deltas['modified'])
        removed = len(self.deltas['removed'])
        unmodified = len(self.deltas['unmodified'])
        dict['deltas_count'] = added + modified + removed + unmodified

        category_dict = OrderedDict()
        added_list = []
        modified_list = []
        removed_list = []
        unmodified_list = []

        for category in self.deltas:
            for deltaObject in self.deltas[category]:
                deltas_dict = {}
                if deltaObject.new_file is None:
                    deltas_dict['new'] = deltaObject.new_file
                else:
                    deltas_dict['new'] = deltaObject.new_file.to_dict()
                if deltaObject.old_file is None:
                    deltas_dict['old'] = deltaObject.old_file
                else:
                    deltas_dict['old'] = deltaObject.old_file.to_dict()

                if category == 'added':
                    added_list.append(deltas_dict)
                elif category == 'modified':
                    modified_list.append(deltas_dict)
                elif category == 'removed':
                    removed_list.append(deltas_dict)
                elif category == 'unmodified':
                    unmodified_list.append(deltas_dict)

            category_dict['added'] = added_list
            category_dict['modified'] = modified_list
            category_dict['removed'] = removed_list
            category_dict['unmodified'] = unmodified_list

        dict['deltas'] = category_dict

        return dict


class Delta:
    """
    A tuple reflecting a comparison of two files -- each of which is a File
    object -- and the category that characterizes the comparison:
    'added', 'modified', 'removed' or 'unmodified'.
    """
    def __init__(self, new_file, old_file, delta_type):
        # TODO: add check to ensure both are File objects
        self.new_file = new_file
        self.old_file = old_file
        self.category = delta_type

    def license_diff(self):
        if self.new_file is None or self.old_file is None:
            return False

        new_file_keys = []
        old_file_keys = []
        cutoff_score = 50
        if self.new_file.licenses is not None:
            for l in self.new_file.licenses:
                if l.score >= cutoff_score:
                    new_file_keys.append(l.key)
        if self.old_file.licenses is not None:
            for l in self.old_file.licenses:
                if l.score >= cutoff_score:
                    old_file_keys.append(l.key)

        deduped_new_file_keys = list(set(new_file_keys))
        deduped_old_file_keys = list(set(old_file_keys))

        if deduped_new_file_keys != deduped_old_file_keys:
            return True
        else:
            return False
