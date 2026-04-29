"""Phase 1: does the turntable rotate, and does a cup ride along?

Question:  When commanded 0 -> pi/2, does TURNTABLE_MODEL reach pi/2 and does
           a cup placed on it rotate by the same amount?
Action:    Spawn a cup on the turntable, command rotation, wait, sample yaws.
PASS:      |cup_yaw - turntable_yaw| < 0.1 rad and turntable yaw within 0.1
           rad of pi/2.
Catches:   turntable joint not actuated, cup not in contact, broken friction.
"""

# import math, sys
# import rospy
# from helpers import (wait_for_sim, spawn_cup, delete_model, get_pose,
#                      TURNTABLE_MODEL)


def command_turntable_angle(target_rad):
    # Publish the rotate command on whatever topic Team 10 / Team 8 expose.
    pass


def yaw_of(pose):
    # Quaternion -> yaw.
    pass


def main():
    # rospy.init_node("test_turntable", anonymous=True)
    # wait_for_sim()
    # spawn_cup("test_cup_tt", x=..., y=..., z=...)  # on the turntable
    # try:
    #     command_turntable_angle(math.pi / 2)
    #     rospy.sleep(3.0)
    #     tt_yaw = yaw_of(get_pose(TURNTABLE_MODEL))
    #     cup_yaw = yaw_of(get_pose("test_cup_tt"))
    #     ok = abs(tt_yaw - math.pi/2) < 0.1 and abs(cup_yaw - tt_yaw) < 0.1
    #     print PASS/FAIL with both yaws, sys.exit(0 if ok else 1)
    # finally:
    #     delete_model("test_cup_tt")
    pass


if __name__ == "__main__":
    main()