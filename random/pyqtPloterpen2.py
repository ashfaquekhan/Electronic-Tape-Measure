import bluetooth 
import socket
import struct
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5 import QtGui
from PyQt5 import QtOpenGL
from PyQt5.QtOpenGL import *
from PyQt5.QtGui import QPainter, QColor, QPen, QOpenGLVertexArrayObject, QOpenGLBuffer
from OpenGL.GL import *
from OpenGL.GLUT import glutBitmapCharacter, GLUT_BITMAP_HELVETICA_18
import ctypes
import math
from PyQt5.QtGui import QPainterPath

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
        

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), QColor(0, 0, 0))
        pen = QPen(QColor(255, 255, 255))
        pen.setWidth(2)
        painter.setPen(pen)

        # Adjust the coordinate system to make the center of the widget the origin
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(1, -1)

        # Draw the path using the adjusted coordinate system
        painter.drawPath(self.path)
        
    def addLine(self, x1, y1, x2, y2):
        if x1 != x2 or y1 != y2:
            self.path.lineTo(x2, y2)
        self.update()


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

     
        # Create a layout for ploter
        self.paint_plot=DrawingWidget() 
        self.paint_plot.setGeometry(500,100,400,3800)
        self.paint_plot.setVisible(True)


        # Create a layout for the UI
        layout = QVBoxLayout()
        layout.addLayout(device_layout)
        layout.addWidget(self.data_recv_label)

        layout.addWidget(self.paint_plot)

        self.setLayout(layout)
        self.thread =None

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


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
