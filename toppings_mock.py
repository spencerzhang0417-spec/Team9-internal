"""Phase 2: mock for franka2 (the toppings robot — what Teams 17-19 will ship).

Same shape as service_mock.py, but for robot_group == "toppings" and the
dispense_nuts / dispense_candy / exchange actions.

Not in v1: --fail-rate, --no-sim, dispatch tables, retry logic.
"""

# import rospy
# from trail_mix.interface import TrailMixInterface
# from helpers import build_robot_status

# Hardcoded plausible durations (seconds) — toppings robot actions only.
TOPPINGS_ACTION_DURATIONS = {
    "dispense_nuts": 2.5,
    "dispense_candy": 2.5,
    "exchange": 2.0,
}


def on_task_cmd(msg, status_pub):
    # Ignore unless msg.robot_group == "toppings".
    # Publish in_progress, sleep duration, publish done.
    pass


def main():
    # rospy.init_node("toppings_mock")
    # tmi = TrailMixInterface()
    # status_pub = tmi.robot_status.publisher()
    # tmi.task_cmd.subscriber(lambda m: on_task_cmd(m, status_pub))
    # rospy.spin()
    pass


if __name__ == "__main__":
    main()