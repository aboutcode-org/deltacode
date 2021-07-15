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
import simplejson

from deltacode import DeltaCode
from deltacode import __version__
from deltacode.utils import deltas, get_notice, collect_errors


def write_json(deltacode, outfile, all_delta_types=False):
    """
    Using the DeltaCode object, create a .json file containing the primary
    information from the Delta objects.  Through a call to utils.deltas(), omit
    all unmodified Delta objects -- identified by a 'score' of 0 -- unless the
    user selects the '-a'/'--all-delta-types' option.
    """
    results = OrderedDict([
        ('deltacode_notice', get_notice()),
        # ('new_scan_options', deltacode.new_scan_options),
        # ('old_scan_options', deltacode.old_scan_options),
        ('deltacode_options', deltacode.options),
        ('deltacode_version', __version__),
        ('deltacode_errors', collect_errors(deltacode)),
        ('deltas_count', len([d for d in deltas(deltacode, all_delta_types)])),
        ('delta_stats', deltacode.stats.to_dict()),
        ('deltas', deltas(deltacode, all_delta_types))
    ])

    # TODO: add toggle for pretty printing
    simplejson.dump(results, outfile, iterable_as_array=True, indent=2)
    outfile.write('\n')


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('DeltaCode version ' + __version__)
    ctx.exit()


@click.command()
@click.help_option('-h', '--help')
@click.option('--version', is_flag=True, is_eager=True, expose_value=False, callback=print_version, help='Show the version and exit.')
@click.option('-n', '--new', required=True, prompt=False, type=click.Path(exists=True, readable=True), help='Identify the path to the "new" scan file')
@click.option('-o', '--old', required=True, prompt=False, type=click.Path(exists=True, readable=True), help='Identify the path to the "old" scan file')
@click.option('-j', '--json-file', prompt=False, default='-', type=click.File(mode='w', lazy=False), help='Identify the path to the .json output file')
@click.option('-a', '--all-delta-types', is_flag=True, help="Include unmodified files as well as all changed files in the .json output.  If not selected, only changed files are included.")
def cli(new, old, json_file, all_delta_types):
    """
    Identify the changes that need to be made to the 'old'
    scan file (-o or --old) in order to generate the 'new' scan file (-n or
    --new).  Write the results to a .json file (-j or --json-file) at a
    user-designated location.  If no file option is selected, print the JSON
    results to the console.
    """
    # retrieve the option selections
    options = OrderedDict([
        ('--new', new),
        ('--old', old),
        ('--all-delta-types', all_delta_types)
    ])

    # do the delta
    deltacode = DeltaCode(new, old, options)
    # generate JSON output
    write_json(deltacode, json_file, all_delta_types)
