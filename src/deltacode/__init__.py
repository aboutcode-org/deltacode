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

import os
from collections import OrderedDict

from deltacode import utils
from commoncode import paths
from commoncode.resource import VirtualCodebase


from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution("deltacode").version
except DistributionNotFound:
    # package is not installed ??
    __version__ = "1.0.0"

SIMILARITY_LIMIT = 35


class DeltaCode(object):
    """
    Handle the basic operations on a pair of incoming ScanCode scans (in JSON
    format) and the Delta objects created from a comparison of the files (in
    the form of File objects) contained in those scans.
    """

    def __init__(self, new_path, old_path, options):
        self.codebase1 = None
        self.codebase2 = None
        self.options = options
        self.deltas = []
        self.errors = []

        self._populate(new_path, old_path)
        
        self.new_scan_options = []
        self.old_scan_options = []
        self.determine_delta()
        self.options_diff()
        self.license_diff()
        self.copyright_diff()
        self.stats.calculate_stats()
        self.similarity()
        # Sort deltas by score, descending, i.e., high > low, and then by
        # factors, alphabetically.  Run the least significant sort first.
        self.deltas.sort(key=lambda Delta: Delta.factors, reverse=False)
        self.deltas.sort(key=lambda Delta: Delta.score, reverse=True)

    def _populate(self, new_path, old_path):
        if os.path.isfile(new_path) and os.path.isfile(old_path):
            self.codebase1 = VirtualCodebase(new_path)
            self.codebase2 = VirtualCodebase(old_path)
        else:
            error_message = (
                "{} is expected to be a file".format(new_path)
                if not os.path.isfile(new_path)
                else "{} is expected to be a file".format(old_path)
            )
            raise utils.FileError(error_message)
        self.stats = Stat(
            self.codebase1.compute_counts()[0], self.codebase2.compute_counts()[0]
        )

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
            new_fingerprint = (
                delta.new_file.fingerprint
                if hasattr(delta.new_file, "fingerprint")
                else None
            )
            old_fingerprint = (
                delta.old_file.fingerprint
                if hasattr(delta.old_file, "fingerprint")
                else None
            )

            if new_fingerprint == None or old_fingerprint == None:
                continue
            new_fingerprint = utils.bitarray_from_hex(delta.new_file.fingerprint)
            old_fingerprint = utils.bitarray_from_hex(delta.old_file.fingerprint)

            hamming_distance = utils.hamming_distance(new_fingerprint, old_fingerprint)
            if hamming_distance > 0 and hamming_distance <= SIMILARITY_LIMIT:
                delta.score += hamming_distance
                delta.factors.append(
                    "Similar with hamming distance : {}".format(hamming_distance)
                )

    def create_deltas(
        self, new_resource, old_resource, new_path, old_path, score, status
    ):
        """
        Creates the Delta Objects and appends them to the member list.
        """
        delta = Delta(score, new_resource, old_resource)
        delta.status = status
        self.deltas.append(delta)

    def determine_delta(self):
        """
        Create Delta objects and append them to the list. Top Down BFS Traversal is used 
        to visit the codebase structures of the old and new Codebase Directiries.
        """

        old_resource_considered = set()
        # Set to keep track of the old resources visited
        try:
            Delta.NEW_CODEBASE_OFFSET, Delta.OLD_CODEBASE_OFFSET = utils.align_trees(
                self.codebase1, self.codebase2
            )
        except utils.AlignmentException:
            Delta.NEW_CODEBASE_OFFSET, Delta.OLD_CODEBASE_OFFSET = 0, 0

        for new_resource in self.codebase1.walk():
            # Visit each resource of the new codebase in a Top Down BFS fashion
            if new_resource.is_file: 
                path_new = "/".join(
                    paths.split(new_resource.path)[Delta.NEW_CODEBASE_OFFSET :]
                )
            # If the resource is a file align its path

                old_resource = self.codebase2.get_resource_from_path(path_new)
                # Check in the old codebase weather a resource with such a path exists or not
                # if it exists and their corresponding sha's are same then its an unmodified delta

                if old_resource and old_resource.sha1 == new_resource.sha1:
                    old_resource_considered.add(old_resource.path)
                    path_old = "/".join(
                        paths.split(old_resource.path)[Delta.OLD_CODEBASE_OFFSET :]
                    )
                    self.create_deltas(
                        new_resource, old_resource, path_new, path_old, 0, "unmodified",
                    )
                    self.stats.num_unmodified += 1

                    continue
                
                
                # Now when  we do not get old resources with the same name 
                ADDED = True
                for old_resource in self.codebase2.walk():
                    # Visit each resource of the new codebase in a Bottom Up BFS fashion
                    if old_resource.path in old_resource_considered:
                        # If old resources are previously considered then continue
                        continue
                    path_old = "/".join(
                        paths.split(old_resource.path)[Delta.OLD_CODEBASE_OFFSET :]
                    )
                    # Make the path aligned
                    if (
                        old_resource.is_file
                        and not old_resource.path in old_resource_considered
                    ):
                    # If the old resource is a file and currently unvisited

                        if path_new == path_old:
                            # Old and New Resources are having the same path after alignment
                            ADDED = False
                            if new_resource.sha1 == old_resource.sha1:
                                # They are having same sha1
                                old_resource_considered.add(old_resource.path)
                                self.create_deltas(
                                    new_resource,
                                    old_resource,
                                    path_new,
                                    path_old,
                                    0,
                                    "unmodified",
                                )
                                self.stats.num_unmodified += 1
                                break
                            else:
                                # They are having different sha1
                                old_resource_considered.add(old_resource.path)
                                self.create_deltas(
                                    new_resource,
                                    old_resource,
                                    path_new,
                                    path_old,
                                    20,
                                    "modified",
                                )
                                self.stats.num_modified += 1
                                break
                        else:
                            # Their paths are different
                            if new_resource.sha1 == old_resource.sha1:
                                # THey are having the same sha1
                                old_resource_considered.add(old_resource.path)
                                ADDED = False
                                self.create_deltas(
                                    new_resource,
                                    old_resource,
                                    path_new,
                                    path_old,
                                    0,
                                    "moved",
                                )
                                self.stats.num_moved += 1
                                break

                if ADDED:
                    # If none of the above criteria matches then the delta is an added one.
                    self.create_deltas(
                        new_resource, None, path_new, None, 100, "added",
                    )
                    self.stats.num_added += 1

        for old_resource_remaining in self.codebase2.walk():
            # Now again visit the old codebase in a top down fashion
            # If any delta is left out it is a case of removed delta 
            if (
                old_resource_remaining.is_file
                and old_resource_remaining.path not in old_resource_considered
            ):
                path_old = "/".join(
                    paths.split(old_resource_remaining.path)[
                        Delta.OLD_CODEBASE_OFFSET :
                    ]
                )
                self.create_deltas(
                    None, old_resource_remaining, None, path_old, 0, "removed",
                )
                self.stats.num_removed += 1

    def license_diff(self):
        """
        Compare the license details for a pair of 'new' and 'old' File objects
        in a Delta object and change the Delta object's 'score' attribute --
        and add one or more appropriate categories (e.g., 'license change',
        'copyleft added') to the Delta object's 'factors' attribute -- if there
        has been a license change.
        """
        # TODO: Figure out the best way to handle this.
        unique_categories = set(
            [
                "Commercial",
                "Copyleft",
                "Copyleft Limited",
                "Free Restricted",
                "Patent License",
                "Proprietary Free",
            ]
        )

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

    def options_diff(self):
        try:
            self.new_scan_options = self.codebase1.get_headers()[0].get("options", "")
            self.old_scan_options = self.codebase2.get_headers()[0].get("options", "")
        except IndexError as exception:
            pass


class Delta(object):
    """
    A tuple reflecting a comparison of two files -- each of which is a File
    object -- and the 'factors' (e.g., 'added', 'modified' etc.) and related
    'score' that characterize that comparison.
    """

    NEW_CODEBASE_OFFSET = 0
    OLD_CODEBASE_OFFSET = 0

    def __init__(self, score=0, new_file=None, old_file=None):
        self.new_file = new_file if new_file else None
        self.old_file = old_file if old_file else None
        self.factors = []
        self.score = score
        self.status = ""

    def update(self, score=0, factor=""):
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
        if (
            self.new_file
            and self.old_file
            and self.new_file.sha1 == self.old_file.sha1
            and self.new_file.path == self.old_file.path
        ):
            return True

    def is_added(self):
        """
        Identify a Delta object reflecting the addition of a File.
        """
        if self.new_file and not self.old_file:
            return True

    def copyrights_to_dict(self, file):
        """
        Given a Copyright object, return an OrderedDict with the full
        set of fields from the ScanCode 'copyrights' value.
        """
        copyrights = []
        try:
            copyrights = file.copyrights
        except AttributeError:
            return []

        all_copyrights = []
        for copyright in copyrights:
            all_copyrights.append(
                OrderedDict(
                    [
                        ("statements", copyright.get("statements", None)),
                        ("holders", copyright.get("holders", None)),
                    ]
                )
            )

        return all_copyrights

    def licenses_to_dict(self, file):
        """
        Given a License object, return an OrderedDict with the full
        set of fields from the ScanCode 'license' value.
        """
        licenses = []
        try:
            for license in file.licenses:
                licenses.append(
                    OrderedDict(
                        [
                            ("key", license.get("key", None)),
                            ("score", license.get("score", None)),
                            ("short_name", license.get("short_name", None)),
                            ("category", license.get("category", None)),
                            ("owner", license.get("owner", None)),
                        ]
                    )
                )
            return licenses
        except:
            return []

    def file_to_dict(self, deltacode, file, new_file=True):

        path_offset = (
            Delta.NEW_CODEBASE_OFFSET if new_file else Delta.OLD_CODEBASE_OFFSET
        )
        if file:
            return OrderedDict(
                [
                    ("path", "/".join(paths.split(file.path)[path_offset:])),
                    ("type", file.type),
                    ("name", file.name),
                    ("size", file.size),
                    ("sha1", file.sha1),
                    (
                        "fingerprint",
                        file.fingerprint if hasattr(file, "fingerprint") else "",
                    ),
                    ("original_path", file.path),
                    ("licenses", self.licenses_to_dict(file)),
                    ("copyrights", self.copyrights_to_dict(file)),
                ]
            )

    def to_dict(self, deltacode):
        """
        Return an OrderedDict comprising the 'factors', 'score' and new and old
        'path' attributes of the object.
        """
        if (
            not deltacode.options.get("--all-delta-types", "") == True
            and self.status == "unmodified"
        ):
            return
        if self.new_file:
            new_file = self.new_file.to_dict()
        else:
            new_file = None

        if self.old_file:
            old_file = self.old_file.to_dict()
        else:
            old_file = None

        return OrderedDict(
            [
                ("status", self.status),
                ("factors", self.factors),
                ("score", self.score),
                ("new", self.file_to_dict(deltacode, self.new_file, new_file=True)),
                ("old", self.file_to_dict(deltacode, self.old_file, new_file=False)),
            ]
        )


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
        self.percent_added = utils.calculate_percent(
            self.num_added, self.old_files_count
        )
        self.percent_removed = utils.calculate_percent(
            self.num_removed, self.old_files_count
        )
        self.percent_moved = utils.calculate_percent(
            self.num_moved, self.old_files_count
        )
        self.percent_modified = utils.calculate_percent(
            self.num_modified, self.old_files_count
        )
        self.percent_unmodified = utils.calculate_percent(
            self.num_unmodified, self.old_files_count
        )

    def to_dict(self):
        """
        Return an OrderedDict comprising all the percent attributes of the object.
        """
        return OrderedDict(
            [
                ("old_files_count", self.old_files_count),
                ("new_files_count", self.new_files_count),
                ("percent_added", self.percent_added),
                ("percent_removed", self.percent_removed),
                ("percent_moved", self.percent_moved),
                ("percent_modified", self.percent_modified),
                ("percent_unmodified", self.percent_unmodified),
            ]
        )
