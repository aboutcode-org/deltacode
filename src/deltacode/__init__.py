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
                setattr(f, 'original_path', f.path)
            for f in self.old.files:
                setattr(f, 'original_path', f.path)

    def determine_delta(self):
        """
        Given new and old scans, return a list of Delta objects identifying
        each as 'added', 'modified', 'removed' or 'unchanged'. Returns None if
        no File objects can be loaded from either scan.
        """
        if self.new.files is None or self.old.files is None:
            return None

        deltas = []

        # align scan and create our index
        self.align_scan()
        new_index = self.new.index_files()
        old_index = self.old.index_files()

        # TODO: handle this better, maybe a counts object or something.
        # gathering counts to ensure no files lost or missing from our 'deltas' set
        new_nonfiles = 0
        old_nonfiles = 0
        modified = 0
        unchanged = 0

        # perform the deltas
        for path, new_file in new_index.items():
            if new_file.type != 'file':
                new_nonfiles += 1
                continue

            try:
                delta_old_file = old_index[path]
            except KeyError:
                added = Delta(new_file, None, 'added')
                deltas.append(added)
                continue

            # at this point, we have a delta_old_file.
            # we need to determine wheather this is identical,
            # or a modification.
            if new_file.sha1 == delta_old_file.sha1:
                delta = Delta(new_file, delta_old_file, 'unchanged')
                deltas.append(delta)
                unchanged += 1
                continue
            else:
                delta = Delta(new_file, delta_old_file, 'modified')
                deltas.append(delta)
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
                deltas.append(removed)
                continue

        # make sure everything is accounted for
        assert len(deltas) == ((self.new.files_count - new_nonfiles) + (self.old.files_count - old_nonfiles) - (modified + unchanged))

        return deltas

    def get_stats(self):
        """
        Given a list of Delta objects, return a 'counts' dictionary keyed by
        category that contains the count as a value for each category.
        """
        added, modified, removed, unchanged = 0, 0, 0, 0

        for delta in self.deltas:
            if delta.category == 'added':
                added += 1
            if delta.category == 'modified':
                modified += 1
            if delta.category == 'removed':
                removed += 1
            if delta.category == 'unchanged':
                unchanged += 1

        return OrderedDict([('added', added), ('modified', modified), ('removed', removed), ('unchanged', unchanged)])

    def to_dict(self):
        """
        Given a list of Delta objects, return an OrderedDict with a
        'deltacode_version' field, a 'deltacode_stats' field, a 'deltas_count'
        field, and a 'deltas' field containing a list of our Delta objects.
        """
        dict = OrderedDict()
        dict['deltacode_version'] = __version__
        dict['deltacode_stats'] = self.get_stats()
        dict['deltas_count'] = len(self.deltas)

        deltas_list = []

        for f in self.deltas:
            deltas_dict = {}
            if f.new_file is None:
                deltas_dict['new'] = f.new_file
            else:
                deltas_dict['new'] = f.new_file.__dict__
            if f.old_file is None:
                deltas_dict['old'] = f.old_file
            else:
                deltas_dict['old'] = f.old_file.__dict__
            deltas_dict['category'] = f.category
            deltas_list.append(deltas_dict)

        dict['deltas'] = deltas_list

        return dict


class Delta:
    """
    A tuple reflecting a comparison of two files -- each of which is a File
    object -- and the category that characterizes the comparison:
    'added', 'modified', 'removed' or 'unchanged'.
    """
    def __init__(self, new_file, old_file, delta_type):
        # TODO: add check to ensure both are File objects
        self.new_file = new_file
        self.old_file = old_file
        self.category = delta_type
