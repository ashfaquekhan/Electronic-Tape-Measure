import bluetooth
import struct
import socket
import sys
import math
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtGui import QPainterPath
target_name = "HC-05"
target_address = None
nearby_devices = bluetooth.discover_devices()

for bdaddr in nearby_devices:
    if target_name == bluetooth.lookup_name(bdaddr):
        target_address = bdaddr
        break

if target_address is not None:
    print("found target bluetooth device with address ", target_address)
else:
    print("could not find target bluetooth device nearby")

port = 1
s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
size = 2048
s.connect((target_address, port))
print("CONNECTED")

d = "0"
s.send(d.encode())
x_pos = 400
y_pos = 300
r_value = 0
y_value = 0



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
        painter.drawPath(self.path)

    def addLine(self, x1, y1, x2, y2):
        if x1 != x2 or y1 != y2:
            self.path.lineTo(x2, y2)
            self.update()

def readData(s, drawing_widget):
    while True:
        global x_pos,y_pos
        data = b''
        while len(data) < 8:
            data += s.recv(1)
        y, _, _, r = struct.unpack('<hhhh', data[:8])
        y_value = y / 100
        r_value = r / 1
        print(f"y={y/100},r={r/1},({x_pos},{y_pos})")
        data = data[8:]
        x_pos_new = x_pos + r_value * math.cos(math.radians(y_value))
        y_pos_new = y_pos + r_value * math.sin(math.radians(y_value))
        drawing_widget.addLine(x_pos, y_pos, x_pos_new, y_pos_new)
        x_pos = x_pos_new
        y_pos = y_pos_new

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Drawing")
        vbox = QVBoxLayout()
        self.drawing_widget = DrawingWidget()
        vbox.addWidget(self.drawing_widget)
        self.setLayout(vbox)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    t = threading.Thread(target=readData, args=(s, main_window.drawing_widget))
    t.start()
    sys.exit(app.exec_())
