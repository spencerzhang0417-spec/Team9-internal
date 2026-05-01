"""Phase 1: does the dispenser lever joint actuate and return?

Question:  Does the lever move past a threshold when pushed, then return when
           released by the spring?
Action:    Read joint angle, apply effort via /gazebo/apply_joint_effort,
           read peak, wait for the spring to settle, read rest.
PASS:      Joint moved past 0.2 rad when pushed AND returned to within
           0.05 rad of neutral.
Catches:   joint dropped from URDF, dispenser_spring.py not running, spring
           constant misconfigured, /gazebo/apply_joint_effort regression.
"""

import sys

import rospy
from gazebo_msgs.srv import ApplyJointEffort, GetJointProperties

from helpers import wait_for_sim, require_models, DISPENSER_MODEL, DISPENSER_LEVER_JOINT

LEVER = f"{DISPENSER_MODEL}::{DISPENSER_LEVER_JOINT}"
PUSH_EFFORT = 5.0       # N·m applied by apply_joint_effort
PUSH_DURATION = 0.5     # seconds the effort is applied for
SPRING_SETTLE_S = 2.0   # how long to wait for dispenser_spring to return it
PASS_PEAK_RAD = 0.2     # joint must deflect at least this much when pushed
PASS_REST_RAD = 0.05    # joint must return within this of neutral


def read_lever_angle():
    proxy = rospy.ServiceProxy('/gazebo/get_joint_properties', GetJointProperties)
    response = proxy(LEVER)
    return response.position[0]


def apply_lever_effort(effort, duration):
    proxy = rospy.ServiceProxy('/gazebo/apply_joint_effort', ApplyJointEffort)
    proxy(LEVER, effort, rospy.Time.now(), rospy.Duration(duration))


def main():
    rospy.init_node("test_dispenser_lever", anonymous=True)
    wait_for_sim()
    require_models("test_dispenser_lever", DISPENSER_MODEL)
    rospy.wait_for_service('/gazebo/get_joint_properties')
    rospy.wait_for_service('/gazebo/apply_joint_effort')

    neutral = read_lever_angle()
    apply_lever_effort(PUSH_EFFORT, PUSH_DURATION)
    rospy.sleep(PUSH_DURATION + 0.1)
    peak = read_lever_angle()
    rospy.sleep(SPRING_SETTLE_S)
    rest = read_lever_angle()

    moved = abs(peak - neutral) > PASS_PEAK_RAD
    returned = abs(rest - neutral) < PASS_REST_RAD
    ok = moved and returned

    if ok:
        print(f"PASS test_dispenser_lever (neutral={neutral:.3f}, peak={peak:.3f}, rest={rest:.3f})")
    elif not moved:
        print(f"FAIL test_dispenser_lever (lever didn't move: |peak - neutral|={abs(peak - neutral):.3f} < {PASS_PEAK_RAD}; check joint name '{LEVER}' or apply_joint_effort)")
    else:
        print(f"FAIL test_dispenser_lever (lever didn't return: |rest - neutral|={abs(rest - neutral):.3f} > {PASS_REST_RAD}; is dispenser_spring.py running?)")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()