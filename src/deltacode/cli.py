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

import csv

import click
import simplejson

from deltacode import DeltaCode
from deltacode import __version__
from deltacode.utils import deltas, get_notice


# FIXME: update the function argument delta to deltacode
def write_csv(delta, result_file, all_delta_types=False):
    """
    Using the DeltaCode object, create a .csv file
    containing the primary information from the Delta objects.  Omit all Delta
    objects whose 'category' is 'unmodified' unless the user selects the
    '-a'/'--all' option.
    """
    with open(result_file, 'wb') as out:
        csv_out = csv.writer(out)
        csv_out.writerow(['Type of delta', 'Path', 'Name', 'Type', 'Size', 'Old Path'])
        for row in [(
            f.category,
            f.old_file.path if f.category == 'removed' else f.new_file.path,
            f.old_file.name if f.category == 'removed' else f.new_file.name,
            f.old_file.type if f.category == 'removed' else f.new_file.type,
            f.old_file.size if f.category == 'removed' else f.new_file.size,
            f.old_file.path if f.category == 'moved' else '')
                for d in delta.deltas for f in delta.deltas.get(d)]:
                    if all_delta_types is True:
                        csv_out.writerow(row)
                    elif row[0] != 'unmodified':
                        csv_out.writerow(row)


def write_json(deltacode, outfile, all_delta_types=False):
    """
    Using the DeltaCode object, create a .json file containing the primary
    information from the Delta objects.  Omit all Delta objects whose
    'category' is 'unmodified' unless the user selects the
    '-a'/'--all-delta-types' option.
    """
    results = OrderedDict([
        ('deltacode_notice', get_notice()),
        ('deltacode_options', deltacode.options),
        ('deltacode_version', __version__),
        ('deltacode_stats', deltacode.get_stats()),
        ('deltas', deltas(deltacode, all_delta_types)),
    ])

    # TODO: add toggle for pretty printing
    simplejson.dump(results, outfile, iterable_as_array=True, indent=2)
    outfile.write('\n')


@click.command()
@click.help_option('-h', '--help')
@click.option('-n', '--new', required=True, prompt=False, type=click.Path(exists=True, readable=True), help='Identify the path to the "new" scan file')
@click.option('-o', '--old', required=True, prompt=False, type=click.Path(exists=True, readable=True), help='Identify the path to the "old" scan file')
@click.option('-c', '--csv-file', prompt=False, type=click.Path(exists=False), help='Identify the path to the .csv output file')
@click.option('-j', '--json-file', prompt=False, default='-', type=click.File(mode='wb', lazy=False), help='Identify the path to the .json output file')
@click.option('-a', '--all-delta-types', is_flag=True, help="Include unmodified files as well as all changed files in the .json or .csv output.  If not selected, only changed files are included.")
def cli(new, old, csv_file, json_file, all_delta_types):
    """
    Identify the changes that need to be made to the 'old'
    scan file (-o or --old) in order to generate the 'new' scan file (-n or
    --new).  Write the results to a .csv file (-c or --csv-file) or a
    .json file (-j or --json-file) at a user-designated location.  If no file
    option is selected, print the JSON results to the console.
    """
    # retrieve the option selections
    options = OrderedDict([
        ('--all-delta-types', all_delta_types)
    ])

    # do the delta
    deltacode = DeltaCode(new, old, options)

    # output to csv
    if csv_file:
        write_csv(deltacode, csv_file, all_delta_types)
    # generate JSON output
    else:
        write_json(deltacode, json_file, all_delta_types)
