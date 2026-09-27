import json
import math
from pathlib import Path

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from track_core import compute_centerline, save_results


class TrackSubscriber(Node):
    def __init__(self):
        super().__init__("track_subscriber")

        default_output = (
            Path(__file__).resolve().parent.parent / "output" / "ros"
        )
        self.declare_parameter("output_dir", str(default_output))
        self.output_dir = self.get_parameter("output_dir").value

        self.completed = False

        self.subscription = self.create_subscription(
            String,
            "/track_points",
            self.process_track,
            10,
        )

        self.get_logger().info("Waiting for track points...")

    def process_track(self, message):
        if self.completed:
            return

        try:
            payload = json.loads(message.data)
            left = self.validate_points(payload["left"])
            right = self.validate_points(payload["right"])
            centerline = compute_centerline(left, right)
        except (ValueError, TypeError, KeyError) as error:
            self.get_logger().error(f"Invalid track message: {error}")
            return

        try:
            save_results(left, right, centerline, self.output_dir)
        except OSError as error:
            self.get_logger().error(f"Could not save results: {error}")
            return

        self.completed = True
        self.get_logger().info(
            f"Received {len(left)} left and {len(right)} right points. "
            f"Saved {len(centerline)} centerline points to {self.output_dir}"
        )

    @staticmethod
    def validate_points(points):
        if not isinstance(points, list):
            raise ValueError("Boundary must be a list")

        result = []

        for point in points:
            if not isinstance(point, list) or len(point) != 2:
                raise ValueError("Each point must contain x and y")

            x, y = map(float, point)

            if not (math.isfinite(x) and math.isfinite(y)):
                raise ValueError("Coordinates must be finite")

            result.append((x, y))

        return result


def main():
    rclpy.init()
    node = None

    try:
        node = TrackSubscriber()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
