"""Shared utilities for Team 9 sim QC tests + mocks.

Two responsibilities:
  1. Constants — centralize Team 8's "magic strings" (model/joint names) so a
     world rename costs one line, not N tests.
  2. Thin shims — Gazebo service wrappers and well-formed TrailMix message
     builders (so we don't trip the order_id>0 validator).

No test framework, no result reporting, no fixtures — keep this file small.
"""

# ---------------------------------------------------------------------------
# Constants — mirror project_scene_spawn.yaml + launch files.
# Update here when Team 8 renames anything in their world.
# ---------------------------------------------------------------------------

CUP_MODEL = "cup_z_021"                  # cups[0].model_name in scene yaml
DISPENSER_MODEL = "dispenser1"           # dispensers[0]
TURNTABLE_MODEL = "turntable"            # tables[0]
DISPENSER_LEVER_JOINT = None             # TBD — read from dispenser.urdf
TURNTABLE_JOINT = None                   # TBD — read from turntable.xacro
CUP_SDF_PATH = "meam520_labs/meshes/cup_final/model.sdf"
FRANKA_NAMESPACES = ("franka1", "franka2")


# ---------------------------------------------------------------------------
# Gazebo wrappers — thin shims around gazebo_msgs services.
# ---------------------------------------------------------------------------

def wait_for_sim(timeout=30):
    # Poll /gazebo/get_model_state until it answers, or exit with a clear
    # "Run `roslaunch meam520_labs project.launch`" message.
    pass


def get_pose(model_name):
    # Wrap /gazebo/get_model_state. Returns geometry_msgs/Pose.
    pass


def set_pose(model_name, x, y, z, yaw=0):
    # Wrap /gazebo/set_model_state. Used to seed fixtures at known poses.
    pass


def spawn_cup(name, x, y, z):
    # Wrap /gazebo/spawn_sdf_model using CUP_SDF_PATH (same path
    # scene_model_spawner.py uses).
    pass


def delete_model(name):
    # Wrap /gazebo/delete_model. Cleanup after a test that spawned something.
    pass


# ---------------------------------------------------------------------------
# TrailMix builders — always set order_id > 0 + timestamp, so the
# interface.py:175-199 validator never rejects our messages.
# ---------------------------------------------------------------------------

def build_robot_status(order_id, robot_group, action, status, detail=""):
    # Returns a trail_mix/RobotStatus with timestamp = rospy.Time.now().
    # Used by service_mock.py and toppings_mock.py.
    pass


def build_robot_command(order_id, robot_group, action, target_id="", quantity=1):
    # Returns a trail_mix/RobotCommand. Used by test_e2e_happy_path.py.
    pass