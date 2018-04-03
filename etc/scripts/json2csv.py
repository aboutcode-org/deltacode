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

from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import codecs
from collections import OrderedDict
import json
import os

import click
click.disable_unicode_literals_warning = True

import unicodecsv

"""
Convert a DeltaCode JSON file to a CSV.
Ensure you are in the DeltaCode virtualenv and run 'python etc/scripts/json2csv.py -h'.
"""


def load_deltas(json_input):
    """
    Return a list of DeltaCode results loaded from a json_input, in
    DeltaCode standard JSON format.
    """
    with codecs.open(json_input, 'rb', encoding='utf-8') as jsonf:
        delta = jsonf.read()

    delta_results = json.loads(delta, object_pairs_hook=OrderedDict)

    delta_results = delta_results['deltas']

    return delta_results


def json_delta_to_csv(json_input, csv_output):
    """
    Convert a DeltaCode JSON output file to a CSV.
    """
    delta_results = load_deltas(json_input)

    headers = OrderedDict([
        ('Score', []),
        ('Factors', []),
        ('Path', []),
        ('Name', []),
        ('Type', []),
        ('Size', []),
        ('Old Path', []),
    ])

    rows = list(flatten_deltas(delta_results, headers))

    w = unicodecsv.DictWriter(csv_output, headers)
    w.writeheader()

    for r in rows:
        w.writerow(r)


def flatten_deltas(deltas, headers):
    if len(deltas) < 1:
        yield OrderedDict([
            ('Score', ''),
            ('Factors', ''),
            ('Path', ''),
            ('Name', ''),
            ('Type', ''),
            ('Size', ''),
            ('Old Path', ''),
        ])

    for d in deltas:
        delta_score = d.get('score')
        delta_factors = d.get('factors')
        delta_path = d.get('old').get('path') if 'removed' in delta_factors else d.get('new').get('path')
        delta_name = d.get('old').get('name') if 'removed' in delta_factors else d.get('new').get('name')
        delta_type = d.get('old').get('type') if 'removed' in delta_factors else d.get('new').get('type')
        delta_size = d.get('old').get('size') if 'removed' in delta_factors else d.get('new').get('size')
        delta_old_path = d.get('old').get('path') if 'moved' in delta_factors else ''

        yield OrderedDict([
            ('Score', delta_score),
            ('Factors', ' '.join(delta_factors)),
            ('Path', delta_path),
            ('Name', delta_name),
            ('Type', delta_type),
            ('Size', delta_size),
            ('Old Path', delta_old_path),
        ])


@click.command()
@click.argument('json_input', type=click.Path(exists=True, readable=True))
@click.argument('csv_output', type=click.File('wb', lazy=False))
@click.help_option('-h', '--help')
def cli(json_input, csv_output):
    """
    Convert a DeltaCode JSON file to a CSV file. For example:

    python etc/scripts/json2csv.py  /c/input.json /c/output.csv
    """
    json_input = os.path.abspath(os.path.expanduser(json_input))
    json_delta_to_csv(json_input, csv_output)


if __name__ == '__main__':
    cli()
