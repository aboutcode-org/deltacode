============
Contributing
============

Contributions are welcome and appreciated!
Every little bit helps, and credit will always be given.

.. _issue : https://github.com/nexB/deltacode/issue
__ issue_

If you are new to DeltaCode and want to find easy tickets to work on,
check `easy issues <https://github.com/nexB/deltacode/labels/easy>`_

When contributing to DeltaCode (such as code, bugs, documentation, etc.) you
agree to the Developer `Certificate of Origin <http://developercertificate.org/>`_
and the DeltaCode license (see the `NOTICE <https://github.com/nexB/deltacode/blob/develop/NOTICE>`_ file).
The same approach is used by the Linux Kernel developers and several other projects.

For commits, it is best to simply add a line like this to your commit message,
with your name and email::

    Signed-off-by: Jane Doe <developer@example.com>

Please try to write a good commit message, see `good commit message wiki
<https://github.com/nexB/aboutcode/wiki/Writing-good-commit-messages>`_ for
details. In particular use the imperative for your commit subject: think that
you are giving an order to the codebase to update itself.


Feature requests and feedback
=============================

To send feedback or ask a question, `file an issue <issues_>`_

If you are proposing a feature:

* Explain how it would work.
* Keep the scope simple possible to make it easier to implement.
* Remember that your contributions are welcomed to implement this feature!


Chat with other developers
==========================

For other questions, discussions, and chats, we have:

- an official Gitter channel at https://gitter.im/aboutcode-org/discuss
  Gitter also has an IRC bridge at https://irc.gitter.im/
  This is the main place where we chat and meet.

- an official #aboutcode IRC channel on freenode (server chat.freenode.net)
  for DeltaCode and other related tools. You can use your
  favorite IRC client or use the web chat at https://webchat.freenode.net/ .
  This is a busy place with a lot of CI and commit notifications that makes
  actual chat sometimes difficult!

- a mailing list at `sourceforge <https://lists.sourceforge.net/lists/listinfo/aboutcode-discuss>`_


Bug reports
===========

When `reporting a bug`__ please include:

* Your operating system name, version and architecture (32 or 64 bits).
* Your Python version.
* Your DeltaCode version.
* Any additional details about your local setup that might be helpful to
  diagnose this bug.
* Detailed steps to reproduce the bug, such as the commands you ran and a link
  to the code you are scanning.
* The errors messages or failure trace if any.
* If helpful, you can add a screenshot as an issue attachment when relevant or
  some extra file as a link to a `Gist <https://gist.github.com>`_.


Documentation improvements
==========================

Documentation can come in the form of wiki pages, docstrings, blog posts,
articles, etc. Even a minor typo fix is welcomed.
See also extra documentation on the `Wiki <https://github.com/nexB/deltacode/wiki>`_.


Development
===========

To set up DeltaCode for local development:

1. Fork the deltacode on GitHub, click `fork <https://github.com/nexb/deltacode/fork>`_ button

2. Clone your fork locally:

   Use SSH::

    git clone git@github.com:your_name_here/deltacode.git

   Or use HTTPS::

    git clone https://github.com/your_name_here/deltacode.git

   See also GitHub docs dor `SSH <https://help.github.com/articles/connecting-to-github-with-ssh/>`_
   or `HTTPS <https://help.github.com/articles/which-remote-url-should-i-use/#cloning-with-https-urls-recommended>`_

   If you want to change the connection type, do following

    SSH to HTTPS ::

      git remote set-url <repository-alias-name> https://github.com/your_name_here/deltacode.git

    HTTPS to SSH ::

      git remote set-url <repository-alias-name> git@github.com:your_name_here/deltacode.git

   Generally <repository-alias-name> is named origin, but in the case of multiple fetch/pull source of repository you can choose whatever name you want

3. Create a branch for local development::

    git checkout -b name-of-your-bugfix-or-feature

4. To configure your local environment for development, locate to the main
   directory of the local repository, run the configure script.
   The configure script creates an isolated Python `virtual environment` in
   your checkout directory, the Python `pip` tool, and installs the thirdparty
   libraries (from the `thirdparty/ directory`), setup the paths, etc.
   See https://virtualenv.pypa.io/en/latest/ for more details.

   Run this command to configure DeltaCode::

        ./configure

   On Windows use instead::

        configure

   Then run this: `source bin/activate` or `. bin/activate`
   (or run `bin\\activate` on Windows)

   When you create a new terminal/shell to work on DeltaCode rerun the activate step.

   When you pull new code from git, rerun ./configure


5. Now you can make your code changes in your local clone.
   Please create new unit tests for your code. We love tests!

6. When you are done with your changes, run all the tests.
   Use this command::

        py.test

   Or use the -n6 option to run on 6 threads in parallel and run tests faster::

       py.test -n6

7. Check the status of your local repository before commit, regarding files changed::

    git status


8. Commit your changes and push your branch to your GitHub fork::

    git add <file-changed-1> <file-changed-2> <file-changed-3>
    git commit -m "Your detailed description of your changes." --signoff
    git push <repository-alias-name> name-of-your-bugfix-or-feature

9. Submit a pull request through the GitHub website for this branch.


Pull Request Guidelines
-----------------------

If you need a code review or feedback while you are developing the code just
create a pull request. You can add new commits to your branch as needed.

For merging, your request would need to:

1. Include unit tests that are passing (run ``py.test``).
2. Update documentation as needed for new API, functionality etc.
3. Add a note to ``CHANGELOG.rst`` about the changes.
4. Add your name to ``AUTHORS.rst``.


Test tips
---------

To run a subset of test functions containing test_myfeature in their name use::

    py.test -k test_myfeature

To run the tests from a single test file::

    py.test  tests/commoncode/test_fileutils.py

To run tests in parallel on eight processors::

    py.test  -n 8

To run tests verbosely, displaying all print statements to terminal::

    py.test  -vvs
