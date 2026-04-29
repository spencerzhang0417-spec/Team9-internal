"""Phase 3: does an Order flow through the mocks to completion?

Question:  When the canonical 8-step command sequence for one order is
           published, do both mocks acknowledge every step with a `done`?
Action:    subprocess.Popen both mocks, wait ~2 s for subscribers, publish
           commands, collect robot_status for 30 s.
PASS:      Every published command got a matching `done` response.
FAIL:      Names the missing action(s).
Catches:   topic mismatch with Team 2 wrapper, mock crash on a specific
           action, schema drift between RobotCommand and RobotStatus.

Self-contained — `python3 test_e2e_happy_path.py` runs the whole scenario.
"""

# import subprocess, sys, time
# import rospy
# from trail_mix.interface import TrailMixInterface
# from helpers import build_robot_command

# The 8-step happy-path sequence Team 6 emits for one order.
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
    # subprocess.Popen(["python3", "service_mock.py"]),
    # subprocess.Popen(["python3", "toppings_mock.py"]). Return both procs.
    pass


def stop_mocks(procs):
    # Terminate / wait. Used in finally:.
    pass


def main():
    # rospy.init_node("test_e2e_happy_path", anonymous=True)
    # tmi = TrailMixInterface()
    # done_actions = set()
    # tmi.robot_status.subscriber(
    #     lambda m: done_actions.add((m.robot_group, m.action))
    #     if m.status == "done" else None)
    # procs = start_mocks()
    # try:
    #     time.sleep(2.0)
    #     cmd_pub = tmi.task_cmd.publisher()
    #     for i, (group, action) in enumerate(HAPPY_PATH):
    #         cmd_pub.publish(build_robot_command(
    #             order_id=42, robot_group=group, action=action))
    #         time.sleep(0.1)
    #     deadline = time.time() + 30.0
    #     while time.time() < deadline and len(done_actions) < len(HAPPY_PATH):
    #         time.sleep(0.2)
    #     missing = [step for step in HAPPY_PATH if step not in done_actions]
    #     ok = not missing
    #     print PASS/FAIL with missing list, sys.exit(0 if ok else 1)
    # finally:
    #     stop_mocks(procs)
    pass


if __name__ == "__main__":
    main()