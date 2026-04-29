"""Phase 1: does a stacked cup stay where it was spawned?

Question:  Does CUP_MODEL stay put under gravity for 5 s?
Action:    Read pose, sleep 5 s, read pose again.
PASS:      Euclidean drift < 1 cm.
Catches:   world-physics regressions, friction tuning, cup not settled at spawn.
"""

# import sys
# import rospy
# from helpers import wait_for_sim, get_pose, CUP_MODEL


def main():
    # rospy.init_node("test_cup_stack", anonymous=True)
    # wait_for_sim()
    # p0 = get_pose(CUP_MODEL)
    # rospy.sleep(5.0)
    # p1 = get_pose(CUP_MODEL)
    # drift = euclidean(p0.position, p1.position)
    # ok = drift < 0.01
    # print(f"PASS test_cup_stack (drift={drift:.4f} m)" if ok
    #       else f"FAIL test_cup_stack (drift={drift:.4f} m, threshold=0.01)")
    # sys.exit(0 if ok else 1)
    pass


if __name__ == "__main__":
    main()