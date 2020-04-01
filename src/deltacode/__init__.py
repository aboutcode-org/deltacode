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

from deltacode.models import File
from deltacode.models import Scan
from deltacode import utils


from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution('deltacode').version
except DistributionNotFound:
    # package is not installed ??
    __version__ = '1.0.0'

SIMILARITY_LIMIT = 35

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
        self.stats = Stat(self.new.files_count, self.old.files_count)

        if self.new.path != '' and self.old.path != '':
            self.determine_delta()
            self.determine_moved()
            self.license_diff()
            self.copyright_diff()
            self.stats.calculate_stats()
            self.similarity()
            # Sort deltas by score, descending, i.e., high > low, and then by
            # factors, alphabetically.  Run the least significant sort first.
            self.deltas.sort(key=lambda Delta: Delta.factors, reverse=False)
            self.deltas.sort(key=lambda Delta: Delta.score, reverse=True)

    def align_scans(self):
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

    def similarity(self):
        """
        Compare the fingerprints of a pair of 'new' and 'old' File objects
        in a Delta object and change the Delta object's 'score' attribute --
        and add an appropriate category 'Similar with hamming distance'
        to the Delta object's 'factors' attribute -- if the hamming
        distance is less than the threshold distance.
        """
        for delta in self.deltas:
            if delta.new_file == None or delta.old_file == None:
                continue
            new_fingerprint = delta.new_file.fingerprint
            old_fingerprint = delta.old_file.fingerprint
            if new_fingerprint == None or old_fingerprint == None:
                continue
            new_fingerprint = utils.bitarray_from_hex(delta.new_file.fingerprint)
            old_fingerprint = utils.bitarray_from_hex(delta.old_file.fingerprint)
            hamming_distance = utils.hamming_distance(new_fingerprint, old_fingerprint)
            if hamming_distance > 0 and hamming_distance <= SIMILARITY_LIMIT:
                delta.score += hamming_distance
                delta.factors.append('Similar with hamming distance : {}'.format(hamming_distance))

    def determine_delta(self):
        """
        Add to a list of Delta objects that can be sorted by their attributes,
        e.g., by Delta.score.  Return None if no File objects can be loaded
        from either scan.
        """
        # align scan and create our index
        self.align_scans()
        new_index = self.new.index_files()
        old_index = self.old.index_files()

        # gathering counts to ensure no files lost or missing from our 'deltas' set
        new_visited, old_visited = 0, 0

        # perform the deltas
        for path, new_files in new_index.items():
            for new_file in new_files:

                if new_file.type != 'file':
                    continue

                new_visited += 1

                try:
                    delta_old_files = old_index[path]
                except KeyError:
                    delta = Delta(100, new_file, None)
                    delta.status = 'added'
                    self.stats.num_added += 1
                    self.deltas.append(delta)
                    continue

                # at this point, we have a delta_old_file.
                # we need to determine wheather this is identical,
                # or a modification.
                for f in delta_old_files:
                    # TODO: make sure sha1 is NOT empty
                    if new_file.sha1 == f.sha1:
                        delta = Delta(0, new_file, f)
                        delta.status = 'unmodified'
                        self.stats.num_unmodified += 1
                        self.deltas.append(delta)
                        continue
                    else:
                        delta = Delta(20, new_file, f)
                        delta.status = 'modified'
                        self.stats.num_modified += 1
                        self.deltas.append(delta)

        # now time to find the added.
        for path, old_files in old_index.items():
            for old_file in old_files:
                if old_file.type != 'file':
                    continue

                old_visited += 1

                try:
                    # This file already classified so do nothing
                    new_index[path]
                except KeyError:
                    delta = Delta(0, None, old_file)
                    delta.status = 'removed'
                    self.stats.num_removed += 1
                    self.deltas.append(delta)
                    continue

        # make sure everything is accounted for
        if new_visited != self.new.files_count:
            self.errors.append(
                'DeltaCode Warning: new_visited({}) != new_total({}). Assuming old scancode format.'.format(new_visited, self.new.files_count)
            )

        if old_visited != self.old.files_count:
            self.errors.append(
                'DeltaCode Warning: old_visited({}) != old_total({}). Assuming old scancode format.'.format(old_visited, self.old.files_count)
            )

    def determine_moved(self):
        """
        Modify the list of Delta objects by creating an index of
        'removed' Delta objects and an index of 'added' Delta objects indexed
        by their 'sha1' attribute, identifying any unique pairs of Deltas in
        both indices with the same 'sha1' and File 'name' attributes, and
        converting each such pair of 'added' and 'removed' Delta objects to a
        'moved' Delta object.  The 'added' and 'removed' indices are defined by
        the presence/absence of the object's 'old_file' and 'new_file'.
        """
        added = self.index_deltas('sha1', [i for i in self.deltas if i.old_file is None and i.new_file])
        removed = self.index_deltas('sha1', [i for i in self.deltas if i.old_file and i.new_file is None])

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
        delta = Delta(0, added.new_file, removed.old_file)
        delta.status = 'moved'
        self.stats.num_moved += 1
        self.stats.num_added -= 1
        self.stats.num_removed -= 1
        self.deltas.append(delta)
        self.deltas.remove(added)
        self.deltas.remove(removed)

    def license_diff(self):
        """
        Compare the license details for a pair of 'new' and 'old' File objects
        in a Delta object and change the Delta object's 'score' attribute --
        and add one or more appropriate categories (e.g., 'license change',
        'copyleft added') to the Delta object's 'factors' attribute -- if there
        has been a license change.
        """
        # TODO: Figure out the best way to handle this.
        unique_categories = set([
            'Commercial',
            'Copyleft',
            'Copyleft Limited',
            'Free Restricted',
            'Patent License',
            'Proprietary Free'
        ])

        for delta in self.deltas:
            utils.update_from_license_info(delta, unique_categories)

    def copyright_diff(self):
        """
        Compare the copyright details for a pair of 'new' and 'old' File objects
        in a Delta object and change the Delta object's 'score' attribute --
        and add an appropriate category (e.g., 'copyright info removed', 'copyright
        info added' or 'copyright change') to the Delta object's 'factors'
        attribute -- if there has been a copyright change.
        """
        for delta in self.deltas:
            utils.update_from_copyright_info(delta)

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
            key = getattr(delta.new_file if delta.new_file else delta.old_file, index_key)

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
        self.has_license = False
        self.has_copyright = False
        self.factors = []
        self.score = score
        self.status = ''

    def update(self, score=0, factor=''):
        """
        Add the score to the Delta object's 'score' attribute and add a string,
        summarizing the factor associated with the score, to the object's
        'factors' attribute (a list).
        """
        self.factors.append(factor)
        self.score += score

    def is_modified(self):
        """
        Identify a Delta object meriting attention to possible changes in its
        license or copyright content because the File object has been modified.
        """
        if self.score > 0 and self.old_file:
            return True

    def is_unmodified(self):
        """
        Since 'unmodified' is no longer the only category/factor with a
        score = 0, test the Delta object's attributes for categories/factors
        other than 'unmodified' and return True if all but 'unmodified' are
        ruled out.
        """
        if (self.new_file and self.old_file and
                self.new_file.sha1 == self.old_file.sha1 and
                self.new_file.path == self.old_file.path):
            return True

    def is_added(self):
        """
        Identify a Delta object reflecting the addition of a File.
        """
        if self.new_file and not self.old_file:
            return True

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
            ('status', self.status),
            ('factors', self.factors),
            ('score', self.score),
            ('new', new_file),
            ('old', old_file),
        ])

class Stat(object):
    """
    Contains all the stats for the file changes in the new directory
    with respect to the old directory.
    """
    def __init__(self, new_files_count, old_files_count):
        self.new_files_count = new_files_count
        self.old_files_count = old_files_count
        self.num_added = 0
        self.num_removed = 0
        self.num_moved = 0
        self.num_modified = 0
        self.num_unmodified = 0
        self.percent_added = 0
        self.percent_removed = 0
        self.percent_moved = 0
        self.percent_modified = 0
        self.percent_unmodified = 0

    def calculate_stats(self):
        """
        Calculates the percentage change of new directory with respect to
        the old directory.
        """
        self.percent_added = utils.calculate_percent(self.num_added, self.old_files_count)
        self.percent_removed = utils.calculate_percent(self.num_removed, self.old_files_count)
        self.percent_moved = utils.calculate_percent(self.num_moved, self.old_files_count)
        self.percent_modified = utils.calculate_percent(self.num_modified, self.old_files_count)
        self.percent_unmodified = utils.calculate_percent(self.num_unmodified, self.old_files_count)

    def to_dict(self):
        """
        Return an OrderedDict comprising all the percent attributes of the object.
        """
        return OrderedDict([
            ('old_files_count', self.old_files_count),
            ('new_files_count', self.new_files_count),
            ('percent_added', self.percent_added),
            ('percent_removed', self.percent_removed),
            ('percent_moved', self.percent_moved),
            ('percent_modified', self.percent_modified),
            ('percent_unmodified', self.percent_unmodified),
        ])

