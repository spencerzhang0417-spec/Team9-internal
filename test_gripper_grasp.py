"""Phase 1: does the gripper hold a cup through a lift?

Question:  After ArmController(1) closes on a cup and lifts 10 cm, is the cup
           still up there 3 s later?
Action:    Move above cup, open, lower, close, lift, wait, read cup pose.
PASS:      cup z rose by >= 8 cm and stayed there 3 s after the lift.
Catches:   gripper geometry broken, finger friction wrong, cup mass mistuned.
"""

# import sys
# import rospy
# from core.interfaces import ArmController
# from helpers import wait_for_sim, get_pose, CUP_MODEL


def main():
    # rospy.init_node("test_gripper_grasp", anonymous=True)
    # wait_for_sim()
    # arm = ArmController(id=1)
    # z0 = get_pose(CUP_MODEL).position.z
    # arm.safe_move_to_position(<above cup pose>)
    # arm.open_gripper()
    # arm.safe_move_to_position(<at cup pose>)
    # arm.close_gripper()
    # arm.safe_move_to_position(<10 cm above pose>)
    # rospy.sleep(3.0)
    # z1 = get_pose(CUP_MODEL).position.z
    # rise = z1 - z0
    # ok = rise >= 0.08
    # print PASS/FAIL with rise, sys.exit(0 if ok else 1)
    pass


if __name__ == "__main__":
    main()