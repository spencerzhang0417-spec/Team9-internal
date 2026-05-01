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
from gazebo_msgs.srv import GetModelState, SetModelState, GetLinkState, GetWorldProperties
from gazebo_msgs.msg import ModelState
from geometry_msgs.msg import Pose, Point, Quaternion
from tf.transformations import quaternion_from_euler

# Exit codes for tests:
#   0 = PASS, 1 = FAIL (component broken), 2 = SKIP (component not deployed)
EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_SKIP = 2

# ---------------------------------------------------------------------------
# Constants — mirror project_scene_spawn.yaml + launch files.
# Update here when Team 8 renames anything in their world.
# ---------------------------------------------------------------------------

CUP_MODEL = "cup_z_021"                  # cups[0].model_name in scene yaml
DISPENSER_MODEL = "dispenser1"           # dispensers[0]
TURNTABLE_MODEL = "turntable"            # tables[0]
TURNTABLE_ROTATING_LINK = "turntable::upper_base"   # rotating link per turntable.xacro
DISPENSER_LEVER_JOINT = "lever"          # dispenser.urdf joint name
TURNTABLE_JOINT = "base_rotate"          # turntable.xacro continuous joint
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
        print(f"ERROR: get_pose('{model_name}') failed: {e}")
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


def list_gazebo_models():
    # Wrap /gazebo/get_world_properties. Returns list of model name strings
    # currently in the sim. Used by deployment probe + per-test preflight.
    proxy = rospy.ServiceProxy('/gazebo/get_world_properties', GetWorldProperties)
    try:
        return list(proxy().model_names)
    except rospy.ServiceException as e:
        print(f"ERROR: list_gazebo_models() failed: {e}")
        return []


def require_models(test_name, *names):
    # Preflight check used by tests to skip cleanly when Team 8 hasn't deployed
    # a required model yet (vs failing as if the component were broken).
    # Exits with EXIT_SKIP if any are missing; otherwise returns silently.
    models = set(list_gazebo_models())
    missing = [n for n in names if n not in models]
    if missing:
        print(f"SKIP {test_name} (models not deployed yet: {missing})")
        sys.exit(EXIT_SKIP)


def controller_manager_running(namespace, timeout=1.0):
    # True iff /{namespace}/controller_manager/list_controllers service is up.
    # Used by the deployment probe to see whether each robot's controller
    # stack has loaded. Doesn't tell us _which_ controllers are loaded —
    # just whether the controller_manager itself is alive.
    service_name = f"/{namespace}/controller_manager/list_controllers"
    try:
        rospy.wait_for_service(service_name, timeout=timeout)
        return True
    except rospy.ROSException:
        return False


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