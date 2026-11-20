"""Observe the sensor stream with configurable reliability."""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from turtlesim_msgs.msg import Pose


class PoseSubscriber(Node):
    """Log the first pose delivered with the requested profile."""

    def __init__(self) -> None:
        """Read the requested reliability and subscribe to the sensor."""
        super().__init__('pose_subscriber')
        reliability = self.declare_parameter('reliability', 'best_effort').value
        qos = QoSProfile(
            depth=10, reliability=ReliabilityPolicy.get_from_short_key(reliability))
        self.sensor_sub = self.create_subscription(Pose, 'sensor_pose', self.on_pose, qos)
        self.get_logger().info(f'Waiting for sensor_pose with reliability={reliability}')

    def on_pose(self, pose: Pose) -> None:
        """Confirm delivery once to keep steady-state logs quiet."""
        self.get_logger().info(
            f'First pose received: x={pose.x:.3f}, y={pose.y:.3f}, theta={pose.theta:.3f}',
            once=True)


def main() -> None:
    """Run the subscriber until interrupted."""
    with rclpy.init():
        node = PoseSubscriber()
        try:
            rclpy.spin(node)
        except KeyboardInterrupt:
            pass
        finally:
            node.destroy_node()
