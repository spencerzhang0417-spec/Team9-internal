# MEAM 5200 Final Project — Team 9 (Simulation QC)

> **See also:** [STRUCTURE.md](STRUCTURE.md) for the file-by-file design — what each script is, what question it answers, and what's deliberately left out. README is *why/what*; STRUCTURE is *where/how*.


## The Class Project

MEAM 5200's final project is a four-robot Franka system that serves custom-ordered trail mix at the ROBO MS thesis reception on May 8, 2026. Two assembly lines run in parallel, each with two Panda arms and a turntable between them. The robot closer to the customer is the **service robot** (picks cups, dispenses cereal base, mixes, serves). The further one is the **toppings robot** (dispenses nuts and candy). Cups pass between them via the turntable since there are no robot-to-robot handoffs.

Customers enter orders through a frontend; a scheduler decides which assembly line handles each order and coordinates the robots. The class is split into 20 teams of 4, each owning one module of the system. The point is to learn modular systems engineering: defining clean interfaces, coordinating with adjacent teams, and getting independent modules to compose into a working whole.

## Team Roles Relevant to Us

- **Team 1** — Frontend / order UI
- **Team 2** — Communications (ROS message and topic layer)
- **Team 3, 4** — World tracking and cup tracking (perception, AprilTags)
- **Team 5** — Scheduler, high-level (assigns orders to assembly lines)
- **Team 6** — Scheduler, mid-level (translates orders to action sequences) + maintains the orchestrator that launches all teams' code
- **Team 7** — Scheduler QC
- **Team 8** — Simulation (Gazebo world, dual-Franka setup)
- **Team 9 — Simulation QC (us)**
- **Team 10** — Turntable control
- **Teams 11–15** — Service robot subtasks (pick cup, turntable exchange, cereal dispense, mix, serve)
- **Team 16** — Service robot QC
- **Teams 17–19** — Toppings robot subtasks (turntable exchange, candy, nuts)
- **Team 20** — Toppings robot QC

## Our Role: Team 9 — Simulation QC

Per the project spec, our job is to *"construct test scenarios for the simulation. Write control code that checks the simulator outputs, provides control inputs, and checks the resulting state... In the absence of functional robot code, this code could be used to test the communications, front end, and scheduler."*

What that means in practice:

We are **not** part of the runtime system that runs on demo day. The demo runs on physical hardware in the lab; simulation is a development tool, not a deliverable. We exist to support other teams *before* demo day by giving them a way to test their modules without waiting on the rest of the class.

Our deliverable is **test code that other teams run**. Two flavors:

1. **Sim validator tests** — quick checks that Team 8's Gazebo world behaves: cups stay stacked, the dispenser lever moves, the turntable rotates, the gripper holds a cup. Each test answers one yes/no question.
2. **Mock robot stand-ins** — small ROS nodes that pretend to be the robot teams (11–19) so that the scheduler / comms / frontend teams (1, 2, 5, 6) can integration-test without waiting for real robot controllers.

We are a CI/QA tool for the class, not a system component.

## Design Principles

This is the bar we hold our own code to:

- **Plug-and-play.** A teammate from another team should be able to run one command (`python3 tests/test_xxx.py` or `pytest tests/`) and get a clear PASS / FAIL with no setup beyond sourcing the workspace. No config files, no flags, no extra dependencies.
- **Simple beats thorough.** Each test asks one question — "is this component working as intended?" — and answers it with the minimum code needed. No sweeping a parameter to find a slip threshold; no chaos-monkey failure injection; no exhaustive edge-case matrices. Those are research projects, not what other teams need from us.
- **Effective beats clever.** Prefer obvious code over abstractions. A 30-line script that calls `gazebo_msgs` services directly is better than a 200-line framework with handler dispatch tables and fixture decorators. Three similar tests that copy each other are better than one parameterized meta-test.
- **Failures are useful.** When a test fails, the error message names the component and the expected vs actual value. A teammate should be able to read it and know whether to file a Team 8 bug, a Team 2 bug, or fix their own code.
- **No half-finished features.** Don't ship a `--fail-rate` flag, a `--no-sim` mode, or a conformance walker just because they're in this README. Add features only when a specific team asks for them.

## What We Have to Build Against

- **Team 2's repo** (`team-02`) — a fully shipped ROS communications package. Defines 9 custom message types (`Order`, `OrderAssigned`, `RobotCommand`, `RobotStatus`, `WorldState`, `CupState`, etc.) and a Python wrapper `TrailMixInterface` that handles topic registration, type checking, enum validation, and rate monitoring. The README contains the canonical topic table specifying which teams publish/subscribe to what. **This is the contract everyone builds against, including us.** Our row in the table: subscribes to `task_cmd`; publishes to `robot_status`, `turntable_status`, `world_state`.

- **Team 8's repo** (`team-08`) — Gazebo world (`final.world`) with the dual-Franka setup, turntable, and placeholder objects. Some of the dispenser/turntable modeling may still be in progress; we'll find out when we read the world file. Their work is the substrate our Phase 1 tests run against.

- **Team 6's orchestrator** (`final_project`) — process launcher (`clone_repos.sh` + `orchestrator.py`) that coordinates startup of all 20 teams' code on demo-relevant runs. **Mostly not our concern** since we don't deploy on demo day. The one place it touches us: a useful test in our suite is a conformance check that verifies other teams' `main.py` files satisfy the contract Team 6's orchestrator expects, since broken conformance would block real integration.

## Environment

- Ubuntu 20.04, ROS 1 Noetic, Python 3.8
- Workspace `~/meam520_ws`, built with `catkin_make_isolated`
- Sim launched via `roslaunch meam520_labs project.launch` — Team 8's project world (turntable + 6 dispensers + stacked cups + dual Franka arms `franka1` at y=-0.99, `franka2` at y=+0.99). Note: today the sim is a **single assembly line**, not two parallel lines yet.
- Robots controlled per existing labs via `ArmController(id=1)` and `ArmController(id=2)` — see [labs/final/final.py](../labs/final/final.py) for a working example.

### Repo layout we build against

- [team-02-main](../team-02-main) — the `trail_mix` ROS package. Build with `catkin_make_isolated --pkg trail_mix`. Contains `msg/`, `src/trail_mix/interface.py`, and the canonical topic table (in [team-02-main/README.md](../team-02-main/README.md)).
- [team-08-main](../team-08-main) — Team 8's reference copy. The actual deployed sim is at [meam520_labs/ros/meam520_labs/](../ros/meam520_labs/) (byte-identical at time of writing). The team-08 source copy carries a `CATKIN_IGNORE` so catkin only builds one. When Team 8 ships an update, copy `team-08-main/ros/meam520_labs/*` into `meam520_labs/ros/meam520_labs/` rather than removing the marker.

## High-Level Plan

### Sim primitives we get for free

Team 8's world exposes everything we need over `gazebo_msgs` — no extra plumbing required:

| Primitive | How | Used for |
| --- | --- | --- |
| Pose query | `/gazebo/get_model_state` (see [team-08-main/get_coords.py](../team-08-main/get_coords.py)) | Drift, lever angle, gripper-vs-cup pose checks |
| Pose set | `/gazebo/set_model_state` | Seed test fixtures at known poses |
| Spawn cup | `/gazebo/spawn_sdf_model` (see [scene_model_spawner.py](../ros/meam520_labs/scripts/scene_model_spawner.py)) | Add fresh cups for a test run, clean up after |
| Joint state | `/franka{1,2}/joint_states`, `/turntable/...`, `/dispenser*/joint_states` | Verify dispenser lever rotated, turntable reached target |
| Arm control | `ArmController(id=1)` / `ArmController(id=2)` (see [labs/final/final.py](../labs/final/final.py)) | Drive arms into test configurations |
| Comms | `from trail_mix.interface import TrailMixInterface` | Publish/subscribe with type + enum + `order_id>0` validation |

### Phase 1 — Sim component checks

One small script per component. Each one asks the question, prints PASS / FAIL with one line of context, exits. No frameworks, no fixtures.

- **`test_cup_stack.py`** — does a stacked cup stay where it was spawned? Read pose, wait 5 s, read pose again. PASS if drift < 1 cm.
- **`test_dispenser_lever.py`** — does the lever joint move when pushed and return when released? Apply effort, read joint angle, release, read again. PASS if it moved and came back.
- **`test_turntable.py`** — does the turntable rotate to a commanded angle and carry a cup with it? Place a cup, command 90°, check both the table and the cup ended up rotated.
- **`test_gripper_grasp.py`** — does closing the gripper on a cup hold the cup through a small lift? Close, lift, check the cup is still near the gripper.
- **`test_arms_move.py`** — do `ArmController(id=1)` and `ArmController(id=2)` actually drive the arms? Send to neutral, send to a second pose, read joint states.

Each script is self-contained: imports, init_node, do thing, assert, print result. Aim for ~50 lines.

### Phase 2 — Mock robot stand-ins

Two small nodes — `service_mock.py` and `toppings_mock.py`. Each one:

- Subscribes to `task_cmd` via `TrailMixInterface`.
- For commands addressed to it, sleeps a plausible duration and publishes `robot_status="done"` back.
- Helper in `tmi_helpers.py` builds well-formed `RobotStatus` messages (sets `order_id`, `timestamp`) so we don't trip the [interface.py:175-199](../team-02-main/src/trail_mix/interface.py#L175-L199) validator.

That's the whole feature set. If Teams 5/6 later need failure injection or a no-Gazebo mode, we add it then — not before.

### Phase 3 — One end-to-end test

`test_e2e_happy_path.py`: publish one `Order`, wait for the chain of `RobotStatus` messages our mocks emit, assert the order finishes. One scenario, one PASS / FAIL.

More scenarios (queued orders, mid-flight failures) only get added if a consumer team asks for them.

## Known Gaps in Team 2's Interface (to surface, not ignore)

- **`RobotCommand` has no `assembly_line` field.** When both line-1 and line-2 service robots subscribe to `/scheduler/task_cmd`, neither can tell whose command is whose. Either Team 2 needs to add the field, or Team 6 needs to namespace topics per line. Our mocks will need a workaround until this is resolved.
- **`Ingredient.quantity` is `bool` but `RobotCommand.quantity` is `int32`.** Inconsistent; ask Team 1 and Team 2 whether the system supports graduated portions or just include/exclude.
- **`CupState.location` enum lacks `"toppings_robot_gripper"`.** Either docs are incomplete or design assumes cup is "on turntable" while the toppings robot holds it.
- **`RobotCommand.target_id` examples don't include `"nuts"` / `"candy"`.** Likely a docstring bug given the action enum includes `dispense_nuts` and `dispense_candy`.
- **No timestamp on `RobotCommand`, no per-command unique ID.** Limits ability to correlate retries and debug timing.

These are normal v0.1 issues, not failures — but they need to land somewhere before our Phase 2 mocks commit to a particular interpretation.

## Build & Run

```bash
# One-time: build trail_mix (Team 2's comms package).
cd ~/meam520_ws
source /opt/ros/noetic/setup.bash
catkin_make_isolated --pkg trail_mix

# Every shell that wants Team 9 / Team 2 / Team 8 stuff:
source ~/meam520_ws/devel_isolated/setup.bash

# Sanity check:
python3 -c "from trail_mix.interface import TrailMixInterface; print(len(TrailMixInterface.all_topics()), 'topics')"

# Launch sim (Team 8's world):
roslaunch meam520_labs project.launch
```

The toplevel `devel_isolated/setup.bash` was patched on 2026-04-28 to chain through `trail_mix` so everything is on `PYTHONPATH` after a single source. If a future `catkin_make_isolated` (without `--pkg`) regenerates the toplevel and drops `trail_mix` from the chain, re-point it at `devel_isolated/trail_mix/setup.bash`.

## Anticipated Challenges

- **Sim-to-real gap** — anything our mocks pass may still fail on hardware. The class spec acknowledges this; our job is to make the sim-side check pass, not to guarantee hardware behavior.
- **Per-line command routing** — `RobotCommand` has no `assembly_line` field. Not a blocker for us today (sim is one line), but worth tracking.
- **Coordinating with consumer teams** — our value depends on other teams actually running our tests. Clear failure messages and a one-line "how to run" matter more than test breadth.
