"""Phase 2: mock for franka2 (the toppings robot — what Teams 17-19 will ship).

Same shape as service_mock.py, but for robot_group == "toppings" and the
dispense_nuts / dispense_candy / exchange actions.

Not in v1: --fail-rate, --no-sim, dispatch tables, retry logic.
"""

import rospy
from trail_mix.interface import TrailMixInterface as TMI

try:
    from helpers import build_robot_status
except ImportError:
    def build_robot_status(order_id, robot_group, action, status, detail=""):
        msg = TMI.robot_status.msg_type()
        msg.order_id = order_id
        msg.robot_group = robot_group
        msg.action = action
        msg.status = status
        if hasattr(msg, "timestamp"):
            msg.timestamp = rospy.Time.now()
        if hasattr(msg, "detail"):
            msg.detail = detail
        return msg

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
        detail = "toppings_mock does not handle action %r" % msg.action
        rospy.logwarn(detail)
        status_pub.publish(
            build_robot_status(
                msg.order_id,
                "toppings",
                msg.action,
                "error",
                detail=detail,
            )
        )
        return

    rospy.loginfo(
        "toppings_mock: order %s starting %s", msg.order_id, msg.action
    )
    status_pub.publish(
        build_robot_status(
            msg.order_id,
            "toppings",
            msg.action,
            "in_progress",
        )
    )

    rospy.sleep(TOPPINGS_ACTION_DURATIONS[msg.action])

    rospy.loginfo(
        "toppings_mock: order %s finished %s", msg.order_id, msg.action
    )
    status_pub.publish(
        build_robot_status(
            msg.order_id,
            "toppings",
            msg.action,
            "done",
        )
    )


def main():
    rospy.init_node("toppings_mock")
    status_pub = TMI.robot_status.publisher(queue_size=10)
    TMI.task_cmd.subscriber(lambda msg: on_task_cmd(msg, status_pub))
    rospy.loginfo("toppings_mock ready")
    rospy.spin()


if __name__ == "__main__":
    main()
