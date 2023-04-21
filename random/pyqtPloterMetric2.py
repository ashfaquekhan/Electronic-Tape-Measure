import bluetooth 
import socket
import struct
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt, QThread, pyqtSignal,QPoint, QLineF, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen,QPolygon,QPainterPath,QTransform
import ctypes
import math

x_pos = 0
y_pos = 0
r_value = 0
y_value = 0

class BluetoothThread(QThread):
    data_received = pyqtSignal(str)
    
    def __init__(self, device_name, drawing_widget):
        super().__init__()
        self.device_name = device_name
        self.target_address = None
        self.drawing_widget = drawing_widget
        self.x_pos_new=x_pos
        self.y_pos_new=y_pos

    def run(self):
        nearby_devices = bluetooth.discover_devices()
        for bdaddr in nearby_devices:
            if self.device_name == bluetooth.lookup_name(bdaddr):
                self.target_address = bdaddr
                break

        if self.target_address is not None:
            print ("found target bluetooth device with address ", self.target_address)
        else:
            print ("could not find target bluetooth device nearby")
            self.data_received.emit("No Device Found")
            return

        port = 1
        s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        size = 2048
        try:
            s.connect((self.target_address, port))
        except socket.error as e:
            print(f"Error connecting to device: {e}")
            self.data_received.emit("No Device Found")
            return

        print("CONNECTED")
        d = "0"
        s.send(d.encode())

        while True:
            global x_pos, y_pos
            data = b''
            while len(data) < 8:
                data += s.recv(1)
            x, y, z, r = struct.unpack('<hhhh', data[:8])
            #print(f"raw data={data} : x={x/100}, y={y/100}, z={z/100}")
            # print(f"x={x/100}, y={y/100}, z={z/100} ,r={r/1}")
            self.data_received.emit(f"x={x/100}, y={y/100}, z={z/100} ,r={r/1}")
            data = data[8:]
            y_value = x / 100
            r_value = r / 1
            self.x_pos_new = x_pos + r_value * math.cos(math.radians(y_value))
            self.y_pos_new = y_pos + r_value * math.sin(math.radians(y_value))
            self.drawing_widget.addLine(self.x_pos_new, self.y_pos_new,x_pos,y_pos)
            x_pos = self.x_pos_new
            y_pos = self.y_pos_new

        s.close()

class DrawingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.path = QPainterPath()
        self.points=[]
        
    def paintEvent(self, event):
        qp = QPainter(self)
        qp.fillRect(event.rect(), QColor(0, 0, 0))
        pen = QPen(QColor(255, 255, 255))
        pen.setWidth(2)
        qp.setPen(pen)

        # Adjust the coordinate system to make the center of the widget the origin
        qp.translate(self.width() / 2, self.height() / 2)
        qp.scale(1, -1)

        # Draw the path using the adjusted coordinate system
        qp.drawPath(self.path)
        
    def addLine(self, x1, y1, x2, y2):
        if x1 != x2 or y1 != y2:
            self.path.lineTo(x2, y2)
            self.points.append((x2,y2))
        self.update()


class MetricsWidget(QWidget):
    def __init__(self):
        super().__init__(parent=None)
        self.path = QPainterPath()
        self.points=[]
        self.area = 0.0
        self.perimeter=0.0
        self.xs=None
        self.ys=None
        self.xe=None
        self.ye=None
        self.displacement=None
        self.penBl = QPen(Qt.blue, 2, Qt.SolidLine)
        self.penBk = QPen(Qt.black, 2, Qt.SolidLine)
        self.penYl = QPen(Qt.green, 2, Qt.SolidLine)
    
    def displayMetrics(self,coordinates):
        self.points=coordinates
        self.xs,self.ys=map(int, self.points[1])
        self.xe,self.ye=map(int, self.points[-1])
        self.calculate_area()
        self.perimeter = sum(QLineF(QPointF(*p1), QPointF(*p2)).length() for p1, p2 in zip(self.points, self.points[1:]))
        self.displacement = math.hypot(self.xe - self.xs, self.ye - self.ys)
        self.x_displacement = self.xe - self.xs
        self.y_displacement = self.ye - self.ys
        # result_label = QLabel(f"Area: {self.area:.2f}\nPerimeter: {self.perimeter:.2f}")
        print(f"Area: {self.area:.2f}\nPerimeter: {self.perimeter:.2f}")
        self.update()

    def paintEvent(self,e):
        qp = QPainter(self)
        qp.translate(self.width() / 2, self.height() / 2)
        qp.scale(1, -1)
        if((self.xs and self.xe and self.ys and self.ye)!=None):
            self.draw_lines(qp)
            self.draw_polygon(qp)
            self.drawPoint(qp)
            self.drawDisplacement(qp)
    
    def drawPoint(self,qp):
        qp.setPen(QPen(Qt.red, 8))
        if len(self.points) >= 2:
            qp.drawPoint(self.xs, self.ys)
            qp.setPen(QPen(Qt.blue, 8))
            qp.drawPoint(self.xe, self.ye)

    def drawDisplacement(self,qp):
        qp.setPen(self.penYl)
        qp.drawLine(self.xs, self.ys, self.xe, self.ye)
        qp.setPen(self.penBk)
        qp.drawLine(self.xs, self.ys, self.xs + self.x_displacement, self.ys)
        qp.setPen(self.penBl)
        qp.drawLine(self.xs, self.ys, self.xs, self.ys + self.y_displacement)

    def draw_lines(self, qp):
        pen = QPen(Qt.black, 2, Qt.SolidLine)
        qp.setPen(pen)
        for i in range(len(self.points) - 1):
            x1, y1 = map(int, self.points[i])
            x2, y2 = map(int, self.points[i+1])
            qp.drawLine(x1, y1, x2, y2)

    def draw_polygon(self, qp):
        polygon = QPolygon([QPoint(int(p[0]), int(p[1])) for p in self.points])
        brush = Qt.yellow
        qp.setBrush(brush)
        qp.drawPolygon(polygon)     

    def calculate_area(self):
        n = len(self.points) 
        for i in range(n):
            j = (i + 1) % n
            self.area += self.points[i][0] * self.points[j][1] - self.points[j][0] * self.points[i][1]
        self.area=abs(self.area)/2


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Accelerometer Data Visualization")
        self.setGeometry(100, 100, 1000, 3000)

        # Create a combo box to select the Bluetooth device to connect to
        self.device_combo = QComboBox()
        self.device_combo.setMaximumWidth(300)
        self.device_combo.addItems([bluetooth.lookup_name(address) for address in bluetooth.discover_devices()])

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_clicked)

        # Create a label to display the selected Bluetooth device
        self.data_recv_label = QLabel()
        self.data_recv_label.setAlignment(Qt.AlignCenter)

        # Create a layout for the device selection UI
        device_layout = QHBoxLayout()
        device_layout.addWidget(QLabel("Select Bluetooth Device: "))
        device_layout.addWidget(self.device_combo)
        device_layout.addWidget(self.connect_button)
        #button UI

        self.metric_plot=MetricsWidget()
        # self.metric_plot.setMaximumWidth(400)
        # self.metric_plot.setContentsMargins(0,0,400,400)
        self.metric_plot.setVisible(True)

        # Create a layout for ploter
        self.paint_plot=DrawingWidget() 
        # self.paint_plot.setMaximumWidth(400)
        # self.paint_plot.setContentsMargins(0,0,400,400)
        self.paint_plot.setVisible(True)

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_clicked)

        self.generate_button = QPushButton("Generate")
        self.generate_button.clicked.connect(self.generate_button_clicked)
        
        plotLayout = QHBoxLayout()
        plotLayout.addWidget(self.paint_plot)
        plotLayout.addWidget(self.metric_plot)

        # Create a layout for the UI
        layout = QVBoxLayout()
        layout.addLayout(plotLayout)
        layout.addLayout(device_layout)
        # layout.addWidget(self.paint_plot)
        # layout.addWidget(self.metric_plot)
        layout.addWidget(self.data_recv_label)
        layout.addWidget(self.generate_button)
        layout.addWidget(self.reset_button)

        self.setLayout(layout)
        self.thread =None

    def generate_button_clicked(self):
        coordinates=self.paint_plot.points
        self.metric_plot.displayMetrics(coordinates)

    def connect_clicked(self):
        device_name = self.device_combo.currentText()
        if self.thread is not None:
            self.thread.terminate()
        self.thread = BluetoothThread(device_name,self.paint_plot)
        self.thread.data_received.connect(self.data_received)
        self.thread.finished.connect(self.connect_finished)
        self.connect_button.setEnabled(False)
        self.thread.start()

    def data_received(self, data):
        self.data_recv_label.setText(data)

    def connect_finished(self):
        self.connect_button.setEnabled(True)

    def reset_clicked(self):
        self.paint_plot.path = QPainterPath()
        self.metric_plot.path=QPainterPath()
        self.paint_plot.update()
        self.metric_plot.update()
        global x_pos, y_pos
        x_pos = 0
        y_pos = 0
        self.paint_plot.points.clear()
        self.metric_plot.points.clear()
        self.metric_plot.area=0.0
        self.metric_plot.perimeter=0.0
        self.metric_plot.xs=None
        self.metric_plot.xe=None
        self.metric_plot.ys=None
        self.metric_plot.ye=None
        self.metric_plot.x_displacement=self.metric_plot.y_displacement=None
        self.metric_plot.displacement=None
        

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
