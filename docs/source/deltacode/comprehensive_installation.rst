Comprehensive Installation
==========================


There are multiple ways to install DeltaCode.

- :ref:`docker_install`

    An alternative to installing the latest DeltaCode release natively is
    to build a Docker image from the included Dockerfile. The only prerequisite
    is a working Docker installation.

- :ref:`source_code_install`

    You can clone the git source code repository and then run the configure script
    to configure and install DeltaCode for local and development usage.

- :ref:`pip_install`

    To use DeltaCode as a library in your application, you can install it via
    ``pip``. This is recommended for developers or users familiar with Python
    that want to embed DeltaCode as a library.

----

Before Installing
-----------------

- DeltaCode requires a Python version 3.8, 3.9 or 3.10 and is
  tested on Linux, macOS, and Windows. It should work fine on FreeBSD.

System Requirements
-------------------

- Hardware : DeltaCode will run best with a modern X86 64 bits processor and at
  least 8GB of RAM and 2GB of disk space. These are minimum requirements.

- Supported operating systems: DeltaCode should run on these 64-bit OSes running
  X86_64 processors:

    #. Linux: on recent 64-bit Linux distributions,
    #. Mac: on recent x86 64-bit macOS (10.15 and up, including 11 and 12),
       Use the X86 emulation mode on Apple ARM M1 CPUs.
    #. Windows: on Windows 10 and up,
    #. FreeBSD.


.. _install_prerequisites:

Prerequisites
-------------

DeltaCode needs a Python 3.8 (or above) interpreter.

- **On Linux**:

    Use your package manager to install atleast ``python3.8``. If Python 3.8 is not available
    from your package manager, you must compile it from sources.

    For instance, visit https://github.com/dejacode/about-code-tool/wiki/BuildingPython27OnCentos6
    for instructions to compile Python from sources on Centos.

- **On Windows**:

    Download Python from this url:
    https://www.python.org/

    Install Python on the c: drive and use all default installer options.
    See the Windows installation section for more installation details.

- **On Mac**:

    The default Python 3 provided with macOS is 3.8.
    Alternatively you can download and install Python 3.8+ from https://www.python.org/


Installation on Linux and Mac
-----------------------------

Download and extract the latest DeltaCode release from:
https://github.com/aboutcode-org/deltacode/releases/latest

Check whether the :ref:`install_prerequisites` are installed. Open a terminal
in the extracted directory and run::

    ./deltacode --help

This will configure DeltaCode and display the command line help.

Installation on Windows
-----------------------

Download the latest DeltaCode release zip file from:
https://github.com/aboutcode-org/deltacode/releases/latest

- In the File Explorer, select the downloaded DeltaCode zip and right-click.

- In the pop-up menu select 'Extract All...'

- In the pop-up window 'Extract Compressed (Zipped) Folders' use the default options to extract.

- Once the extraction is complete, a new File Explorer window will pop up.

- In this Explorer window, select the new folder that was created and right-click.

.. note::

  On Windows 10, double-click the new folder, select one of the files inside the folder
  (e.g., 'setup.py'), and right-click.

- In the pop-up menu select 'Properties'.

- In the pop-up window 'Properties', select the Location value. Copy this to the clipboard and
  close the 'Properties' window.

- Press the start menu button, click the search box or search icon in the taskbar.

- In the search box type::

    cmd

- Select 'cmd.exe' or 'Command Prompt' listed in the search results.

- A new 'Command Prompt'pops up.

- In this window (aka a 'command prompt'), type 'cd' followed by a space and
  then Right-click in this window and select Paste. This will paste the path you
  copied before and is where you extracted DeltaCode::

    cd path/to/extracted/deltacode

- Press Enter.

- This will change the current location of your command prompt to the root directory where
  DeltaCode is installed.

- Then type::

    deltacode -h

- Press enter. This first command will configure your DeltaCode installation.
  Several messages are displayed followed by the DeltaCode command help.

- The installation is complete.

Un-installation
---------------

- Delete the directory in which you extracted DeltaCode.
- Delete any temporary files created in your system temp directory under a DeltaCode directory.

.. _docker_install:

Using the docker image for testing DeltaCode
--------------------------------------------

- In the project root directory run `docker-compose up`.
- This will create an image of DeltaCode with the name `delta_code`.
- To verify the image created run `docker image ls`.
- To run the image run `docker run -itd --name <specific name of container>  delta_code`.
- The above command runs the image in the background and creates a container with the name
  as per specified.
- To execute the container in a bash mode run `docker exec -it <container name> bash`.
- The above command will open a bash shell in the container.
- To run the commands / pytest inside the shell you can use the commands as specified
  in the documentations.

.. _source_code_install:

Installation from Source Code: Git Clone
-----------------------------------------

You can download the DeltaCode Source Code and build from it yourself.
This is what you would want to do it if:

- You are developing DeltaCode or adding new patches or want to run tests.
- You want to test or run a specific version/checkpoint/branch from the version control.


Download the DeltaCode Source Code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run the following once you have `Git <https://git-scm.com/>`_ installed::

    git clone https://github.com/aboutcode-org/deltacode.git
    cd deltacode


Configure the build
^^^^^^^^^^^^^^^^^^^

DeltaCode use a configure scripts to create an isolated virtual environment,
install required packaged dependencies.

On Linux/Mac:

- Open a terminal
- cd to the clone directory
- run ``./configure``
- run ``source venv/bin/activate``


On Windows:

- open a command prompt
- cd to the clone directory
- run ``configure``
- run ``venv\Scripts\activate``


Now you are ready to use the freshly configured DeltaCode.

.. NOTE::

    For use in development, run instead ``configure --dev``. If your face
    issues while configuring a previous version, ``configure --clean`` to
    clean and reset your environment. You will need to run ``configure`` again.


----

.. _pip_install:

Installation as a library: via ``pip``
--------------------------------------

DeltaCode can be installed from the public PyPI repository using ``pip`` which
the standard Python package management tool.

The steps are:

#. Create a Python virtual environment::

    /usr/bin/python3 -m venv venv

For more information on Python virtualenv, visit this
`page <https://docs.python-guide.org/dev/virtualenvs/#lower-level-virtualenv>`_.

#. Activate the virtual environment you just created::

    source venv/bin/activate

#. Run pip to install the latest versions of base utilities::

    pip install --upgrade pip setuptools wheel

#. Install the latest version of DeltaCode::

    pip install deltacode

To uninstall, run::

    pip uninstall deltacode

