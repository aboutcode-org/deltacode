@echo OFF
@rem Copyright (c) 2018 nexB Inc. http://www.nexb.com/ - All rights reserved.

@rem  A minimal shell wrapper to the CLI entry point

set DELTACODE_ROOT_DIR=%~dp0
@rem Use a trailing space in the next line to set the variable to an empty string
set DELTACODE_CMD_LINE_ARGS= 
set DELTACODE_CONFIGURED_PYTHON=%DELTACODE_ROOT_DIR%\bin\python.exe

@rem Collect all command line arguments in a variable
:collectarg
if ""%1""=="""" goto continue
call set DELTACODE_CMD_LINE_ARGS=%DELTACODE_CMD_LINE_ARGS% %1
shift
goto collectarg

:continue

if not exist "%DELTACODE_CONFIGURED_PYTHON%" goto configure
goto deltacode

:configure
echo * Configuring DeltaCode for first use...
set CONFIGURE_QUIET=1
call "%DELTACODE_ROOT_DIR%\configure" etc/conf
if %errorlevel% neq 0 (
   exit /b %errorlevel%
)

:deltacode
"%DELTACODE_ROOT_DIR%\bin\deltacode" %DELTACODE_CMD_LINE_ARGS%

:EOS
