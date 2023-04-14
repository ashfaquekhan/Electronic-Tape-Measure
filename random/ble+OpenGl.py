import bluetooth 
import socket
import struct
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5 import QtGui
from PyQt5 import QtOpenGL
from PyQt5.QtOpenGL import *
from PyQt5.QtGui import  QPainter, QOpenGLVertexArrayObject, QOpenGLBuffer
from OpenGL.GL import *
from OpenGL.GLUT import glutBitmapCharacter, GLUT_BITMAP_HELVETICA_18
import ctypes

class BluetoothThread(QThread):
    data_received = pyqtSignal(str)
    
    def __init__(self, device_name):
        super().__init__()
        self.device_name = device_name
        self.target_address = None

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
            data = b''
            while len(data) < 8:
                data += s.recv(1)
            x, y, z, r = struct.unpack('<hhhh', data[:8])
            #print(f"raw data={data} : x={x/100}, y={y/100}, z={z/100}")
            print(f"x={x/100}, y={y/100}, z={z/100} ,r={r/1}")
            self.data_received.emit(f"x={x/100}, y={y/100}, z={z/100} ,r={r/1}")
            data = data[8:]

        s.close()



class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 0.0)

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glColor3f(1.0, 1.0, 1.0)
        glRasterPos2f(-0.95, 0.95)
        text = f'x={self.x:.2f}, y={self.y:.2f}, z={self.z:.2f}'
        # for c in text:
        #     glutBitmapCharacter(ctypes.c_void_p(GLUT_BITMAP_HELVETICA_18), ord(c))


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Accelerometer Data Visualization")
        self.setGeometry(100, 100, 600, 400)

        # Create a combo box to select the Bluetooth device to connect to
        self.device_combo = QComboBox()
        self.device_combo.setMaximumWidth(300)
        self.device_combo.addItems([bluetooth.lookup_name(address) for address in bluetooth.discover_devices()])

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_clicked)

        # Create a label to display the selected Bluetooth device
        self.data_recv_label = QLabel()
        self.data_recv_label.setAlignment(Qt.AlignCenter)

        # Create a GLWidget to display the accelerometer data
        self.gl_widget = GLWidget()

        # Create a layout for the device selection UI
        device_layout = QHBoxLayout()
        device_layout.addWidget(QLabel("Select Bluetooth Device: "))
        device_layout.addWidget(self.device_combo)
        device_layout.addWidget(self.connect_button)
        #button UI

     
        # Create a layout for the device info UI

        # Create a layout for the UI
        layout = QVBoxLayout()
        layout.addLayout(device_layout)
        layout.addWidget(self.data_recv_label)
        layout.addWidget(self.gl_widget)

        self.setLayout(layout)
        self.thread =None

    def connect_clicked(self):
        device_name = self.device_combo.currentText()
        if self.thread is not None:
            self.thread.terminate()
        self.thread = BluetoothThread(device_name)
        self.thread.data_received.connect(self.data_received)
        self.thread.finished.connect(self.connect_finished)
        self.connect_button.setEnabled(False)
        self.thread.start()

    def data_received(self, data):
        self.data_recv_label.setText(data)

    def connect_finished(self):
        self.connect_button.setEnabled(True)


    def update_gl_widget(self, x, y, z):
        # Update the GLWidget with the new accelerometer data
        self.gl_widget.x = x
        self.gl_widget.y = y
        self.gl_widget.z = z
        self.gl_widget.update()

    def on_data_received(self, x, y, z):
        self.gl_widget.x = x
        self.gl_widget.y = y
        self.gl_widget.z = z
        self.gl_widget.update()



app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
