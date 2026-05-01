#!/usr/bin/env bash
# Plug-and-play runner: iterates test_*.py, runs each with python3, captures
# exit code, prints a summary.
#
# Exit code convention:
#   0 = PASS, 1 = FAIL (component broken), 2 = SKIP (component not deployed)
#
# Skipped tests don't count as failure — Team 8's sim is shipped progressively,
# so it's normal for some components to not be deployed yet. test_deployment.py
# shows the full picture of what's present.
#
# Assumes `roslaunch meam520_labs project.launch` is already running in
# another terminal — individual tests give a clear error if not.

set -u
cd "$(dirname "$0")"

passed=()
failed=()
skipped=()

for f in test_*.py; do
    echo "===== $f ====="
    python3 "$f"
    rc=$?
    case $rc in
        0) passed+=("$f") ;;
        2) skipped+=("$f") ;;
        *) failed+=("$f") ;;
    esac
    echo
done

echo "===== Summary ====="
echo "PASSED:  ${#passed[@]}"
echo "FAILED:  ${#failed[@]}"
echo "SKIPPED: ${#skipped[@]}"
if [ "${#failed[@]}" -gt 0 ]; then
    echo "Failures:"
    for f in "${failed[@]}"; do
        echo "  - $f"
    done
fi
if [ "${#skipped[@]}" -gt 0 ]; then
    echo "Skipped (component not deployed yet):"
    for f in "${skipped[@]}"; do
        echo "  - $f"
    done
fi
[ "${#failed[@]}" -eq 0 ] && exit 0 || exit 1