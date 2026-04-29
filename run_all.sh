#!/usr/bin/env bash
# Plug-and-play runner: iterates test_*.py, runs each with python3,
# captures exit code, prints "PASSED: N  FAILED: M" plus failing names,
# and exits non-zero if any test failed (CI-friendly).
#
# Assumes `roslaunch meam520_labs project.launch` is already running in
# another terminal — individual tests give a clear error if not.

set -u
cd "$(dirname "$0")"

# TODO: iterate ./test_*.py, run with python3, collect pass/fail, print summary.
# TODO: exit 0 if all passed, 1 otherwise.