"""Launch the PR05 graph and optionally record its sensor topic."""

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    GroupAction,
    IncludeLaunchDescription,
    LogInfo,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node, PushROSNamespace
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    """Keep the simulator global and group the PR05 nodes by namespace."""
    namespace = LaunchConfiguration('namespace')
    record = LaunchConfiguration('record')
    bag_dir = LaunchConfiguration('bag_dir')
    reliability = LaunchConfiguration('subscriber_reliability')
    sensor_topic = PathJoinSubstitution(['/', namespace, 'sensor_pose'])
    sim_launch = PathJoinSubstitution(
        [FindPackageShare('turtle_bringup'), 'launch', 'sim.launch.py'])

    return LaunchDescription([
        DeclareLaunchArgument('namespace', default_value='robot_a'),
        DeclareLaunchArgument('record', default_value='false', choices=['true', 'false']),
        DeclareLaunchArgument('bag_dir', default_value='evidence/pr05/bag'),
        DeclareLaunchArgument(
            'subscriber_reliability', default_value='best_effort',
            choices=['reliable', 'best_effort']),
        LogInfo(msg=['Sensor topic: ', sensor_topic, ' | subscriber: ', reliability]),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(sim_launch)),
        GroupAction([
            PushROSNamespace(namespace),
            Node(
                package='patrol', executable='patrol', output='screen',
                remappings=[
                    ('turtle1/pose', '/turtle1/pose'),
                    ('cmd_vel', '/turtle1/cmd_vel'),
                ],
            ),
            Node(
                package='patrol', executable='pose_relay', output='screen',
                remappings=[('turtle1/pose', '/turtle1/pose')],
            ),
            Node(
                package='patrol', executable='pose_subscriber', output='screen',
                parameters=[{'reliability': reliability}],
            ),
        ]),
        LogInfo(msg=['Recording one topic to ', bag_dir], condition=IfCondition(record)),
        ExecuteProcess(
            cmd=[
                'ros2', 'bag', 'record', '-s', 'mcap', '-o', bag_dir,
                '--disable-keyboard-controls', '--topics', sensor_topic,
            ],
            output='screen',
            condition=IfCondition(record),
        ),
    ])
