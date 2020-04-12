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
import click

from deltacode.models import File
from deltacode.models import Scan
from deltacode import utils
from scancode.resource import VirtualCodebase


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
        self.codebase1 = None
        self.codebase2 = None
        try:
            self.codebase1 = VirtualCodebase(new_path)
            self.codebase2 = VirtualCodebase(old_path)
        except Exception as exception:
            click.secho(exception.message ,fg = "red")
        self.new_files_count = 0 #keeps the count of the new file
        self.old_files_count = 0 #keeps the count of old files
        self.new_files = [] # a list of [[new file1:Original path],[new file2:Original Path],...]
        self.old_files = [] # a list of [[old file1:Original path],[old file2:Original Path],...]
        self.new_files_fingerprint = dict() # map of { {new_file1:fingerprint},{new_file2:fingerprint},...} it will be needed when we need the fingerprints
        self.old_files_fingerprint = dict() # map of { {old_file1:fingerprint},{old_file2:fingerprint},...}
        self.new_files_original_path = dict() #this keeps a map of the path of file with respect to original path 
        self.old_files_original_path = dict()
        self.options = options
        self.deltas = []
        self.errors = []
       
        if self.codebase1 != None and self.codebase2 != None:
            self.enumerate_files_from_codebases()
            self.stats = Stat(self.new_files_count, self.old_files_count) 
            self.new_files_errors = []
            self.old_files_errors = []
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

    def get_files(self,codebase,is_new):
        """
        Walk through the codebase, then generate the resources it(including all files and its directories)
        then we enumerate over this generated codebase to get file, and directories as (obj)
        Now during the time of enumeration we append files in the self.new_files list and incremants out self.new_files_count
        Similarly for old_files.
        Now , we also maintain a map which maps from object path to its fingerprint.
        This map will be required when we calculate the hamming distances and compare similarity.
        """
        resources = codebase.walk_filtered(topdown=True)
        for i,obj in enumerate(resources):            
            if is_new:
                # append in the new_files
                self.new_files.append([obj,''])
                try :
                    self.new_files_fingerprint[obj.path] = obj.fingerprint
                except AttributeError:
                    self.new_files_fingerprint[obj.path] = None
                if obj.is_file:
                    # increment the new files count
                    self.new_files_count += 1

            else:
                # append in the old files
                self.old_files.append([obj,''])
                try:
                    self.old_files_fingerprint[obj.path] = obj.fingerprint
                except AttributeError:
                    self.old_files_fingerprint[obj.path] = None
                if obj.is_file:
                    # increment the old files count
                    self.old_files_count += 1
                    

    def enumerate_files_from_codebases(self):
       """
       An method which call the utility function get_files for generating the codebase
       """
       self.get_files(self.codebase1,is_new = True)
       self.get_files(self.codebase2,is_new = False)
        

    def align_scans(self):
        """
        Seek to align the paths of a pair of files (File objects) in the pair
        of incoming scans so that the attributes and other characteristics of
        the files can be compared with one another.  Call utils.fix_trees(),
        which calls utils.align_trees().
        """
        try:
            self.new_files_original_path , self.old_files_original_path = utils.fix_trees(self.new_files, self.old_files)
        except utils.AlignmentException:
            # self.new_files is a list of type [[ScannedResourceObject,originalPath],...]
            # initially all original path are set to empty string
            # so this part actually sets the original paths 
            for f in self.new_files:
                f[1] = f[0].path
            for f in self.old_files:
                f[1] = f[0].path

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
            # this extracts the fingerprint corresponding to the particular file path
            
            new_fingerprint = self.new_files_fingerprint.get(delta.new_file.path,None)
            old_fingerprint = self.old_files_fingerprint.get(delta.old_file.path,None)
            if new_fingerprint == None or old_fingerprint == None:
                continue
            new_fingerprint = utils.bitarray_from_hex(self.new_files_fingerprint[delta.new_file.path])
            old_fingerprint = utils.bitarray_from_hex(self.old_files_fingerprint[delta.old_file.path])
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
        # returns file index wrt to old and new files
        new_index = utils.index_files(self.new_files)
        old_index = utils.index_files(self.old_files)
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
        if new_visited != self.new_files_count:
            self.errors.append(
                'DeltaCode Warning: new_visited({}) != new_total({}). Assuming old scancode format.'.format(new_visited, self.new.files_count)
            )

        if old_visited != self.old_files_count:
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

    def copyrights_to_dict(self,file):
        """
        Given a Copyright object, return an OrderedDict with the full
        set of fields from the ScanCode 'copyrights' value.
        """
        copyrightC = []
        try :
            copyrightC = file.copyrights
        except AttributeError:
            # arises when the ScannedResource do not have any license attribute
            return []
        if len(copyrightC) == 0:
            return []
        if isinstance(copyrightC[0],OrderedDict):
            # all the copyright are in correct format
            all_copyrights = []
            for i in range(len(copyrightC)):
                # we iterate over all the copyrights
                statements = copyrightC[i].get("statements",None)
                holders = copyrightC[i].get("holders",None)
                d = OrderedDict([
                    ('statements', statements),
                    ('holders', holders)
                ])
                all_copyrights.append(d)

            return all_copyrights

    def licenses_to_dict(self,file):
        """
        Given a License object, return an OrderedDict with the full
        set of fields from the ScanCode 'license' value.
        """
        licenseL = []
        try:
            licenseL = file.licenses
        except AttributeError:
            # arises when the ScannedResource do not have any license attribute
            return []

        if len(licenseL) == 0:
            return []
        if isinstance(licenseL[0],OrderedDict):
            # the licenses are in the correct format
            all_licenses = []
            for i in range(len(licenseL)):
                # we iterate over all the licenses
                key = licenseL[i].get("key",None)
                score = licenseL[i].get("score",None)
                short_key = licenseL[i].get("short_name",None)
                category = licenseL[i].get("category",None)
                owner = licenseL[i].get("owner",None)
                d = OrderedDict([
                    ('key', key),
                    ('score', score),
                    ('short_name', short_key),
                    ('category', category),
                    ('owner', owner)
                ])
                all_licenses.append(d)
            return all_licenses

    def new_file_to_dict(self,deltacode):
        # if self.new_file is not empty we return the new file attributes
        if self.new_file:
            return OrderedDict([
                ("path",self.new_file.path),
                ("type",self.new_file.type),
                ("name",self.new_file.name),
                ("size",self.new_file.size),
                ("sha1",self.new_file.sha1),
                ("fingerprint",deltacode.new_files_fingerprint.get(self.new_file.path,"")),
                ("original_path",deltacode.new_files_original_path.get(self.new_file.path, "")),
                # since license itself has many sub fields so we obtain it from another utility function
                ("licenses",self.licenses_to_dict(self.new_file)),
                # since copyright itself has many sub fields so we obtain it from another utility function
                ("copyrights",self.copyrights_to_dict(self.new_file))          
            ])
        
    
    def old_file_to_dict(self,deltacode):
        if self.old_file :
            return OrderedDict([
                ("path",self.old_file.path),
                ("type",self.old_file.type),
                ("name",self.old_file.name),
                ("size",self.old_file.size),
                ("sha1",self.old_file.sha1),
                ("fingerprint",deltacode.old_files_fingerprint.get(self.old_file.path,"")),
                ("original_path",deltacode.old_files_original_path.get(self.old_file.path, "")),
                # since license itself has many sub fields so we obtain it from another utility function
                ("licenses",self.licenses_to_dict(self.old_file)),
                # since copyright itself has many sub fields so we obtain it from another utility function
                ("copyrights",self.copyrights_to_dict(self.old_file))       
            ])


    def to_dict(self,deltacode):
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
            # receives the detail of the new file
            ('new', self.new_file_to_dict(deltacode)),
            # receives the details of the old file 
            ('old', self.old_file_to_dict(deltacode)),
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
