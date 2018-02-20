#
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
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

from deltacode.models import File
from deltacode.models import Scan
from deltacode import utils


from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution('deltacode').version
except DistributionNotFound:
    # package is not installed ??
    __version__ = '0.0.1.beta'


class DeltaCode(object):
    """
    Handle the basic operations on a pair of incoming ScanCode scans (in JSON
    format) and the Delta objects created from a comparison of the files (in
    the form of File objects) contained in those scans.
    """
    def __init__(self, new_path, old_path, options):
        self.new = Scan(new_path)
        self.old = Scan(old_path)
        self.options = options
        self.deltas = []
        self.errors = []

        if self.new.path != '' and self.old.path != '':
            self.determine_delta()
            self.determine_moved()
            self.license_diff()
            # Sort deltas by score, descending, i.e., high > low.
            self.deltas.sort(key=lambda Delta: Delta.score, reverse=True)

    def align_scan(self):
        """
        Seek to align the paths of a pair of files (File objects) in the pair
        of incoming scans so that the attributes and other characteristics of
        the files can be compared with one another.  Call utils.fix_trees(),
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
        Given new and old scans, return a list of Delta objects that can be
        sorted by their attributes, e.g., by Delta.score.  Return None if no
        File objects can be loaded from either scan.  Pass a 'score' when
        creating a Delta object, and add the appropriate category (e.g.,
        'added') to the Delta object's 'factors' attribute.
        """
        # align scan and create our index
        self.align_scan()
        new_index = self.new.index_files()
        old_index = self.old.index_files()

        # gathering counts to ensure no files lost or missing from our 'deltas' set
        new_files_visited = 0
        old_files_visited = 0

        # perform the deltas
        for path, new_files in new_index.items():
            for new_file in new_files:
                new_files_visited += 1

                if new_file.type != 'file':
                    continue

                try:
                    delta_old_files = old_index[path]
                except KeyError:
                    delta = Delta(100, new_file, None)
                    delta.factors.append('added')
                    self.deltas.append(delta)
                    continue

                # at this point, we have a delta_old_file.
                # we need to determine wheather this is identical,
                # or a modification.
                for f in delta_old_files:
                    # TODO: make sure sha1 is NOT empty
                    if new_file.sha1 == f.sha1:
                        delta = Delta(0, new_file, f)
                        delta.factors.append('unmodified')
                        self.deltas.append(delta)
                        continue
                    else:
                        delta = Delta(20, new_file, f)
                        delta.factors.append('modified')
                        self.deltas.append(delta)

        # now time to find the added.
        for path, old_files in old_index.items():
            for old_file in old_files:
                old_files_visited += 1

                if old_file.type != 'file':
                    continue

                try:
                    # This file already classified as 'modified' or 'unmodified' so do nothing
                    new_index[path]
                except KeyError:
                    delta = Delta(10, None, old_file)
                    delta.factors.append('removed')
                    self.deltas.append(delta)
                    continue

        # make sure everything is accounted for
        if new_files_visited != self.new.files_count:
            self.errors.append("Deltacode Error: Number of visited files({}) does not match total_files({}) in the new scan".format(new_files_visited, self.new.files_count))
        if old_files_visited != self.old.files_count:
            self.errors.append("Deltacode Error: Number of visited files({}) does not match total_files({}) in the old scan".format(old_files_visited, self.old.files_count))

    def determine_moved(self):
        """
        Modify the list of Delta objects by creating an index of
        'removed' Delta objects and an index of 'added' Delta objects indexed
        by their 'sha1' attribute, identifying any unique pairs of Deltas in
        both indices with the same 'sha1' and File 'name' attributes, and
        converting each such pair of 'added' and 'removed' Delta objects to a
        'moved' Delta object.  The 'added' and 'removed' indices are defined by
        the 'score' attribute of the Delta objects.
        """
        added = self.index_deltas('sha1', [i for i in self.deltas if i.score == 100])
        removed = self.index_deltas('sha1', [i for i in self.deltas if i.score == 10])

        # TODO: should it be iteritems() or items()
        for added_sha1, added_deltas in added.iteritems():
            for removed_sha1, removed_deltas in removed.iteritems():

                # check for matching sha1s on both sides
                if utils.check_moved(added_sha1, added_deltas, removed_sha1, removed_deltas):
                    self.update_deltas(added_deltas.pop(), removed_deltas.pop())

    def update_deltas(self, added, removed):
        """
        Convert the matched 'added' and 'removed' Delta objects to a combined
        'moved' Delta object -- passing the appropriate 'score' during object
        creation -- and delete the 'added' and 'removed' objects.
        """
        delta = Delta(5, added.new_file, removed.old_file)
        delta.factors.append('moved')
        self.deltas.append(delta)
        self.deltas.remove(added)
        self.deltas.remove(removed)

    def license_diff(self):
        """
        Compare the license details for a pair of 'new' and 'old' File objects
        in a Delta object and change the Delta object's 'score' attribute --
        and add an appropriate category (e.g., 'license info removed', 'license
        info added' or 'license change') to the Delta object's 'factors'
        attribute -- if there has been a license change and depending on the
        nature of that change.
        """
        for i in self.deltas:
            if 20 <= i.score < 100:

                new_licenses = i.new_file.licenses or []
                old_licenses = i.old_file.licenses or []

                if len(i.new_file.licenses) > 0 and i.old_file.licenses == []:
                    i.factors.append('license info added')
                    i.score += 20
                    return

                if i.new_file.licenses == [] and len(i.old_file.licenses) > 0:
                    i.factors.append('license info removed')
                    i.score += 15
                    return

                new_keys = set(l.key for l in new_licenses)
                old_keys = set(l.key for l in old_licenses)

                if new_keys != old_keys:
                    i.factors.append('license change')
                    i.score += 10

    def index_deltas(self, index_key='path', delta_list=[]):
        """
        Return a dictionary of a list of Delta objects indexed by the key
        passed via the 'index_key' variable.  If no 'index_key' variable is
        passed, the dict is keyed by the Delta object's 'path' variable.  For a
        'removed' Delta object -- identified by its 'score' attribute -- use
        the variable from the 'old_file'; for all other Delta objects (e.g.,
        'added'), use the 'new_file'.  This function does not currently catch
        the AttributeError exception.
        """
        index = {}

        for delta in delta_list:
            # FIXME: This is an ugly way to do this.
            if delta.score == 10:
                key = getattr(delta.old_file, index_key)
            else:
                key = getattr(delta.new_file, index_key)

            if index.get(key) is None:
                index[key] = []
                index[key].append(delta)
            else:
                index[key].append(delta)

        return index


class Delta(object):
    """
    A tuple reflecting a comparison of two files -- each of which is a File
    object -- and the 'factors' (e.g., 'added', 'modified' etc.) and related
    'score' that characterize that comparison.
    """
    def __init__(self, score=0, new_file=None, old_file=None):
        self.new_file = new_file if new_file else None
        self.old_file = old_file if old_file else None
        self.factors = []
        self.score = score

    def to_dict(self):
        """
        Return an OrderedDict comprising the 'factors', 'score' and new and old
        'path' attributes of the object.
        """
        if self.new_file:
            new_file = self.new_file.to_dict()
        else:
            new_file = None

        if self.old_file:
            old_file = self.old_file.to_dict()
        else:
            old_file = None

        return OrderedDict([
            ('factors', self.factors),
            ('score', self.score),
            ('new', new_file),
            ('old', old_file),
        ])
