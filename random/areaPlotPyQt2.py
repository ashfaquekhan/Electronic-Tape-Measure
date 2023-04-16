import json
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QPainter, QPolygon, QPen
from PyQt5.QtCore import Qt, QPoint, QLineF, QPointF

def calculate_area(points):
    """
    Calculates the area of a polygon defined by the given points.
    Assumes the points are in clockwise order.
    """
    n = len(points)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += points[i][0] * points[j][1] - points[j][0] * points[i][1]
    return abs(area) / 2.0

def calculate_distance_and_displacement(points):
    """
    Calculates the distance and displacement from start to end point.
    """
    start_point = QPointF(*points[0])
    end_point = QPointF(*points[-1])
    displacement = end_point - start_point
    distance = QLineF(start_point, end_point).length()
    x_disp, y_disp = displacement.x(), displacement.y()
    return distance, displacement, x_disp, y_disp

# Load GeoJSON data from file
with open('D:\prjX\pointsO.geojson', 'r') as f:
    data = json.load(f)

# Extract coordinates from GeoJSON features
features = data['features']
points = []
for feature in features:
    geometry = feature['geometry']
    if geometry['type'] == 'Point':
        x, y = geometry['coordinates']
        points.append((x, y))

class Example(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Polygon Area and Perimeter Calculator'
        self.left = 100
        self.top = 100
        self.width = 800
        self.height = 600
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        # Calculate area and perimeter of the bounded region
        intersection = QLineF(QPointF(*points[0]), QPointF(*points[-1])).intersects(QLineF(QPointF(*points[1]), QPointF(*points[-2])))
        if intersection:
            area = calculate_area(points)
            perimeter = sum(QLineF(QPointF(*p1), QPointF(*p2)).length() for p1, p2 in zip(points, points[1:]))
            result_label = QLabel(f"Area: {area:.2f}\nPerimeter: {perimeter:.2f}")
        else:
            distance, displacement, x_disp, y_disp = calculate_distance_and_displacement(points)
            result_label = QLabel(f"Distance: {distance:.2f}\nDisplacement: ({displacement.x():.2f}, {displacement.y():.2f})\nX displacement: {x_disp:.2f}\nY displacement: {y_disp:.2f}")
        
        # Set up layout
        layout = QVBoxLayout()
        layout.addWidget(result_label)
        self.setLayout(layout)
        self.show()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.draw_lines(qp)
        self.draw_polygon(qp)
        qp.end()

    def draw_lines(self, qp):
        pen = QPen(Qt.black, 2, Qt.SolidLine)
        qp.setPen(pen)
        for i in range(len(points) - 1):
            x1, y1 = map(int, points[i])
            x2, y2 = map(int, points[i+1])
            qp.drawLine(x1, y1, x2, y2)

    def draw_polygon(self, qp):
        polygon = QPolygon([QPoint(int(p[0]), int(p[1])) for p in points])
        brush = Qt.green
        qp.setBrush(brush)
        qp.drawPolygon(polygon)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
