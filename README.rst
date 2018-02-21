=========
Deltacode
=========

 +--------------+----------------------------------------------------------------------------------------------+
 | **Branch**   | **Linux (Travis)**                                                                           |
 +--------------+----------------------------------------------------------------------------------------------+
 | develop      |.. image:: https://travis-ci.com/nexB/deltacode.svg?token=9MXbiHv3xZxwT2egFxby&branch=develop |
 |              |   :target: https://travis-ci.com/nexB/deltacode                                              |
 +--------------+----------------------------------------------------------------------------------------------+

About:
======

``deltacode`` is a simple command line utility that leverages the power
of `scancode-toolkit <https://github.com/nexB/scancode-toolkit>`_ to determine file-level differences between two
codebases.

How to use:
===========

In order to calculate these differences (i.e. 'deltas'), the user must have two individual
scancode scan files, with the ``--info`` scan option at minimum.

For example::

    $ pip install scancode-toolkit
    $ scancode --info ~/postgresql-9.6/ ~/psql-9.6-fileinfo.json
    $ scancode --info ~/postgresql-10.0/ ~/psql-10.0-fileinfo.json



Once you have the two codebase scans, simply run deltacode on the two scans::

    $ ./deltacode --help
    Usage: deltacode [OPTIONS]

      Identify the changes that need to be made to the 'old' scan file (-o or
      --old) in order to generate the 'new' scan file (-n or --new).  Write the
      results to a .csv file (-c or --csv-file) or a .json file (-j or --json-
      file) at a user-designated location.  If no file option is selected, print
      the JSON results to the console.

    Options:
      -h, --help                Show this message and exit.
      -n, --new PATH            Identify the path to the "new" scan file
                                [required]
      -o, --old PATH            Identify the path to the "old" scan file
                                [required]
      -c, --csv-file PATH       Identify the path to the .csv output file
      -j, --json-file FILENAME  Identify the path to the .json output file
      -a, --all-delta-types     Include unmodified files as well as all changed
                                files in the .json or .csv output.  If not
                                selected, only changed files are included.
    
    $ ./deltacode -n ~/psql-10.0-fileinfo.json -o ~/psql-9.6-fileinfo.json -j ~/psql-10.0-psql-9.6-delta.json

=========
Problems?
=========

Open an `issue <https://www.github.com/nexb/deltacode/issues>`_.

Notes:
======

- ``deltacode`` also collects statistical information, like # of files and other percentages. Currently, this output is not present in the ``csv`` output

Future TODOs/additions:
=======================

- Use ``copyright`` information from scans to identify changes in copyright holders or dates for attribution.
- Detect package or file changes that are only a version change for the same package or file.
- Determine whether some added/removed files or packages are actually cases where the files or packages were moved.

