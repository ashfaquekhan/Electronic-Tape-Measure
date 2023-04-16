import sys
import math
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView
import json

class GeoJSONViewer(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GeoJSON Viewer")
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

    def load_geojson(self, filename):
        with open(filename, "r") as f:
            data = json.load(f)
        features = data["features"]
        if len(features) < 2:
            raise ValueError("GeoJSON file must contain at least 2 points")

        pen_distance = QPen(QColor(255, 0, 0))
        pen_displacement = QPen(QColor(0, 255, 0))

        total_distance = 0
        start_point = None
        prev_point = None
        for feature in features:
            point = QPointF(*feature["geometry"]["coordinates"])
            if start_point is None:
                start_point = point
            else:
                distance = math.dist((prev_point.x(), prev_point.y()), (point.x(), point.y()))
                total_distance += distance
                self.scene.addLine(prev_point.x(), prev_point.y(), point.x(), point.y(), pen_distance)
            prev_point = point

        end_point = prev_point
        displacement = math.hypot(end_point.x() - start_point.x(), end_point.y() - start_point.y())
        x_displacement = end_point.x() - start_point.x()
        y_displacement = end_point.y() - start_point.y()

        self.scene.clear()
        self.scene.addLine(start_point.x(), start_point.y(), end_point.x(), end_point.y(), pen_distance)
        self.scene.addLine(start_point.x(), start_point.y(), start_point.x() + x_displacement, start_point.y(), pen_displacement)
        self.scene.addLine(start_point.x(), start_point.y(), start_point.x(), start_point.y() + y_displacement, pen_displacement)
        self.scene.addText(f"Distance: {total_distance:.2f}").setPos(10, 10)
        self.scene.addText(f"Displacement: {displacement:.2f}").setPos(10, 30)
        self.scene.addText(f"X Displacement: {x_displacement:.2f}").setPos(10, 50)
        self.scene.addText(f"Y Displacement: {y_displacement:.2f}").setPos(10, 70)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = GeoJSONViewer()
    viewer.show()
    viewer.load_geojson('D:\prjX\pointsO.geojson')
    sys.exit(app.exec_())
