# Team 9 — Project Structure

> **Living document.** Update this file whenever a script is added, renamed, or its responsibility changes. Pair it with [README.md](README.md): README explains *why* and *what*, this file explains *where* and *how*.

Last reviewed: 2026-04-28

---

## Layout

Flat folder, pure Python scripts, no catkin packaging. We're consumers of `trail_mix` (Team 2) and `core.interfaces` (existing labs), not a ROS package ourselves.

```
team-09-main/
├── README.md                   project overview + how to run
├── STRUCTURE.md                this file — file-by-file reference
├── helpers.py                  shared gazebo + trail_mix helpers
├── service_mock.py             Phase 2: mock for franka1 (service robot)
├── toppings_mock.py            Phase 2: mock for franka2 (toppings robot)
├── test_arms_move.py           Phase 1: do ArmController(1)/(2) drive the arms?
├── test_cup_stack.py           Phase 1: do stacked cups stay in place?
├── test_dispenser_lever.py     Phase 1: does the lever joint actuate and return?
├── test_gripper_grasp.py       Phase 1: does the gripper hold a cup through a lift?
├── test_turntable.py           Phase 1: does the turntable rotate and carry a cup?
├── test_e2e_happy_path.py      Phase 3: does an Order flow through the mocks to "done"?
└── run_all.sh                  runs every test_*.py, prints PASS/FAIL summary
```

## How to run (plug-and-play)

```bash
# Terminal 1: bring up the sim.
source ~/meam520_ws/devel_isolated/setup.bash
roslaunch meam520_labs project.launch

# Terminal 2: run a single test, or all of them.
source ~/meam520_ws/devel_isolated/setup.bash
cd ~/meam520_ws/src/meam520_labs/team-09-main
python3 test_cup_stack.py        # one test
./run_all.sh                     # all of them
```

Each script prints `PASS test_name (...)` or `FAIL test_name (reason)` and exits 0 / 1.

---

## Pipeline & decoupling from upstream teams

We don't receive a rosbag. **Team 2 ships a contract, not data** — the `trail_mix` package gives us message types and a Python wrapper (`TrailMixInterface`) that names topics. Anything that publishes to those topics (Team 6 at runtime, our own test scripts in CI) hits our subscribers.

### Three data flows, one per phase

```
Phase 1 (sim component checks — Team 2 not involved):
  us ── /gazebo/{get,set}_model_state ──► Team 8's Gazebo ──► us ──► PASS/FAIL

Phase 2 (mocks — Gazebo not strictly required):
  scheduler/test ── task_cmd (RobotCommand) ──► our mock
  our mock ── robot_status (RobotStatus) ──► subscribers

Phase 3 (e2e — pure Team 2 contract):
  test ── task_cmd ──► our mocks ── robot_status ──► test ──► PASS/FAIL
```

Phase 1 doesn't import `trail_mix` at all; Phase 2/3 don't strictly need Gazebo running. The separation is deliberate — each phase is independently runnable.

### What breaks when upstream changes

| Upstream change | What it breaks | Why |
| --- | --- | --- |
| Team 2 renames a topic (e.g. `task_cmd` → `task_command`) | **Nothing** if they keep the attribute on `TrailMixInterface`. | We use `TMI.task_cmd`, never the raw `/scheduler/task_cmd` string. |
| Team 2 changes a message field | The script that reads/writes that field. | Schema changes are unavoidable; mitigated by failing loudly via the validator. |
| Team 2 adds a new enum value | Nothing. | We send only valid ones; new values are additive. |
| Team 8 renames a model in [project_scene_spawn.yaml](../ros/meam520_labs/config/project_scene_spawn.yaml) | Whichever test names that model. | Hardcoded model names — see mitigation #2 below. |
| Team 8 changes a joint name on dispenser/turntable | `test_dispenser_lever.py`, `test_turntable.py`. | Hardcoded joint names — same mitigation. |
| Team 8 changes the world layout (moves franka1 or cup spawn) | Pose-specific tests, when we add them (`test_turntable.py` will spawn a cup on the turntable). `test_arms_move.py` and `test_gripper_grasp.py` are world-layout-independent — the former uses neutral + relative perturbation; the latter only checks the gripper API. | Most current tests are layout-independent by design. |
| Teams 11–19 ship real controllers | **Nothing.** Our mocks become unused. | We don't depend on Teams 11–19; they replace our mocks. |
| Teams 5/6 change scheduling logic | **Nothing for Phase 1/2.** Phase 3 publishes its own commands. | We test against the contract, not against any specific scheduler. |
| `core.interfaces.ArmController` API changes | Phase 1 arm/grasp tests. | Mostly stable, but gripper API has a known sim-vs-real split — see [README.md § Known Gaps in `core.interfaces.ArmController`](README.md#known-gaps-in-coreinterfacesarmcontroller-existing-labs). |

### Three mitigations baked into our design

1. **Always use `TrailMixInterface` attributes, never raw topic strings.** `TMI.task_cmd.publisher()` instead of `rospy.Publisher("/scheduler/task_cmd", ...)`. Team 2 owns the topic name; if they rename it, they update their interface and we keep working. This is what their wrapper exists for.

2. **Centralize Team 8's "magic strings" in `helpers.py` as named constants.** `CUP_MODEL = "cup_z_021"`, `DISPENSER_MODEL = "dispenser1"`, `TURNTABLE_MODEL = "turntable"`, joint names, etc. When Team 8 renames something in their YAML, we update one line and every test picks it up. See the *Constants* table in `helpers.py` below.

3. **One question per test.** When Team 8 breaks the dispenser, only `test_dispenser_lever.py` fails; the others stay green. That's the practical payoff of refusing to share fixtures or parameterize.

What we explicitly **don't** try to handle:

- Gazebo physics tuning that drifts our thresholds (friction, mass). We pick conservative tolerances; if a test starts flaking, we adjust the constant.
- Message schema changes from Team 2 (field renamed/removed). We rely on the [interface.py validator](../team-02-main/src/trail_mix/interface.py#L277-L316) to fail loudly so we know to fix it.

---

## `helpers.py` — shared utilities

The only shared module. Everything tests + mocks both need lives here. Target ~80 lines.

### Constants (the "one place to update if Team 8 changes the world")

These mirror the names in [project_scene_spawn.yaml](../ros/meam520_labs/config/project_scene_spawn.yaml) and the launch files. If Team 8 renames a model or joint, edit this block and every test picks up the change.

| Constant | Current value | Source |
| --- | --- | --- |
| `CUP_MODEL` | `"cup_z_021"` | [project_scene_spawn.yaml](../ros/meam520_labs/config/project_scene_spawn.yaml) `cups[0].model_name` |
| `DISPENSER_MODEL` | `"dispenser1"` | same yaml, `dispensers[0]` |
| `TURNTABLE_MODEL` | `"turntable"` | same yaml, `tables[0]` |
| `DISPENSER_LEVER_JOINT` | TBD when we read [dispenser.urdf](../ros/meam520_labs/urdf/dispenser.urdf) | dispenser URDF |
| `TURNTABLE_JOINT` | TBD when we read [turntable.xacro](../ros/meam520_labs/urdf/turntable.xacro) | turntable xacro |
| `CUP_SDF_PATH` | `meam520_labs/meshes/cup_final/model.sdf` | [scene_model_spawner.py](../ros/meam520_labs/scripts/scene_model_spawner.py) |
| `FRANKA_NAMESPACES` | `("franka1", "franka2")` | [project.launch](../ros/meam520_labs/launch/project.launch) |

Topic strings come from `TrailMixInterface` attributes — never hardcoded here.

### Gazebo wrappers (thin shims around `gazebo_msgs`)

| Function | Purpose |
| --- | --- |
| `wait_for_sim(timeout=30)` | Polls `/gazebo/get_model_state`. If Gazebo isn't up, exits with a clear "Run `roslaunch meam520_labs project.launch`" message instead of a stack trace. |
| `get_pose(model_name)` | Wraps `/gazebo/get_model_state`, returns `Pose`. |
| `set_pose(model_name, x, y, z, yaw=0)` | Wraps `/gazebo/set_model_state` for seeding fixtures at known poses. |
| `get_link_pose(link_name)` | Wraps `/gazebo/get_link_state`. `link_name` is `"model::link"` (e.g. `"franka1::panda_hand"`). Bypasses tf because the `world → franka1/base` static transform in [project.launch](../ros/meam520_labs/launch/project.launch) is identity while Gazebo spawns franka1 at `y=-0.99`. |
| `spawn_cup(name, x, y, z)` | Wraps `/gazebo/spawn_sdf_model` using the cup SDF at `meam520_labs/meshes/cup_final/model.sdf` (same path [scene_model_spawner.py](../ros/meam520_labs/scripts/scene_model_spawner.py) uses). |
| `delete_model(name)` | Cleanup after a test that spawned something. |

### TrailMix helpers (avoid `order_id` validator gotcha)

The interface validator at [team-02-main/src/trail_mix/interface.py:175-199](../team-02-main/src/trail_mix/interface.py#L175-L199) rejects messages with `order_id <= 0`. These helpers always set it correctly:

| Function | Purpose |
| --- | --- |
| `build_robot_status(order_id, robot_group, action, status, detail="")` | Returns a `RobotStatus` with `timestamp = rospy.Time.now()` filled in. Used by mocks. |
| `build_robot_command(order_id, robot_group, action, target_id="", quantity=1)` | Returns a `RobotCommand`. Used by `test_e2e_happy_path.py`. |

No test framework, no result reporting, no fixture decorators here — keep this file small.

---

## Phase 1 tests — sim component checks

Every test follows the same skeleton (~50 lines each):

```python
rospy.init_node("test_X", anonymous=True)
wait_for_sim()
# do thing
# check result
print("PASS test_X (...)" if ok else f"FAIL test_X ({reason})")
sys.exit(0 if ok else 1)
```

### `test_cup_stack.py` — does a stacked cup stay put?

- Read pose of `cup_z_021`, sleep 5 s, read again.
- **PASS** if Euclidean drift < 1 cm.
- **Catches:** world-physics regressions, friction tuning issues, cup not properly settled at spawn.

### `test_dispenser_lever.py` — does the lever joint actuate and return?

- Read `dispenser1` lever joint angle. Apply effort via `/gazebo/apply_joint_effort`. Read again. Release. Read again.
- **PASS** if the joint moved past a threshold, then returned to within 0.05 rad of neutral.
- **Catches:** joint dropped from URDF, [dispenser_spring.py](../ros/meam520_labs/scripts/dispenser_spring.py) not running, spring constant misconfigured.

### `test_turntable.py` — does the turntable rotate, and does a cup ride along?

- Spawn a cup on the turntable. Send the rotate command (0 → π/2). Wait. Check turntable yaw and cup yaw both moved by ~π/2.
- **PASS** if cup angular position within 0.1 rad of turntable's.
- **Catches:** turntable joint not actuated, cup not in contact, friction broken.

### `test_gripper_grasp.py` — gripper API smoke test

- `ArmController(id=1).move_to_neutral()` → `_gripper.move_joints(0.08)` → `_gripper.move_joints(0.00)`. PASS if neither call raises.
- **Scope: API smoke only.** Verifies the gripper action server is up and `move_joints` is wired correctly. Catches "gripper namespace misconfigured", "action server crashed at sim start", "API regression breaks move_joints".
- **Does NOT test contact physics** (does the closed gripper hold a cup against gravity?). We tried that with several approaches — teleport-then-close, physics pause, slow close — and every one was brittle: position-controller compliance under contact wobbles the wrist 3°+, blocking action calls hang while physics is paused, contact dynamics eject the cup unpredictably. The *correct* level for the grip-holds-cup question is **Team 16's service-robot QC**: when their `pick_cup` test runs, the real picking controller drives the real gripper around a real cup and a held-cup outcome falls out as a side effect. Layered tests work; duplicating their test at our scope did not.
- Gripper open/close uses `arm._gripper.move_joints(width)` — **not** `exec_gripper_cmd` or `_gripper.grasp`. See [README.md § Known Gaps in `core.interfaces.ArmController`](README.md#known-gaps-in-coreinterfacesarmcontroller-existing-labs) for why those are sim-only false greens. The smoke test exercises the supported path so a regression on `move_joints` itself surfaces here.

### `test_arms_move.py` — do `ArmController(1)` and `ArmController(2)` drive the arms?

- `ArmController(id=1).safe_move_to_position(neutral)`, then a second target. Same for `id=2`.
- **PASS** if joint states for `franka1` and `franka2` reach within 0.05 rad of each commanded pose.
- **Catches:** namespace/topic relay regressions in [project.launch](../ros/meam520_labs/launch/project.launch), one arm not coming up.

---

## Phase 2 mocks — fake robot controllers

### `service_mock.py` — pretends to be Teams 11–15 (franka1)

- Subscribes to `task_cmd` via `TrailMixInterface`. For commands where `robot_group == "service"`:
  1. Publish `RobotStatus(status="in_progress")`.
  2. `rospy.sleep(D)` — `D` is a hardcoded plausible duration per action (e.g. `pick_cup`: 2 s, `dispense_cereal`: 3 s, `mix`: 2 s, `serve`: 2 s).
  3. Publish `RobotStatus(status="done")`.
- Run as `python3 service_mock.py`. That's the whole node.

### `toppings_mock.py` — pretends to be Teams 17–19 (franka2)

- Same shape as `service_mock.py`, but listens for `robot_group == "toppings"` and the `dispense_nuts` / `dispense_candy` / `exchange` actions.

**Not in v1:** `--fail-rate`, `--no-sim`, dispatch tables, retry logic. Add only when a consumer team explicitly asks for them.

---

## Phase 3 — one end-to-end test

### `test_e2e_happy_path.py` — does an Order flow through the mocks to completion?

- Subscribe to `robot_status` *before* starting the mocks (so we don't miss early statuses).
- `subprocess.Popen` both mocks (with `cwd=team-09-main/` so they can import `helpers`). Then poll `cmd_pub.get_num_connections()` until it reaches 2 — this is more robust than a fixed sleep and handles slow rospy startup. If under 2 after 10 s, FAIL early naming the connection count.
- Publish a sequence of `RobotCommand` messages mirroring what Team 6 would emit for one order: `pick_cup` → `dispense_cereal` → `mix` → `exchange` → `dispense_nuts` → `dispense_candy` → `exchange` → `serve`. Both `exchange` actions appear, one per `robot_group`, and they stay distinct in our `(group, action)` set.
- Wait up to 30 s for every `(group, action)` to come back as `status="done"`.
- **PASS** if every command got a matching `done` response.
- **FAIL** naming the missing `(group, action)` pair(s).
- `finally:` `terminate()` → `wait(5 s)` → `kill()` for both mock subprocesses.

Self-contained — one `python3 test_e2e_happy_path.py` runs the whole scenario; no need to start mocks in separate terminals.

**Not in v1:** queued orders, mid-flight failures, parallel-line scenarios. Add only when a consumer team asks.

---

## `run_all.sh` — plug-and-play runner

From `team-09-main/`:

```bash
./run_all.sh
```

- Iterates `test_*.py`, runs each with `python3`, captures exit code.
- Prints a summary: `PASSED: N  FAILED: M` plus names of failing tests.
- Exits non-zero if any test failed (CI-friendly).
- Assumes `roslaunch meam520_labs project.launch` is already running — individual tests give a clear error if not.

---

## What's deliberately NOT in this structure

- **No `setup.py` / `package.xml` / `CMakeLists.txt`.** We're not a catkin package. We import from `trail_mix` (built) and `core.interfaces` (already in the workspace). Saves ~50 lines of boilerplate.
- **No `tests/` or `mocks/` subdirectory.** Would force `__init__.py` files and either `python3 -m` invocation or `sys.path` hacks. Flat is one fewer thing to explain.
- **No `pytest` config.** Standalone scripts that print PASS/FAIL work in CI, terminals, screenshots, anywhere. Pytest would gain nothing and force teaching teammates a new tool.
- **No conformance walker, no failure injection, no `--no-sim`.** Speculative features. Add when a specific team asks.

---

## Maintenance

When you change anything in the table of files above, update this document in the same commit:

- New script → add a section explaining its question, action, PASS criterion, and what it catches.
- Renamed / removed script → update the layout tree and remove/rename the section.
- Helper added to `helpers.py` → add a row to the helpers table.
- Phase 2/3 features added (e.g. `--fail-rate`) → document the flag and which consumer team asked for it.
- **Team 8 ships a world update** → check [project_scene_spawn.yaml](../ros/meam520_labs/config/project_scene_spawn.yaml) and the URDFs, update the *Constants* table and the corresponding values in `helpers.py`.
- **Team 2 changes a message schema** → update any test/mock that uses the changed field, and note the change in [README.md](README.md)'s *Known Gaps* if it affects design assumptions.
