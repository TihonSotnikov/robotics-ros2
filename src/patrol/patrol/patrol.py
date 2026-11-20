"""Publish velocity commands for turtlesim using ROS parameters."""

from math import isfinite

from geometry_msgs.msg import Twist
from rcl_interfaces.msg import SetParametersResult
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from turtlesim_msgs.msg import Pose


PARAMETER_LIMITS = {
    'linear_speed': (0.0, 1.0),
    'turn_rate': (-1.0, 1.0),
    'publish_hz': (1.0, 30.0),
}


def validate_parameter(name: str, value: float) -> str:
    """Return an error message for an invalid motion parameter."""
    minimum, maximum = PARAMETER_LIMITS[name]
    if not isfinite(value) or not minimum <= value <= maximum:
        return f'{name} must be finite and in [{minimum}, {maximum}]'
    return ''


def choose_command(
    pose: Pose | None, linear_speed: float, turn_rate: float,
) -> tuple[float, float]:
    """Wait for the first pose before commanding movement."""
    if pose is None:
        return 0.0, 0.0
    return linear_speed, turn_rate


class Patrol(Node):
    """Keep the latest pose and periodically publish a Twist."""

    def __init__(self) -> None:
        """Declare motion settings and connect the ROS graph."""
        super().__init__('patrol')
        self.add_on_set_parameters_callback(self.check_parameters)
        self.declare_parameter('linear_speed', 0.5)
        self.declare_parameter('turn_rate', 0.3)
        frequency = self.declare_parameter('publish_hz', 10.0).get_parameter_value()

        self.last_pose: Pose | None = None
        self.pose_sub = self.create_subscription(
            Pose, '/turtle1/pose', self.on_pose, 10)
        self.cmd_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.timer = self.create_timer(1.0 / frequency.double_value, self.on_timer)
        self.add_post_set_parameters_callback(self.apply_parameters)

    def check_parameters(self, parameters: list[Parameter]) -> SetParametersResult:
        """Validate motion settings before ROS stores them."""
        for parameter in parameters:
            if parameter.name in PARAMETER_LIMITS:
                value = parameter.get_parameter_value().double_value
                reason = validate_parameter(parameter.name, value)
                if reason:
                    return SetParametersResult(successful=False, reason=reason)
        return SetParametersResult(successful=True)

    def apply_parameters(self, parameters: list[Parameter]) -> None:
        """Replace the timer after ROS accepts a publish frequency."""
        for parameter in parameters:
            if parameter.name == 'publish_hz':
                frequency = parameter.get_parameter_value().double_value
                replacement = self.create_timer(
                    1.0 / frequency, self.on_timer, autostart=False)
                self.timer.cancel()
                self.destroy_timer(self.timer)
                self.timer = replacement
                self.timer.reset()

    def on_pose(self, msg: Pose) -> None:
        """Remember the latest pose."""
        self.last_pose = msg

    def on_timer(self) -> None:
        """Publish a command using the current motion settings."""
        linear_speed = self.get_parameter('linear_speed').get_parameter_value().double_value
        turn_rate = self.get_parameter('turn_rate').get_parameter_value().double_value
        linear, angular = choose_command(self.last_pose, linear_speed, turn_rate)
        msg = Twist()
        msg.linear.x = linear
        msg.angular.z = angular
        self.cmd_pub.publish(msg)


def main() -> None:
    """Run the patrol node until interrupted."""
    with rclpy.init():
        node = Patrol()
        try:
            rclpy.spin(node)
        except KeyboardInterrupt:
            pass
        finally:
            node.destroy_node()


if __name__ == '__main__':
    main()
