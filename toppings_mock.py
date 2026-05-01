"""Phase 2: mock for franka2 (the toppings robot — what Teams 17-19 will ship).

Same shape as service_mock.py, but for robot_group == "toppings" and the
dispense_nuts / dispense_candy / exchange actions.

Not in v1: --fail-rate, --no-sim, dispatch tables, retry logic.
"""

import rospy
from trail_mix.interface import TrailMixInterface as TMI
from helpers import build_robot_status

# Hardcoded plausible durations (seconds) — toppings robot actions only.
TOPPINGS_ACTION_DURATIONS = {
    "dispense_nuts": 2.5,
    "dispense_candy": 2.5,
    "exchange": 2.0,
}


def on_task_cmd(msg, status_pub):
    if msg.robot_group != "toppings":
        return
    if msg.action not in TOPPINGS_ACTION_DURATIONS:
        return
    rospy.loginfo("toppings_mock: %s order=%d (sleep %.1fs)",
                  msg.action, msg.order_id, TOPPINGS_ACTION_DURATIONS[msg.action])
    status_pub.publish(build_robot_status(
        order_id=msg.order_id, robot_group="toppings",
        action=msg.action, status="in_progress",
    ))
    rospy.sleep(TOPPINGS_ACTION_DURATIONS[msg.action])
    status_pub.publish(build_robot_status(
        order_id=msg.order_id, robot_group="toppings",
        action=msg.action, status="done",
    ))


def main():
    rospy.init_node("toppings_mock")
    status_pub = TMI.robot_status.publisher(queue_size=10)
    TMI.task_cmd.subscriber(lambda m: on_task_cmd(m, status_pub))
    rospy.loginfo("toppings_mock ready (actions: %s)",
                  list(TOPPINGS_ACTION_DURATIONS))
    rospy.spin()


if __name__ == "__main__":
    main()