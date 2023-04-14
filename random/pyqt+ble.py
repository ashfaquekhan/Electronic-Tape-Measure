import bluetooth 
import socket
import struct
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt, QThread, pyqtSignal

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
            self.data_received.emit("Could not find target device.")
            return

        port = 1
        s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        size = 2048
        try:
            s.connect((self.target_address, port))
        except socket.error as e:
            print(f"Error connecting to device: {e}")
            self.data_received.emit("Error connecting to device.")
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

class MainWindow(QWidget):
    def __init__(self,parent=None):
        super().__init__()

        self.devices_combo = QComboBox()
        self.devices_combo.addItems([bluetooth.lookup_name(address) for address in bluetooth.discover_devices()])

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_clicked)

        self.label = QLabel("Waiting for data...")

        devices_layout = QHBoxLayout()
        devices_layout.addWidget(self.devices_combo)
        devices_layout.addWidget(self.connect_button)

        layout = QVBoxLayout()
        layout.addLayout(devices_layout)
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.thread = None

    def connect_clicked(self):
        device_name = self.devices_combo.currentText()
        if self.thread is not None:
            self.thread.terminate()
        self.thread = BluetoothThread(device_name)
        self.thread.data_received.connect(self.data_received)
        self.thread.finished.connect(self.connect_finished)
        self.connect_button.setEnabled(False)
        self.thread.start()

    def data_received(self, data):
        self.label.setText(data)

    def connect_finished(self):
        self.connect_button.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
