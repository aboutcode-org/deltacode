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
            ('unmodified', []),
            ('license_changes', [])
        ])

        # align scan and create our index
        self.align_scan()
        new_index = self.new.index_files()
        old_index = self.old.index_files()

        # gathering counts to ensure no files lost or missing from our 'deltas' set
        new_files_to_visit = self.new.files_count
        old_files_to_visit = self.old.files_count

        # perform the deltas
        for path, new_files in new_index.items():
            for new_file in new_files:
                new_files_to_visit -= 1

                if new_file.type != 'file':
                    continue

                try:
                    delta_old_files = old_index[path]
                except KeyError:
                    deltas['added'].append(Delta(new_file, None, 'added'))
                    continue

                # at this point, we have a delta_old_file.
                # we need to determine wheather this is identical,
                # or a modification.
                for f in delta_old_files:
                    if new_file.sha1 == f.sha1:
                        deltas['unmodified'].append(Delta(new_file, f, 'unmodified'))
                        continue
                    else:
                        deltas['modified'].append(Delta(new_file, f, 'modified'))

        # now time to find the added.
        for path, old_files in old_index.items():
            for old_file in old_files:
                old_files_to_visit -= 1
                
                if old_file.type != 'file':
                    continue

                try:
                    # This file already classified as 'modified' or 'unmodified' so do nothing
                    new_index[path]
                except KeyError:
                    deltas['removed'].append(Delta(None, old_file, 'removed'))
                    continue
            
        # make sure everything is accounted for
        assert new_files_to_visit == 0
        assert old_files_to_visit == 0

        deltas_modified = deltas['modified']
        deltas['license_changes'] = self.modified_lic_diff(deltas_modified)

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

    def modified_lic_diff(self, modified):
        """
        Accept a list of 'modified' Delta objects passed by
        DeltaCode.determine_delta() from the OrderedDict of Delta objects
        and return a list of Delta objects with license changes
        that satisfy the test in Delta.license_diff().
        """
        return [modified_delta for modified_delta in modified if modified_delta.license_diff()]


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
        """
        Compare the license details for a pair of 'new' and 'old' File objects
        in a Delta object,  return True if those details differ, and otherwise
        return False.
        """
        if self.new_file is None or self.old_file is None:
            return False

        cutoff_score = 50

        if self.new_file.licenses:
            new_file_keys = [l.key for l in self.new_file.licenses if l.score >= cutoff_score]
        else:
            new_file_keys = []

        if self.old_file.licenses:
            old_file_keys = [l.key for l in self.old_file.licenses if l.score >= cutoff_score]
        else:
            old_file_keys = []

        new_file_keys = list(set(new_file_keys))
        old_file_keys = list(set(old_file_keys))

        if new_file_keys != old_file_keys:
            return True
        else:
            return False
