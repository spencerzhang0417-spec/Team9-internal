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
from helpers import build_robot_status

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
        return
    rospy.loginfo("service_mock: %s order=%d (sleep %.1fs)",
                  msg.action, msg.order_id, SERVICE_ACTION_DURATIONS[msg.action])
    status_pub.publish(build_robot_status(
        order_id=msg.order_id, robot_group="service",
        action=msg.action, status="in_progress",
    ))
    rospy.sleep(SERVICE_ACTION_DURATIONS[msg.action])
    status_pub.publish(build_robot_status(
        order_id=msg.order_id, robot_group="service",
        action=msg.action, status="done",
    ))


def main():
    rospy.init_node("service_mock")
    status_pub = TMI.robot_status.publisher(queue_size=10)
    TMI.task_cmd.subscriber(lambda m: on_task_cmd(m, status_pub))
    rospy.loginfo("service_mock ready (actions: %s)",
                  list(SERVICE_ACTION_DURATIONS))
    rospy.spin()


if __name__ == "__main__":
    main()