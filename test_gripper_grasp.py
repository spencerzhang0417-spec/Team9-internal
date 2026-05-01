"""Phase 1: gripper API smoke test.

Question:  Does `arm._gripper.move_joints(width)` complete for both an open
           and a close command? (Gripper action server alive, commands
           accepted, no crash.)
Action:    Drive franka1 to neutral. Call move_joints(0.08) then move_joints(0.0).
PASS:      Both calls return without raising.
Catches:   gripper action server not running, gripper namespace
           misconfigured, regressions that break the move_joints API.

Out of scope (and **not** tested here): cup-gripper contact physics. We
tried — position-controller compliance under contact, Gazebo sim quirks, and
blocking-action calls under physics-pause all made a contact test brittle
and prone to false PASS/FAIL. Team 16's service-robot QC exercises the
"does the grip hold the cup" question as a side effect of their `pick_cup`
test, which is the right level for that question.

Gripper API: arm._gripper.move_joints(width). Do NOT use exec_gripper_cmd
or _gripper.grasp — see "Known Gaps in core.interfaces.ArmController" in
README.md.
"""

import sys
import rospy
from core.interfaces import ArmController
from helpers import wait_for_sim


def main():
    rospy.init_node("test_gripper_grasp", anonymous=True)
    wait_for_sim()
    arm = ArmController(id=1)
    arm.move_to_neutral()
    try:
        arm._gripper.move_joints(0.08)   # NOT exec_gripper_cmd
        arm._gripper.move_joints(0.00)   # NOT exec_gripper_cmd / grasp
    except Exception as e:
        print(f"FAIL test_gripper_grasp ({type(e).__name__}: {e})")
        sys.exit(1)
    print("PASS test_gripper_grasp (open + close commands both completed)")
    sys.exit(0)


if __name__ == "__main__":
    main()