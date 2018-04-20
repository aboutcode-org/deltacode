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

from scancode.resource import VirtualCodebase

# from deltacode.models import File
# from deltacode.models import Scan
from deltacode import utils


class DeltaCode_VC(object):
    """
    Handle the basic operations on a pair of incoming ScanCode scans (in JSON
    format) and the Delta objects created from a comparison of the files (in
    the form of File objects) contained in those scans.
    """
    def __init__(self, new_path, old_path, options):
        # self.new = Scan(new_path)
        # self.old = Scan(old_path)
        self.options = options
        self.deltas = []
        self.errors = []

        # self.new_codebase = VirtualCodebase(new_path, {})
        # self.old_codebase = VirtualCodebase(old_path, {})

        try:
            self.new_codebase = VirtualCodebase(new_path, {})
            self.old_codebase = VirtualCodebase(old_path, {})
        except KeyError:
            self.errors.append('KeyError: legacy ScanCode version')
            print('\n\nOOPS -- KeyError!!!\n')

        print('\n\nself.new_codebase = {}\n'.format(self.new_codebase))

        # if self.new.path != '' and self.old.path != '':
        if self.new_codebase is not None and self.old_codebase is not None:
            self.determine_delta()
            self.determine_moved()
            self.license_diff()
            self.copyright_diff()
            # Sort deltas by score, descending, i.e., high > low, and then by
            # factors, alphabetically.  Run the least significant sort first.
            # self.deltas.sort(key=lambda Delta: Delta.factors, reverse=False)
            # self.deltas.sort(key=lambda Delta: Delta.score, reverse=True)
            self.deltas.sort(key=lambda Delta_VC: Delta_VC.factors, reverse=False)
            self.deltas.sort(key=lambda Delta_VC: Delta_VC.score, reverse=True)

    # def align_scans(self):
    #     """
    #     Seek to align the paths of a pair of files (File objects) in the pair
    #     of incoming scans so that the attributes and other characteristics of
    #     the files can be compared with one another.  Call utils.fix_trees(),
    #     which calls utils.align_trees().
    #     """
    #     try:
    #         utils.fix_trees(self.new.files, self.old.files)
    #     except utils.AlignmentException:
    #         for f in self.new.files:
    #             f.original_path = f.path
    #         for f in self.old.files:
    #             f.original_path = f.path

    def determine_delta(self):
        """
        Add to a list of Delta objects that can be sorted by their attributes,
        e.g., by Delta.score.  Return None if no File objects can be loaded
        from either scan.
        """
        print('\n\nINSIDE DETERMINE_DELTA()\n')
        # align scan and create our index
        # 4/12/18  TODO: test whether we want or need this.  For the time being, don't use -- comment out.
        # self.align_scans()

        # new_index = self.new.index_files()
        # old_index = self.old.index_files()

        new_index = index_resources(self.new_codebase)
        old_index = index_resources(self.old_codebase)

        # print('\n\nnew_index = {}\n'.format(new_index))
        for resource in new_index:
            print('\n\nfor resource in new_index, print resource = {}\n'.format(resource))
            print('\n\nnew_index.get(resource) = {}\n'.format(new_index.get(resource)))
            print('\n\nself.new_codebase.compute_counts() = {}\n'.format(self.new_codebase.compute_counts()))
            # print('\n\nresource.compute_counts() = {}\n'.format(resource.compute_counts()))  #  no attribute etc.

        results_new = list(self.new_codebase.walk())
        print('\n\nself.new_codebase.walk() = {}\n'.format(results_new))
        resource_index = 0
        for resource in results_new:
            print('----------------------------\n')
            print('for resource in self.new_codebase.walk(), resource = \n\n{}  \n'.format(resource))
            # print(self.new_codebase.compute_counts()[resource_index])

            print('resource_index = {}'.format(resource_index))
            print('resource.pid = {}'.format(resource.pid))
            print('resource.rid = {}'.format(resource.rid))
            print('resource.path = {}'.format(resource.path))
            print('resource.name = {}'.format(resource.name))
            print('resource.has_children() = {}'.format(resource.has_children()))
            print('resource.children_rids = {}'.format(resource.children_rids))
            print('resource.has_siblings(self.new_codebase) = {}\n'.format(resource.has_siblings(self.new_codebase)))
            # print('resource.siblings(self.new_codebase) = {}'.format(resource.siblings(self.new_codebase)))
            resource_has_siblings = resource.has_siblings(self.new_codebase)
            if resource_has_siblings:
                resource_siblings = resource.siblings(self.new_codebase)
                for sibling in resource_siblings:
                    print('\tsibling.pid = {}'.format(sibling.pid))
                    print('\tsibling.rid = {}'.format(sibling.rid))
                    print('\tsibling.path = {}'.format(sibling.path))
                    print('\tsibling.name = {}\n'.format(sibling.name))
            else:
                print('\t==no siblings==\n')
            print('resource.location = {}'.format(resource.location))
            print('resource.cache_location = {}'.format(resource.cache_location))
            print('resource.files_count = {}'.format(resource.files_count))
            print('resource.dirs_count = {}'.format(resource.dirs_count))
            print('resource.size_count = {}'.format(resource.size_count))
            print('resource.is_file = {}'.format(resource.is_file))
            print('resource.is_filtered = {}'.format(resource.is_filtered))
            print('resource.date = {}'.format(resource.date))
            print('resource.size = {}'.format(resource.size))
            print('len(resource.licenses) = {}'.format(len(resource.licenses)))
            # TODO: explore the copyrights
            for license in resource.licenses:
                print('for license in resource.licenses, license.get(\'key\') = {}'.format(license.get('key')))
            resource_index += 1  # xxx
            print('\n----------------------------\n')

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
                    # delta = Delta(100, new_file, None)
                    delta = Delta_VC(100, new_file, None)
                    delta.factors.append('added')
                    self.deltas.append(delta)
                    continue

                # at this point, we have a delta_old_file.
                # we need to determine wheather this is identical,
                # or a modification.
                for f in delta_old_files:
                    # TODO: make sure sha1 is NOT empty
                    if new_file.sha1 == f.sha1:
                        # delta = Delta(0, new_file, f)
                        delta = Delta_VC(0, new_file, f)
                        delta.factors.append('unmodified')
                        self.deltas.append(delta)
                        continue
                    else:
                        # delta = Delta(20, new_file, f)
                        delta = Delta_VC(20, new_file, f)
                        delta.factors.append('modified')
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
                    # delta = Delta(0, None, old_file)
                    delta = Delta_VC(0, None, old_file)
                    delta.factors.append('removed')
                    self.deltas.append(delta)
                    continue

        # print('\n\nGETTING READY TO CHECK FILES_COUNT\n')
        # print('\n\ntype(self.new_codebase) = {}\n'.format(type(self.new_codebase)))
        # results_new = list(self.new_codebase.walk())
        # print('\n\nresults_new = {}\n'.format(results_new))

        # results_new = list(self.new_codebase.walk())[0]
        # # print(results_new)
        # print(help(results_new))

        # print(help(self.new_codebase))

        test = self.new_codebase.compute_counts()
        print('test = {}'.format(test))


        # make sure everything is accounted for
        # if new_visited != self.new.files_count:
        # if new_visited != self.new_codebase.files_count:
            # self.errors.append(
            #     'DeltaCode Warning: new_visited({}) != new_total({}). Assuming old scancode format.'.format(new_visited, self.new.files_count)
            # )

        new_files_count = self.new_codebase.compute_counts()[0]
        old_files_count = self.old_codebase.compute_counts()[0]

        if new_visited != new_files_count:
            self.errors.append(
                'DeltaCode Warning: new_visited({}) != new_total({}). Assuming old scancode format.'.format(new_visited, new_files_count)
            )

        # if old_visited != self.old.files_count:
            # self.errors.append(
            #     'DeltaCode Warning: old_visited({}) != old_total({}). Assuming old scancode format.'.format(old_visited, self.old.files_count)
            # )
        if old_visited != old_files_count:
            self.errors.append(
                'DeltaCode Warning: old_visited({}) != old_total({}). Assuming old scancode format.'.format(old_visited, old_files_count)
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
        # added = self.index_deltas('sha1', [i for i in self.deltas if i.old_file is None and i.new_file])
        # removed = self.index_deltas('sha1', [i for i in self.deltas if i.old_file and i.new_file is None])
        added = self.index_deltas('sha1', [i for i in self.deltas if i.old_resource is None and i.new_resource])
        removed = self.index_deltas('sha1', [i for i in self.deltas if i.old_resource and i.new_resource is None])
        print('\n\nadded = {}\n'.format(added))
        print('\n\nremoved = {}\n'.format(removed))

        # TODO: should it be iteritems() or items()
        for added_sha1, added_deltas in added.iteritems():
            for removed_sha1, removed_deltas in removed.iteritems():

                # check for matching sha1s on both sides
                # if utils.check_moved(added_sha1, added_deltas, removed_sha1, removed_deltas):
                #     self.update_deltas(added_deltas.pop(), removed_deltas.pop())
                if check_moved(added_sha1, added_deltas, removed_sha1, removed_deltas):
                    self.update_deltas(added_deltas.pop(), removed_deltas.pop())

    def update_deltas(self, added, removed):
        """
        Convert the matched 'added' and 'removed' Delta objects to a combined
        'moved' Delta object -- passing the appropriate 'score' during object
        creation -- and delete the 'added' and 'removed' objects.
        """
        # delta = Delta(0, added.new_file, removed.old_file)
        delta = Delta_VC(0, added.new_resource, removed.old_resource)
        delta.factors.append('moved')
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
            # key = getattr(delta.new_file if delta.new_file else delta.old_file, index_key)
            key = getattr(delta.new_resource if delta.new_resource else delta.old_resource, index_key)

            if index.get(key) is None:
                index[key] = []
                index[key].append(delta)
            else:
                index[key].append(delta)

        return index


class Delta_VC(object):
    """
    A tuple reflecting a comparison of two files -- each of which is a File
    object -- and the 'factors' (e.g., 'added', 'modified' etc.) and related
    'score' that characterize that comparison.
    """
    # def __init__(self, score=0, new_file=None, old_file=None):
    #     self.new_file = new_file if new_file else None
    #     self.old_file = old_file if old_file else None
    #     self.factors = []
    #     self.score = score

    def __init__(self, score=0, new_resource=None, old_resource=None):
        self.new_resource = new_resource if new_resource else None
        self.old_resource = old_resource if old_resource else None
        self.factors = []
        self.score = score

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
        # if self.score > 0 and self.old_file:
            # return True
        if self.score > 0 and self.old_resource:
            return True

    def is_unmodified(self):
        """
        Since 'unmodified' is no longer the only category/factor with a
        score = 0, test the Delta object's attributes for categories/factors
        other than 'unmodified' and return True if all but 'unmodified' are
        ruled out.
        """
        # if (self.new_file and self.old_file and
        #         self.new_file.sha1 == self.old_file.sha1 and
        #         self.new_file.path == self.old_file.path):
        #     return True
        if (self.new_resource and self.old_resource and
                self.new_resource.sha1 == self.old_resource.sha1 and
                self.new_resource.path == self.old_resource.path):
            return True

    def is_added(self):
        """
        Identify a Delta object reflecting the addition of a File.
        """
        # if self.new_file and not self.old_file:
        #     return True
        if self.new_resource and not self.old_resource:
            return True

    def to_dict(self):
        """
        Return an OrderedDict comprising the 'factors', 'score' and new and old
        'path' attributes of the object.
        """
        # if self.new_file:
        #     new_file = self.new_file.to_dict()
        # else:
        #     new_file = None

        # if self.old_file:
        #     old_file = self.old_file.to_dict()
        # else:
        #     old_file = None

        # return OrderedDict([
        #     ('factors', self.factors),
        #     ('score', self.score),
        #     ('new', new_file),
        #     ('old', old_file),
        # ])
        if self.new_resource:
            new_resource = self.new_resource.to_dict()
        else:
            new_resource = None

        if self.old_resource:
            old_resource = self.old_resource.to_dict()
        else:
            old_resource = None

        return OrderedDict([
            ('factors', self.factors),
            ('score', self.score),
            ('new', new_resource),
            ('old', old_resource),
        ])


def index_resources(codebase, index_key='path'):
    """
    Return a dictionary of a list of Resource objects indexed by the key passed via
    the 'key' variable.  If no 'key' variable is passed, the dict is
    keyed by the Resource object's 'path' variable.  This function does not
    currently catch the AttributeError exception.
    """
    index = {}

    for f in codebase.walk():
        key = getattr(f, index_key)

        if index.get(key) is None:
            index[key] = []
            index[key].append(f)
        else:
            index[key].append(f)

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
    # if added_deltas[0].new_file.name == removed_deltas[0].old_file.name:
    #     return True
    if added_deltas[0].new_resource.name == removed_deltas[0].old_resource.name:
        return True
