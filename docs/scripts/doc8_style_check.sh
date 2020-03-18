#!/bin/bash
# halt script on error
set -e
# Check for Style Code Violations
# (Here D000 is ignored to bypass the include statement errors as the files we are including are
# not in the same source folder as the include statement.)
doc8 --max-line-length 100 source --ignore D000 --quiet