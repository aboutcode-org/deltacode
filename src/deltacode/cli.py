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
import json

import click

from deltacode import DeltaCode
from deltacode import __version__


def generate_csv(delta, result_file):
    """
    Using the DeltaCode object, create a .csv file
    containing the primary information from the Delta objects.
    """
    with open(result_file, 'wb') as out:
        csv_out = csv.writer(out)
        csv_out.writerow(['Type of delta', 'Path'])
        for row in [(f.category, f.old_file.path if f.category == 'removed' else f.new_file.path) for d in delta.deltas for f in delta.deltas.get(d)]:
            csv_out.writerow(row)


def generate_json(delta, result_file):
    """
    Using the DeltaCode object, create a .json file
    containing the primary information from the Delta objects.
    """
    output = OrderedDict([
        ('deltacode_version', __version__),
        ('deltacode_stats', delta.get_stats()),
        ('deltas', delta.to_dict())
    ])

    with open(result_file, 'w') as outfile:
        json.dump(output, outfile, indent=4)


@click.command()
@click.help_option('-h', '--help')
@click.option('-n', '--new', required=True, prompt=False, type=click.Path(exists=True, readable=True), help='Identify the path to the "new" scan file')
@click.option('-o', '--old', required=True, prompt=False, type=click.Path(exists=True, readable=True), help='Identify the path to the "old" scan file')
@click.option('-c', '--csv-file', prompt=False, type=click.Path(exists=False), help='Identify the path to the .csv output file')
@click.option('-j', '--json-file', prompt=False, type=click.Path(exists=False), help='Identify the path to the .json output file')
def cli(new, old, csv_file, json_file):
    """
    This script identifies the changes that need to be made to the 'old'
    scan file (-o or -old) in order to generate the 'new' scan file (-n or
    -new).  The results are written to a .csv file (-c or -csv-file) or a
    .json file (-j or -json-file) at a user-designated location.  If no file
    option is selected, the JSON results are printed to the console.
    """
    # do the delta
    delta = DeltaCode(new, old)

    # output to csv
    if csv_file:
        generate_csv(delta, csv_file)
    # generate JSON output
    elif json_file:
        generate_json(delta, json_file)
    # print to stdout
    else:
        print(json.dumps(delta.to_dict()))
