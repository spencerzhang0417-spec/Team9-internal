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

import sys
import rospy
from helpers import wait_for_sim, DISPENSER_MODEL, DISPENSER_LEVER_JOINT
from gazebo_msgs.srv import ApplyJointEffort, GetJointProperties

joint_full_name = f"{DISPENSER_MODEL}::{DISPENSER_LEVER_JOINT}"

def read_lever_angle():
    # Subscribe to /dispenser1/joint_states, return DISPENSER_LEVER_JOINT pos.
    proxy = rospy.ServiceProxy('/gazebo/get_joint_properties', GetJointProperties)
    try:
        response = proxy(joint_full_name)
    except rospy.ServiceException as e:
        print(f"ERROR: get_joint_properties('{joint_full_name}') failed: {e}")
        sys.exit(1)
    if not response.success:
        print(f"ERROR: get_joint_properties('{joint_full_name}') failed: {response.status_message}")
        sys.exit(1)
    return response.position[0]


def apply_lever_effort(effort, duration):
    # /gazebo/apply_joint_effort on DISPENSER_LEVER_JOINT.
    proxy = rospy.ServiceProxy('/gazebo/apply_joint_effort', ApplyJointEffort)
    try:
        response = proxy(joint_full_name, effort, rospy.Time.now(),rospy.Duration(duration))
    except rospy.ServiceException as e:
        print(f"ERROR: apply_joint_effort('{joint_full_name}') failed: {e}")
        sys.exit(1)
    if not response.success:
        print(f"ERROR: apply_joint_effort('{joint_full_name}') failed: {response.status_message}")
        sys.exit(1)


def main():
    rospy.init_node("test_dispenser_lever", anonymous=True)
    wait_for_sim()
    neutral = read_lever_angle()
    apply_lever_effort(effort=1, duration=1.2)
    rospy.sleep(0.7)
    peak = read_lever_angle()
    rospy.sleep(1.5)  # let spring return it
    rest = read_lever_angle()
    moved = abs(peak - neutral) > 0.05
    returned = abs(rest - neutral) < 0.05
    ok = moved and returned
    print(f"  neutral={neutral:.4f} rad")
    print(f"  peak   ={peak:.4f} rad   (moved by {abs(peak-neutral):.4f}, threshold 0.05)")
    print(f"  rest   ={rest:.4f} rad   (residual {abs(rest-neutral):.4f}, threshold 0.05)")

    if ok:
        print(f"PASS test_dispenser_lever (moved={abs(peak-neutral):.4f}, "
            f"residual={abs(rest-neutral):.4f})")
    else:
        reasons = []
        if not moved:
            reasons.append(f"did not move enough ({abs(peak-neutral):.4f} < 0.2)")
        if not returned:
            reasons.append(f"did not return ({abs(rest-neutral):.4f} > 0.05)")
        reason = "; ".join(reasons)
        print(f"FAIL test_dispenser_lever ({reason})")
        if not returned:
            print("  Hint: is dispenser_spring.py running? "
                "Check `rosnode list | grep dispenser_spring`.")

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()