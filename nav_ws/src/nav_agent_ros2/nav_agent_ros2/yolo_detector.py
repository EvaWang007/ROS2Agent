import json
from datetime import datetime

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
from ultralytics import YOLO


class YoloDetector(Node):
    def __init__(self):
        super().__init__("yolo_detector")
        self.bridge = CvBridge()
        self.model = YOLO("yolov8n.pt")  # 首次会自动下载
        self.sub = self.create_subscription(
            Image, "/camera_sensor/image_raw", self.cb, 10
        )
        self.pub = self.create_publisher(String, "/perception/detections_text", 10)

    def cb(self, msg: Image):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        results = self.model(frame, imgsz=416, conf=0.4, verbose=False)
        dets = []
        if results and len(results) > 0 and results[0].boxes is not None:
            names = results[0].names
            for box in results[0].boxes:
                cls_id = int(box.cls.item())
                conf = float(box.conf.item())
                dets.append({"class": names.get(cls_id, str(cls_id)), "conf": round(conf, 3)})

        out = {
            "ts": datetime.utcnow().isoformat(),
            "count": len(dets),
            "detections": dets[:10],
        }
        m = String()
        m.data = json.dumps(out, ensure_ascii=False)
        self.pub.publish(m)


def main():
    rclpy.init()
    node = YoloDetector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()