Development
===========

TL;DR:

- Contributions comes as bugs/questions/issues and as pull requests.
- Source code and runtime data are in the /src/ directory.
- Test code and test data are in the /tests/ directory.
- Datasets (inluding licenses) and test data are in /data/ sub-directories.
- We use DCO signoff in commit messages, like Linux does.

See CONTRIBUTING.rst for details:
https://github.com/aboutcode-org/deltacode/blob/develop/CONTRIBUTING.rst

.. _contrib_code_conven:

Code layout and conventions
---------------------------

Source code is in the ``src/`` directory, tests are in the ``tests/`` directory.
Miscellaneous scripts and configuration files are in the ``etc/`` directory.

There is one Python package for each major feature under ``src/`` and a
corresponding directory with the same name under ``tests`` (but this is not a
package by design as it would not make sense to have a top level "tests" package
which is a name that's too common).

Each test script is named ``test_XXXX``; we prefer organizing tests in subclasses
of the standard library ``unittest`` module. But we also use plain functions
that are discovered nicely by ``pytest``.

When source or tests need data files, we store these in a ``data`` subdirectory.

We use PEP8 conventions with a relaxed line length that can be up to 90'ish
characters long when needed to keep the code clear and readable.

We write tests, a lot of tests, thousands of tests.  When finding bugs or adding
new features, we add tests. See existing test code for examples which form also
a good specification for the supported features.

The tests should pass on Linux 64 bits, Windows 64 bits and on
macOS 10.14 and up. We maintain multiple CI loops with Azure (all OSes)
at https://dev.azure.com/nexB/deltacode/_build and Appveyor (Windows) at
https://ci.appveyor.com/project/nexB/deltacode.


Several tests are data-driven and use data files as test input and sometimes
data files as test expectation (in this case using either JSON or YAML files);
a large number of copyright, license and package manifest parsing tests are such
data-driven tests.

Running tests
-------------

DeltaCode comes with over 29,000 unit tests to ensure detection accuracy and
stability across Linux, Windows and macOS OSes: we kinda love tests, do we?

We use pytest to run the tests: call the ``pytest`` script to run the whole
test suite. This is installed with the ``pytest`` package which is installed
when you run ``./configure --dev``).

If you are running from a fresh git clone and you run ``./configure`` and then
``source venv/bin/activate`` the ``pytest`` command will be available in your path.

Alternatively, if you have already configured but are not in an activated
"virtualenv" the ``pytest`` command is available under
``<root of your checkout>/venv/bin/pytest``

(Note: paths here are for POSIX, but mostly the same applies to Windows)

If you have a multiprocessor machine you might want to run the tests in parallel
(and faster). For instance: ``pytest -n4`` runs the tests on 4 CPUs. We
typically run the tests in verbose mode with ``pytest -vvs -n4``.

See also https://docs.pytest.org for details or use the ``pytest -h`` command
to show the many other options available.

One useful option is to run a select subset of the test functions matching a
pattern with the ``-k`` option, for instance: ``pytest -vvs -k tcpdump`` would
only run test functions that contain the string "tcpdump" in their name or their
class name or module name.

Another useful option after a test run with some failures is to re-run only the
failed tests with the ``--lf`` option, for instance: ``pytest -vvs --lf`` would
only run only test functions that failed in the previous run.


Thirdparty libraries and dependencies management
-----------------------------------------------------

DeltaCode uses the ``configure`` and ``configure.bat`` scripts to install a
`virtualenv <https://virtualenv.pypa.io/en/stable/>`_ , install required
packaged dependencies using  `setuptools <https://github.com/pypa/setuptools>`_
and such that DeltaCode can be installed in a repeatable and consistent manner on
all OSes and Python versions.

For this we maintain a ``setup.cfg`` with our direct dependencies with loose
minimum version constraints; and we keep pinned exact versions of these
dependencies in the ``requirements.txt`` and ``requirements-dev.txt`` (for
testing and development).

And to ensure that we also all use well known version of the core virtualenv,
pip, setuptools and wheel libraries, we use the ``virtualenv.pyz`` Python
zipp app from https://github.com/pypa/get-virtualenv/tree/master/public and
store it in the Git repo in the ``etc/thirdparty`` directory.

DeltaCode app archives should not require network access for installation or
configuration of its third-party libraries and dependencies. To enable this,
we store bundled thirdparty components and  libraries in the ``thirdparty``
directory of released app archives; this is done at build time.
These dependencies are stored as pre-built wheels. These wheels are sometimes
built by us when there is no wheel available upstream on PyPI. We store all
these prebuilt wheels with corresponding .ABOUT and .LICENSE files in
https://github.com/aboutcode-org/thirdparty-packages/tree/main/pypi which is published
for download at  https://thirdparty.aboutcode.org/pypi/

Because this is used by the configure script, all the thirdparty dependencies
used in DeltaCode MUST be available there first. Therefore adding a new
dependency means requesting a merge/PR in
https://github.com/aboutcode-org/thirdparty-packages/ first that contains all the
recursive dependencies.

There are utility scripts in ``etc/release`` that can help with the dependencies
management process in particular to build or update wheels with native code for
multiple OSes (Linux, macOS and Windows) and multiple Python versions (3.7+),
which is not a completely simple operation (and requires eventually 12 wheels
and one source distribution to be published as we support 3 OSes and 4 Python
versions).


Using DeltaCode as a Python library
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

DeltaCode can be used alright as a Python library and is available as as a
Python wheel in Pypi and installed with ``pip install deltacode``
