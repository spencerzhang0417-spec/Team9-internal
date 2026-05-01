# Team 9 — Deployment Guide for Other Teams

This guide is for teams who want to run Team 9's QC suite against their own work or integrate our entry point into their tooling.

## What Team 9 Provides

Team 9 is the Simulation QC team. We ship two things you can use:

1. **A test suite (`test_*.py`)** that probes Team 8's Gazebo sim and reports which components are working. Run it before integrating against the sim — it tells you whether a failure you're seeing is in your code or in the substrate.
2. **Mock robots (`service_mock.py`, `toppings_mock.py`)** that subscribe to Team 2's `task_cmd` topic and publish well-formed `RobotStatus` replies. Useful for Teams 1, 2, 5, 6 to integration-test the comms / scheduler / frontend stack without waiting on real robot controllers (Teams 11–19).

Team 9's code is **not part of the demo-day runtime**. It is a development and CI tool.

## Prerequisites

| Requirement | Version / source |
| --- | --- |
| OS | Ubuntu 20.04 |
| ROS | Noetic |
| Python | 3.8 |
| Catkin workspace | `~/meam520_ws` (or equivalent) |
| Team 2 package | `trail_mix` built via `catkin_make_isolated --pkg trail_mix` |
| Team 8 package | `meam520_labs` (Gazebo world) — only required to run sim-touching tests |

If `trail_mix` is not on your `PYTHONPATH`, the mock-robot tests and `test_e2e_happy_path.py` will fail to import. The Phase 1 sim tests do not require `trail_mix`.

## Install

Clone this repo into your workspace's `src/` alongside the other team repos:

```bash
cd ~/meam520_ws/src
git clone <team-09 repo url> team-09-main
```

No build step is required — all entry points are plain Python scripts.

Source the workspace overlay so `trail_mix` and `meam520_labs` are visible:

```bash
source /opt/ros/noetic/setup.bash
source ~/meam520_ws/devel_isolated/setup.bash
```

## Run

### Option A — Full suite

From the `team-09-main/` directory, with `roslaunch meam520_labs project.launch` already running in another terminal:

```bash
./run_all.sh
```

Output: each test's stdout, followed by a summary block:

```
===== Summary =====
PASSED:  N
FAILED:  M
SKIPPED: K
```

Process exit code: `0` if no FAIL, `1` if any FAIL. Skipped tests do not count as failures.

### Option B — A single test

Each `test_*.py` is self-contained:

```bash
python3 test_dispenser_lever.py
```

Same exit code convention applies.

### Option C — Programmatic entry point

`main.py` accepts `--team <id>` and optional `--robot <id>` and shells out to `run_all.sh`. Use it if you are launching Team 9 from a process orchestrator that follows the `python3 main.py --team N` convention. `--robot` is accepted but ignored (the suite is not robot-scoped).

```bash
python3 main.py --team 9
```

Exit code propagates from `run_all.sh`.

## Exit Code Convention

All `test_*.py` scripts use the same exit codes. If you wrap the suite in CI, treat them as follows:

| Code | Meaning | What to do |
| --- | --- | --- |
| `0` | **PASS** — component works as intended. | Nothing. |
| `1` | **FAIL** — component is deployed but broken. | File the issue with the responsible team (named in the failure message). |
| `2` | **SKIP** — required component is not deployed in this sim yet. | Not a regression. Re-run after the dependency ships. |

`run_all.sh` buckets and reports each category separately so partial deployments are not misread as broken software.

`test_deployment.py` is a Phase 0 diagnostic and **always exits `0`**. It is not a pass/fail check — it just lists which expected models and controllers are present in the running sim, so you can predict which other tests will SKIP vs RUN before invoking them.

## Test Reference

| Test | Question it answers | Owner team if it FAILs |
| --- | --- | --- |
| `test_deployment.py` | Which expected models and controllers are present? (diagnostic only) | — |
| `test_cup_stack.py` | Does a stacked cup stay where it was spawned? | Team 8 |
| `test_dispenser_lever.py` | Does the dispenser lever move under effort and return when released? | Team 8 |
| `test_turntable.py` | Does the turntable joint rotate under effort, and does a cup ride along? | Team 8 |
| `test_gripper_grasp.py` | Does the gripper action server respond to open/close commands? (API smoke test, not contact physics) | Team 8 / labs infra |
| `test_arms_move.py` | Do `ArmController(id=1)` and `ArmController(id=2)` drive their arms to commanded poses? | Team 8 / labs infra |
| `test_e2e_happy_path.py` | With both Team 9 mocks running, does an 8-command happy-path order flow through Team 2's comms layer and report `done`? | Team 2 (comms), Team 9 (mocks) |

Each test prints `PASS <name> (...)` or `FAIL <name> (<reason>)` on a single line so the failure point is immediately visible in CI logs.

## Mock Robots — Standalone Use

If you are building scheduler, comms, or frontend code (Teams 1, 2, 5, 6) and want to drive an integration test without real robot controllers, run the mocks directly:

```bash
# Terminal 1
roscore

# Terminal 2
python3 service_mock.py

# Terminal 3
python3 toppings_mock.py
```

Each mock subscribes to `task_cmd` via `TrailMixInterface`. For commands routed to its robot group, it sleeps a plausible duration and publishes `robot_status="done"` back. Message construction goes through `helpers.build_robot_status` / `helpers.build_robot_command`, which set `order_id` and `timestamp` correctly so they pass Team 2's interface validators.

The mocks do not implement failure injection or timing variation. If your integration test needs that, contact Team 9 first — we will add it on request rather than ship speculative configuration surface.

## Reporting Issues

| Issue type | Where to file |
| --- | --- |
| A test produced a wrong PASS or wrong FAIL | Team 9 |
| A test's failure message points at Team X — the bug is in Team X's component | Team X (the message names them) |
| A mock robot published a malformed message or missed a command | Team 9 |
| You need a new test or mock behavior | Team 9 |

When filing with Team 9, include the failing test name, the full single-line PASS/FAIL output, and the output of `test_deployment.py` so we can see what was deployed at the time.

## Compatibility Notes

- **Single assembly line today.** Team 8's sim currently spawns one assembly line (`franka1`, `franka2`, one turntable, six dispensers). `test_deployment.py` will report line-2 components as `NOT DEPLOYED`; that is expected and not a failure.
- **Gripper portability.** Tests drive the gripper via `arm._gripper.move_joints(width)`, which publishes correctly on both sim and real hardware. `arm.exec_gripper_cmd(width, force)` and `arm._gripper.grasp(...)` work in sim but do not publish on the real robot — avoid them in any code expected to run on hardware.
- **Workspace overlay.** `~/meam520_ws/devel_isolated/setup.bash` chains through `trail_mix`, so a single source brings in Team 2's package. If a future plain `catkin_make_isolated` regenerates the toplevel and drops `trail_mix`, source `devel_isolated/trail_mix/setup.bash` directly as a workaround.
