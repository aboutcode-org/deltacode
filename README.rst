Deltacode
=========

 +--------------+----------------------------------------------------------------------------------------------+
 | **Branch**   | **Linux (Travis)**                                                                           |
 +--------------+----------------------------------------------------------------------------------------------+
 | develop      |.. image:: https://travis-ci.com/nexB/deltacode.svg?token=9MXbiHv3xZxwT2egFxby&branch=develop |
 |              |   :target: https://travis-ci.com/nexB/deltacode                                              |
 +--------------+----------------------------------------------------------------------------------------------+


DeltaCode is a simple command line utility that leverages the power
of `scancode-toolkit <https://github.com/nexB/scancode-toolkit>`_
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


Quick Start
===========
For more comprehensive installation instructions and development instructions, see:
`Comprehensive Installation <https://github.com/nexB/deltacode/wiki/Comprehensive-Installation>`_

For development instructions, see:
`Development Instructions <https://github.com/nexB/deltacode/wiki/Development>`_

Make sure you have Python 3.6+ installed:
  * Download and install Python 3.6+ Windows
    https://www.python.org/downloads/windows/
  * Download and install Python 3.6+ for Mac
    https://www.python.org/downloads/mac-osx/
  * Download and install Python 3.6+ for Linux via distro package manager

Next, download and extract the latest DeltaCode release from::

    https://github.com/nexB/deltacode/releases/

Open a terminal, extract the downloaded release archive, then `cd` to
the extracted directory and run this command to display the command
help. DeltaCode will self-configure if needed::

    ./deltacode --help

Run a sample delta

    ./deltacode -n samples/samples.json -o samples/samples.json

Run a simple delta saved to the `output.json` file::

    ./deltacode -n samples/samples.json -o samples/samples.json -j output.json

Then open `output.json` to view the delta results.

To get DeltaCode results for your codebase, install
`scancode-toolkit <https://github.com/nexB/scancode-toolkit>`_ and generate a
scan for each of the codebases you wish to 'Delta'


Support
=======

If you have a problem, a suggestion or found a bug, please enter a ticket at:
https://github.com/nexB/deltacode/issues

For other questions, discussions, and chats, we have:

- an official Gitter channel at https://gitter.im/aboutcode-org/discuss
  Gitter also has an IRC bridge at https://irc.gitter.im/

- an official #aboutcode IRC channel on freenode (server chat.freenode.net)
  for DeltaCode and other related tools. Note that this receives
  notifications from repos so it can be a tad noisy. You can use your
  favorite IRC client or use the web chat at
  https://webchat.freenode.net/


Source code
===========

* https://github.com/nexB/deltacode.git


License
=======

* Apache-2.0 with an acknowledgement required to accompany the delta output.

See the NOTICE file for more details.


Documentation & FAQ
===================

https://github.com/nexB/deltacode/wiki
