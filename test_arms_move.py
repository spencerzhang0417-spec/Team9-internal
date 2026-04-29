"""Phase 1: do ArmController(id=1) and ArmController(id=2) drive the arms?

Question:  Can each arm be commanded to two distinct configurations and reach
           them?
Action:    For each arm: safe_move_to_position(neutral), then a second target.
           Read final joint state.
PASS:      Joint states within 0.05 rad of each commanded pose for both arms.
Catches:   namespace/topic relay regressions in project.launch, one arm not
           coming up.
"""

# import sys
# import numpy as np
# import rospy
# from core.interfaces import ArmController
# from helpers import wait_for_sim, FRANKA_NAMESPACES


def reached(arm, target, tol=0.05):
    # Compare arm.get_positions() to `target` joint-by-joint.
    pass


def main():
    # rospy.init_node("test_arms_move", anonymous=True)
    # wait_for_sim()
    # neutral = <7-DoF neutral>
    # second  = <7-DoF second pose>
    # results = []
    # for arm_id in (1, 2):
    #     arm = ArmController(id=arm_id)
    #     arm.safe_move_to_position(neutral)
    #     ok_n = reached(arm, neutral)
    #     arm.safe_move_to_position(second)
    #     ok_s = reached(arm, second)
    #     results.append((arm_id, ok_n, ok_s))
    # ok = all(n and s for _, n, s in results)
    # print PASS/FAIL with per-arm details, sys.exit(0 if ok else 1)
    pass


if __name__ == "__main__":
    main()