"""Phase 2: mock for franka1 (the service robot — what Teams 11-15 will ship).

Subscribes to task_cmd via TrailMixInterface. For commands where
robot_group == "service":
  1. Publish RobotStatus(status="in_progress").
  2. rospy.sleep(D) where D is a hardcoded plausible duration per action.
  3. Publish RobotStatus(status="done").

Run as `python3 service_mock.py`. That's the whole node.

Not in v1: --fail-rate, --no-sim, dispatch tables, retry logic. Add only when
a consumer team explicitly asks.
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

# Hardcoded plausible durations (seconds) — service robot actions only.
SERVICE_ACTION_DURATIONS = {
    "pick_cup": 2.0,
    "dispense_cereal": 3.0,
    "mix": 2.0,
    "exchange": 2.0,
    "serve": 2.0,
}


def on_task_cmd(msg, status_pub):
    if msg.robot_group != "service":
        return

    if msg.action not in SERVICE_ACTION_DURATIONS:
        detail = "service_mock does not handle action %r" % msg.action
        rospy.logwarn(detail)
        status_pub.publish(
            build_robot_status(
                msg.order_id,
                "service",
                msg.action,
                "error",
                detail=detail,
            )
        )
        return

    rospy.loginfo(
        "service_mock: order %s starting %s", msg.order_id, msg.action
    )
    status_pub.publish(
        build_robot_status(
            msg.order_id,
            "service",
            msg.action,
            "in_progress",
        )
    )

    rospy.sleep(SERVICE_ACTION_DURATIONS[msg.action])

    rospy.loginfo(
        "service_mock: order %s finished %s", msg.order_id, msg.action
    )
    status_pub.publish(
        build_robot_status(
            msg.order_id,
            "service",
            msg.action,
            "done",
        )
    )


def main():
    rospy.init_node("service_mock")
    status_pub = TMI.robot_status.publisher(queue_size=10)
    TMI.task_cmd.subscriber(lambda msg: on_task_cmd(msg, status_pub))
    rospy.loginfo("service_mock ready")
    rospy.spin()


if __name__ == "__main__":
    main()
