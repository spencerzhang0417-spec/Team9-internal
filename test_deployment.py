"""Phase 0: simulation deployment readiness probe.

Question:  Which sim components and controllers are currently deployed?
Action:    Query /gazebo/get_world_properties for models; probe per-namespace
           controller_manager services for whether the controller stack is up.
Output:    Per-category breakdown of present vs the project-spec target
           (4-Franka, 2-line trail-mix system). Exits 0 always — this is a
           status report, not a pass/fail test.

Why this exists: Team 8's sim is shipped progressively (line 1 first, then
line 2; controllers added over time). Other tests in this suite use
`require_models(...)` to SKIP when their dependency hasn't shipped yet,
distinguishing "Team 8 hasn't deployed X" from "Team 8 deployed X but it's
broken". This file shows the full deployment picture in one place.

Update the EXPECTED dict below as Team 8 ships line 2 (their naming for
franka3/4 and the second turntable is a guess until they confirm).
"""

import sys
import rospy

from helpers import wait_for_sim, list_gazebo_models, controller_manager_running

# Best-guess project-spec target. Line 2 names (franka3, franka4, turntable2)
# are placeholders — update when Team 8 confirms their naming convention.
EXPECTED = {
    "service robots":  ("franka1", "franka3"),
    "toppings robots": ("franka2", "franka4"),
    "turntables":      ("turntable", "turntable2"),
    "dispensers":      ("dispenser1", "dispenser2", "dispenser3",
                        "dispenser4", "dispenser5", "dispenser6"),
    "cups":            ("cup_z_021", "cup_z_022", "cup_z_023", "cup_z_024"),
}


def status(n_present, n_total):
    if n_total == 0:
        return "n/a"
    if n_present == n_total:
        return "OK"
    if n_present == 0:
        return "NOT DEPLOYED"
    return f"PARTIAL ({n_present}/{n_total})"


def main():
    rospy.init_node("test_deployment", anonymous=True)
    wait_for_sim()

    models = set(list_gazebo_models())

    print("=== Gazebo models ===")
    for category, expected in EXPECTED.items():
        present = [m for m in expected if m in models]
        missing = [m for m in expected if m not in models]
        print(f"  [{status(len(present), len(expected))}] {category}: present={present}, missing={missing}")

    print()
    print("=== Controller managers ===")
    cm_targets = (list(EXPECTED["service robots"])
                  + list(EXPECTED["toppings robots"])
                  + list(EXPECTED["turntables"]))
    for ns in cm_targets:
        if ns not in models:
            print(f"  [SKIP] /{ns}/controller_manager (model not in sim)")
            continue
        running = controller_manager_running(ns)
        print(f"  [{'OK' if running else 'MISSING'}] /{ns}/controller_manager")

    print()
    print("(diagnostic only — exits 0 regardless. Tests that depend on")
    print(" missing components will SKIP, not FAIL.)")
    sys.exit(0)


if __name__ == "__main__":
    main()