"""Phase 1: does the dispenser lever joint actuate and return?

Question:  Does the lever move past a threshold when pushed, then return when
           released?
Action:    Read joint angle, apply effort via /gazebo/apply_joint_effort, read,
           release, read again.
PASS:      Joint moved past threshold, then returned to within 0.05 rad of
           neutral.
Catches:   joint dropped from URDF, dispenser_spring.py not running, spring
           constant misconfigured.
"""

# import sys
# import rospy
# from helpers import wait_for_sim, DISPENSER_MODEL, DISPENSER_LEVER_JOINT


def read_lever_angle():
    # Subscribe to /dispenser1/joint_states, return DISPENSER_LEVER_JOINT pos.
    pass


def apply_lever_effort(effort, duration):
    # /gazebo/apply_joint_effort on DISPENSER_LEVER_JOINT.
    pass


def main():
    # rospy.init_node("test_dispenser_lever", anonymous=True)
    # wait_for_sim()
    # neutral = read_lever_angle()
    # apply_lever_effort(effort=5.0, duration=0.5)
    # peak = read_lever_angle()
    # rospy.sleep(1.0)  # let spring return it
    # rest = read_lever_angle()
    # moved = abs(peak - neutral) > 0.2
    # returned = abs(rest - neutral) < 0.05
    # ok = moved and returned
    # print PASS/FAIL with neutral/peak/rest values, sys.exit(0 if ok else 1)
    pass


if __name__ == "__main__":
    main()