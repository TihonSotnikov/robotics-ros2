"""Republish the simulator pose as a best-effort sensor stream."""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from turtlesim_msgs.msg import Pose


class PoseRelay(Node):
    """Forward each simulator pose without modifying it."""

    def __init__(self) -> None:
        """Connect the input and output through a subscription callback."""
        super().__init__('pose_relay')
        sensor_qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.sensor_pub = self.create_publisher(Pose, 'sensor_pose', sensor_qos)
        self.pose_sub = self.create_subscription(Pose, 'turtle1/pose', self.on_pose, 10)

    def on_pose(self, pose: Pose) -> None:
        """Publish the received position, heading and velocities unchanged."""
        self.sensor_pub.publish(pose)


def main() -> None:
    """Run the relay until interrupted."""
    with rclpy.init():
        node = PoseRelay()
        try:
            rclpy.spin(node)
        except KeyboardInterrupt:
            pass
        finally:
            node.destroy_node()
