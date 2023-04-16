import json
import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QPolygon, QPen
from PyQt5.QtCore import Qt, QPoint

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

# Load GeoJSON data from file
with open('D:\prjX\pointsL.geojson', 'r') as f:
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
        self.title = 'Polygon Area Calculator'
        self.left = 100
        self.top = 100
        self.width = 800
        self.height = 600
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.draw_lines(qp)
        self.draw_polygon(qp)
        qp.end()

    def draw_lines(self, qp):
        pen = QPen(Qt.black, 1, Qt.SolidLine)
        qp.setPen(pen)
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i+1]
            qp.drawLine(x1, y1, x2, y2)

    def draw_polygon(self, qp):
        poly = QPolygon([QPoint(*p) for p in points])
        brush = qp.brush()
        qp.setBrush(Qt.green)
        qp.drawPolygon(poly)
        qp.setBrush(brush)

        area = calculate_area(points)
        print(f"Area: {area}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
