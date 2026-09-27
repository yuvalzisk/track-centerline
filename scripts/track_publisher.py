import json
from pathlib import Path

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from track_core import load_track


class TrackPublisher(Node):
    def __init__(self):
        super().__init__("track_publisher")

        default_csv = (
            Path(__file__).resolve().parent.parent
            / "data"
            / "BrandsHatchLayout.csv"
        )

        self.declare_parameter("csv_path", str(default_csv))
        csv_path = self.get_parameter("csv_path").value

        left, right, skipped = load_track(csv_path)

        if not left or not right:
            raise ValueError("Both track boundaries must contain points.")

        self.message = String()
        self.message.data = json.dumps(
            {"left": left, "right": right},
            allow_nan=False,
        )

        self.publisher = self.create_publisher(
            String, "/track_points", 10
        )

        self.timer = self.create_timer(2.0, self.publish_track)

        self.get_logger().info(
            f"Loaded {len(left)} left and {len(right)} right points. "
            f"Skipped rows: {skipped}"
        )

    def publish_track(self):
        self.publisher.publish(self.message)
        self.get_logger().info("Published track boundaries")


def main():
    rclpy.init()
    node = None

    try:
        node = TrackPublisher()
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
