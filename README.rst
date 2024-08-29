Deltacode
=========
DeltaCode is a simple command line utility that leverages the power
of `scancode-toolkit <https://github.com/aboutcode-org/scancode-toolkit>`_
to determine file-level differences between two codebases.

During a typical software release cycle, development teams and software
compliance experts want insight into how a codebase has changed during each
release iteration. Specifically, these users need a utility that can point out
places in a codebase where material license and other provenance changes have
occurred. This is where DeltaCode comes in.

DeltaCode provides an accurate means of comparing two ScanCode result files,
and returning any possible changes that have occurred between the two given
scanned codebases. DeltaCode currently has the ability to detect file size and
license changes, as well as means to detect when files have been moved to new
locations.

We are continuously working on new features, such as detecting copyright changes
and detecting package version changes.

Build and tests status
======================

We run tests on each commit on multiple CIs to ensure a good platform
compatibility with multiple versions of Windows, Linux and macOS.

+--------------+--------------+
| **Azure**    | **RTD Build**|
+==============+==============+
|    |azure|   | |docs-rtd|   |
+--------------+--------------+

Documentation
=============

The DeltaCode documentation is hosted at
`deltacode.readthedocs.io <https://deltacode.readthedocs.io/en/latest/>`_.

Installation
============

Before installing DeltaCode make sure that you have installed the prerequisites
properly. This means installing Python 3.8 for x86/64 architectures.
We support Python 3.8, 3.9 and 3.10.

See `prerequisites <https://deltacode.readthedocs.io/en/latest/comprehensive_installation.html#prerequisites>`_
for detailed information on the support platforms and Python versions.

There are a few common ways to `install DeltaCode <https://deltacode.readthedocs.io/en/latest/comprehensive_installation.html>`_.

- `Development installation from source code using a git clone
  <https://deltacode.readthedocs.io/en/latest/comprehensive_installation.html#source-code-install>`_

- `Development installation as a library with "pip install deltacode"
  <https://deltacode.readthedocs.io/en/latest/comprehensive_installation.html#pip-install>`_

- `Run in a Docker container with a git clone and "docker run"
  <https://deltacode.readthedocs.io/en/latest/comprehensive_installation.html#docker-install>`_


Quick Start
===========

Run this command to display the command
help::

    deltacode --help

Run a sample delta::

    deltacode -n samples/samples.json -o samples/samples.json

Run a simple delta saved to the `output.json` file::

    deltacode -n samples/samples.json -o samples/samples.json -j output.json

Then open `output.json` to view the delta results.

To get DeltaCode results for your codebase, install
`scancode-toolkit <https://github.com/aboutcode-org/scancode-toolkit>`_ and generate a
scan for each of the codebases you wish to 'Delta'


Support
=======

If you have a problem, a suggestion or found a bug, please enter a ticket at:
https://github.com/aboutcode-org/deltacode/issues

For discussions and chats, we have:

* an official Gitter channel for `web-based chats
  <https://gitter.im/aboutcode-org/discuss>`_.
  Gitter is also accessible via an `IRC bridge <https://irc.gitter.im/>`_.
  There are other AboutCode project-specific channels available there too.

* an official `#aboutcode` IRC channel on liberachat (server web.libera.chat).
  This channel receives build and commit notifications and can be noisy.
  You can use your favorite IRC client or use the `web chat
  <https://web.libera.chat/?#aboutcode>`_.



Source code
===========

* https://github.com/aboutcode-org/deltacode/releases
* https://github.com/aboutcode-org/deltacode.git
* https://pypi.org/project/deltacode/


License
=======

* Apache-2.0 with an acknowledgement required to accompany the delta output.

See the NOTICE file and the .ABOUT files that document the origin and license of
the third-party code used in DeltaCode for more details.

.. |azure| image:: https://dev.azure.com/nexB/deltacode/_apis/build/status/nexB.deltacode?branchName=develop
    :target: https://dev.azure.com/nexB/deltacode/_build/latest?definitionId=1&branchName=develop
    :alt: Azure tests status (Linux, macOS, Windows)

.. |docs-rtd| image:: https://readthedocs.org/projects/deltacode/badge/?version=latest
    :target: https://deltacode.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
