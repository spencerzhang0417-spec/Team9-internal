"""Phase 1: do ArmController(id=1) and ArmController(id=2) drive the arms?

Question:  Can each arm be commanded to two distinct configurations and reach
           them?
Action:    For each arm: safe_move_to_position(neutral), then a second target.
           Read final joint state.
PASS:      Joint states within 0.05 rad of each commanded pose for both arms.
Catches:   namespace/topic relay regressions in project.launch, one arm not
           coming up.
"""

import sys
import numpy as np
import rospy
from core.interfaces import ArmController
from helpers import wait_for_sim, FRANKA_NAMESPACES


def reached(arm, target, tol=0.05):
    # Compare arm.get_positions() to `target` joint-by-joint.
    current = np.array(arm.get_positions())
    target = np.array(target)
    err = np.abs(current - target)
    max_err = float(np.max(err))
    ok = max_err < tol
    return ok, max_err


def main():
    rospy.init_node("test_arms_move", anonymous=True)
    wait_for_sim()
    results = [] #store two test results
    for arm_id in (1,2):
        arm = ArmController(id=arm_id) #create arm controller
        print(f"Arm {arm_id}: moving to neutral...")

        # First test
        arm.move_to_neutral()
        ok_n, err_n = reached(arm, arm.neutral_position())

        # Change to a new configuration for second test
        second = np.array(arm.neutral_position()).copy()
        second[0] += np.pi/4
        second[3] -= np.pi/6
        print(f"Arm {arm_id}: moving to second...")
        arm.safe_move_to_position(second)
        ok_s, err_s = reached(arm, second)

        results.append((arm_id, ok_n, err_n, ok_s, err_s))
    all_ok = all(ok_n and ok_s for _, ok_n, _, ok_s, _ in results)
    print()
    for arm_id, ok_n, err_n, ok_s, err_s in results:
        print(f"  Arm {arm_id}: neutral err={err_n:.4f} ({'ok' if ok_n else 'FAIL'}), "
              f"second err={err_s:.4f} ({'ok' if ok_s else 'FAIL'})")
    
    #Final judgement
    if all_ok:
        print("PASS test_arms_move (both arms reached both targets)")
    else:
        print("FAIL test_arms_move (see per-arm details above)")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()