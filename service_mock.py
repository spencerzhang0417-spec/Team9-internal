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

# import rospy
# from trail_mix.interface import TrailMixInterface
# from helpers import build_robot_status

# Hardcoded plausible durations (seconds) — service robot actions only.
SERVICE_ACTION_DURATIONS = {
    "pick_cup": 2.0,
    "dispense_cereal": 3.0,
    "mix": 2.0,
    "exchange": 2.0,
    "serve": 2.0,
}


def on_task_cmd(msg, status_pub):
    # Ignore unless msg.robot_group == "service".
    # Publish in_progress, sleep duration, publish done.
    pass


def main():
    # rospy.init_node("service_mock")
    # tmi = TrailMixInterface()
    # status_pub = tmi.robot_status.publisher()
    # tmi.task_cmd.subscriber(lambda m: on_task_cmd(m, status_pub))
    # rospy.spin()
    pass


if __name__ == "__main__":
    main()