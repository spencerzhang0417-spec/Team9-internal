"""Shared utilities for Team 9 sim QC tests + mocks.

Two responsibilities:
  1. Constants — centralize Team 8's "magic strings" (model/joint names) so a
     world rename costs one line, not N tests.
  2. Thin shims — Gazebo service wrappers and well-formed TrailMix message
     builders (so we don't trip the order_id>0 validator).

No test framework, no result reporting, no fixtures — keep this file small.
"""

import sys
import rospy
from gazebo_msgs.srv import GetModelState, SetModelState, GetLinkState
from gazebo_msgs.msg import ModelState
from geometry_msgs.msg import Pose, Point, Quaternion
from tf.transformations import quaternion_from_euler

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
    try:
        rospy.wait_for_service('/gazebo/get_model_state', timeout=timeout)
    except rospy.ROSException as e:
        print("Error: wait_for_service failed")
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception message: {e}")
        print("If sim is not running, run 'roslaunch meam520_labs project.launch' first")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: unexpected exception: {type(e).__name__}: {e}")
        sys.exit(1)


def get_pose(model_name):
    # Wrap /gazebo/get_model_state. Returns geometry_msgs/Pose.
    get_state = rospy.ServiceProxy('/gazebo/get_model_state', GetModelState)
    try:
        response = get_state(model_name, '')
    except rospy.ServiceException as e:
        print(f"ERROR: get_pose('{model_name}') service call failed: {e}")
        sys.exit(1)
    if not response.success:
        print(f"ERROR: get_pose('{model_name}') failed: {response.status_message}")
        print(f"       Hint: check model names with `rosservice call /gazebo/get_world_properties`.")
        sys.exit(1)
    return response.pose


def set_pose(model_name, x, y, z, yaw=0):
    # Wrap /gazebo/set_model_state. Used to seed fixtures at known poses.
    qx, qy, qz, qw = quaternion_from_euler(0, 0, yaw)
    state = ModelState(
        model_name=model_name,
        pose=Pose(position=Point(x=x, y=y, z=z),
                  orientation=Quaternion(x=qx, y=qy, z=qz, w=qw)),
        reference_frame='world',
    )
    set_state = rospy.ServiceProxy('/gazebo/set_model_state', SetModelState)
    try:
        set_state(state)
    except rospy.ServiceException as e:
        print(f"ERROR: set_pose('{model_name}') failed: {e}")
        sys.exit(1)


def get_link_pose(link_name):
    # Wrap /gazebo/get_link_state. link_name is "model::link" (e.g. "franka1::panda_hand").
    # Bypasses tf because project.launch's world->franka1/base static transform is
    # identity even though Gazebo spawns franka1 at y=-0.99 — tf gives wrong world
    # coords. Gazebo's link state is authoritative.
    proxy = rospy.ServiceProxy('/gazebo/get_link_state', GetLinkState)
    try:
        response = proxy(link_name, 'world')
    except rospy.ServiceException as e:
        print(f"ERROR: get_link_pose('{link_name}') failed: {e}")
        sys.exit(1)
    return response.link_state.pose


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
    # Lazy import so Phase 1 tests can import helpers.py without trail_mix built.
    from trail_mix.msg import RobotStatus
    return RobotStatus(
        order_id=order_id,
        robot_group=robot_group,
        action=action,
        status=status,
        detail=detail,
        timestamp=rospy.Time.now(),
    )


def build_robot_command(order_id, robot_group, action, target_id="", quantity=1):
    from trail_mix.msg import RobotCommand
    return RobotCommand(
        order_id=order_id,
        robot_group=robot_group,
        action=action,
        target_id=target_id,
        quantity=quantity,
    )