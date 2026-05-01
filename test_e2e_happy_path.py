"""Phase 3: does an Order flow through the mocks to completion?

Question:  When the canonical 8-step command sequence for one order is
           published, do both mocks acknowledge every step with a `done`?
Action:    subprocess.Popen both mocks, wait for them to subscribe, publish
           commands, collect robot_status for up to 30 s.
PASS:      Every published command got a matching `done` response.
FAIL:      Names the missing (group, action) pair(s).
Catches:   topic mismatch with Team 2 wrapper, mock crash on a specific
           action, schema drift between RobotCommand and RobotStatus.

Self-contained — `python3 test_e2e_happy_path.py` runs the whole scenario.
Requires roscore (or the project sim) to be running. Gazebo not required.
"""

import os
import subprocess
import sys
import time

import rospy
from trail_mix.interface import TrailMixInterface as TMI
from helpers import build_robot_command

ORDER_ID = 42

# 8-step happy-path sequence Team 6 emits for one order.
HAPPY_PATH = [
    ("service",  "pick_cup"),
    ("service",  "dispense_cereal"),
    ("service",  "mix"),
    ("service",  "exchange"),
    ("toppings", "dispense_nuts"),
    ("toppings", "dispense_candy"),
    ("toppings", "exchange"),
    ("service",  "serve"),
]


def start_mocks():
    here = os.path.dirname(os.path.abspath(__file__))
    return [
        subprocess.Popen(["python3", os.path.join(here, "service_mock.py")], cwd=here),
        subprocess.Popen(["python3", os.path.join(here, "toppings_mock.py")], cwd=here),
    ]


def stop_mocks(procs):
    for p in procs:
        p.terminate()
    for p in procs:
        try:
            p.wait(timeout=5.0)
        except subprocess.TimeoutExpired:
            p.kill()


def main():
    rospy.init_node("test_e2e_happy_path", anonymous=True)

    # Subscribe BEFORE starting mocks so we don't miss early statuses.
    done_pairs = set()
    TMI.robot_status.subscriber(
        lambda m: done_pairs.add((m.robot_group, m.action)) if m.status == "done" else None
    )

    procs = start_mocks()
    try:
        cmd_pub = TMI.task_cmd.publisher(queue_size=10)
        # Wait for both mocks to subscribe to task_cmd. Wall-clock here is
        # fine because we're waiting on Python subprocess startup, not on
        # any sim-time-driven mock work.
        deadline = time.time() + 10.0
        while cmd_pub.get_num_connections() < 2 and time.time() < deadline:
            time.sleep(0.1)
        if cmd_pub.get_num_connections() < 2:
            print(f"FAIL test_e2e_happy_path (only {cmd_pub.get_num_connections()}/2 mocks subscribed within 10s)")
            sys.exit(1)

        # Publish the 8 commands.
        for group, action in HAPPY_PATH:
            cmd_pub.publish(build_robot_command(
                order_id=ORDER_ID, robot_group=group, action=action,
            ))
            time.sleep(0.2)

        # Wait up to 30 SIM seconds for every (group, action) to come back
        # as "done". Use rospy.Time / rospy.sleep, not time.time / time.sleep,
        # because the mocks use rospy.sleep — if Gazebo's RTF is < 1, a wall-
        # clock deadline expires long before mock work finishes in sim time.
        expected = set(HAPPY_PATH)
        deadline = rospy.Time.now() + rospy.Duration(30.0)
        while rospy.Time.now() < deadline and not expected.issubset(done_pairs):
            rospy.sleep(0.2)

        missing = sorted(expected - done_pairs)
        ok = not missing
        if ok:
            print(f"PASS test_e2e_happy_path (all {len(expected)} actions done)")
        else:
            print(f"FAIL test_e2e_happy_path ({len(missing)}/{len(expected)} missing: {missing})")
        sys.exit(0 if ok else 1)
    finally:
        stop_mocks(procs)


if __name__ == "__main__":
    main()