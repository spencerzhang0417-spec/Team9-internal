"""Entry point invoked by Team 6's orchestrator.

The integration repo's contract: every team's `main.py` accepts `--team` and
optional `--robot`, and `main(team, robot)` does that team's job. For Team 9
(sim QC) the job is "run the test suite against the currently-running sim",
so this file shells out to run_all.sh.

`--robot` is accepted to satisfy the orchestrator's interface but ignored:
Team 9's tests cover both arms, both turntables, and all dispensers — the
suite is not robot-scoped.

Stand-alone usage is unchanged: `./run_all.sh` does the same thing.
"""

import argparse
import os
import subprocess
import sys


def main(team, robot=None):
    suffix = f" --robot {robot}" if robot is not None else ""
    print(f"Team 9 (sim QC) launched via orchestrator with --team {team}{suffix}")
    here = os.path.dirname(os.path.abspath(__file__))
    rc = subprocess.call([os.path.join(here, "run_all.sh")], cwd=here)
    sys.exit(rc)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--team", type=int, required=True)
    parser.add_argument("--robot", type=int)
    args = parser.parse_args()
    main(args.team, args.robot)
