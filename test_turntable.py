"""Phase 1: does the turntable rotate, and does a cup ride along?

Question:  Does TURNTABLE_MODEL's rotating link spin under applied effort,
           and does a cup placed on it move with it?
Action:    Teleport CUP_MODEL onto the turntable, apply effort to the joint
           via /gazebo/apply_joint_effort, wait, re-measure.
PASS:      Turntable yaw changed by > 0.2 rad AND cup horizontal position
           changed by > 0.02 m (cup followed the turntable).
Catches:   turntable joint dropped from URDF, /gazebo/apply_joint_effort
           regression, cup not in contact with the surface, friction broken.

Note: we use /gazebo/apply_joint_effort directly (same approach as
dispenser_spring.py) rather than the turntable_controller velocity command
topic. The controller_spawner in turntable.launch fails silently — there
is no /turntable/controller_manager service in the running sim, so the
controller never loads. Using effort-on-joint bypasses this Team 8 issue
and tests what we actually care about: the joint is actuated and the cup
follows.
"""

import math
import sys

import rospy
from gazebo_msgs.srv import ApplyJointEffort

from helpers import (
    wait_for_sim, get_pose, set_pose, get_link_pose, require_models,
    CUP_MODEL, TURNTABLE_MODEL, TURNTABLE_JOINT, TURNTABLE_ROTATING_LINK,
)

JOINT = f"{TURNTABLE_MODEL}::{TURNTABLE_JOINT}"

CUP_OFFSET = 0.10        # cup placed this far in +x from the turntable centre
CUP_HEIGHT_OFFSET = 0.05 # above the turntable surface so it settles on top
EFFORT = 1.0             # N·m applied to base_rotate
EFFORT_DURATION = 1.0    # s
SETTLE_S = 1.0
PASS_TT_YAW = 0.2        # turntable must rotate at least this much
PASS_CUP_MOVE = 0.02     # cup must move at least this much horizontally

# Where to put cup_z_021 back at end-of-test so test_cup_stack still finds
# it at its expected spawn pose on a re-run without restarting the sim.
# Values mirror project_scene_spawn.yaml `cups[0]`.
CUP_RESTORE_X = 0.00
CUP_RESTORE_Y = 0.00
CUP_RESTORE_Z = 0.21


def yaw_of(orientation):
    # Quaternion -> yaw (z-axis rotation).
    q = orientation
    return math.atan2(2.0 * (q.w * q.z + q.x * q.y),
                      1.0 - 2.0 * (q.y * q.y + q.z * q.z))


def main():
    rospy.init_node("test_turntable", anonymous=True)
    wait_for_sim()
    require_models("test_turntable", TURNTABLE_MODEL, CUP_MODEL)

    rospy.wait_for_service('/gazebo/apply_joint_effort')
    apply_effort = rospy.ServiceProxy('/gazebo/apply_joint_effort', ApplyJointEffort)

    try:
        tt = get_pose(TURNTABLE_MODEL)
        set_pose(CUP_MODEL,
                 x=tt.position.x + CUP_OFFSET,
                 y=tt.position.y,
                 z=tt.position.z + CUP_HEIGHT_OFFSET)
        rospy.sleep(SETTLE_S)

        yaw0 = yaw_of(get_link_pose(TURNTABLE_ROTATING_LINK).orientation)
        cup0 = get_pose(CUP_MODEL).position

        apply_effort(JOINT, EFFORT, rospy.Time.now(), rospy.Duration(EFFORT_DURATION))
        rospy.sleep(EFFORT_DURATION + SETTLE_S)

        yaw1 = yaw_of(get_link_pose(TURNTABLE_ROTATING_LINK).orientation)
        cup1 = get_pose(CUP_MODEL).position

        tt_delta = abs(yaw1 - yaw0)
        cup_delta = math.hypot(cup1.x - cup0.x, cup1.y - cup0.y)
        turned = tt_delta > PASS_TT_YAW
        rode = cup_delta > PASS_CUP_MOVE
        ok = turned and rode

        if ok:
            print(f"PASS test_turntable (tt rotated {tt_delta:.3f} rad, cup moved {cup_delta:.3f} m)")
        elif not turned:
            print(f"FAIL test_turntable (turntable didn't rotate: {tt_delta:.3f} rad < {PASS_TT_YAW}; joint '{JOINT}' not actuated by apply_joint_effort?)")
        else:
            print(f"FAIL test_turntable (cup didn't follow: only {cup_delta:.3f} m < {PASS_CUP_MOVE}; check friction or cup placement)")
        sys.exit(0 if ok else 1)
    finally:
        # Restore cup_z_021 so test_cup_stack still finds it where it expects
        # on a subsequent run without a fresh `roslaunch`.
        set_pose(CUP_MODEL, x=CUP_RESTORE_X, y=CUP_RESTORE_Y, z=CUP_RESTORE_Z)


if __name__ == "__main__":
    main()