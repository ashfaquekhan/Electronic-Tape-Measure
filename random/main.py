import bluetooth 
import socket
import struct
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QLabel,QFileDialog, QVBoxLayout, QHBoxLayout, QPushButton,QFrame,QDoubleSpinBox,QCheckBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal,QPoint, QLineF, QPointF,pyqtSlot,QTimer
from PyQt5.QtGui import QPainter, QColor, QPen,QPolygon,QPainterPath,QImage,QPixmap
from PyQt5.QtOpenGL import QGLWidget 
import OpenGL.GL as gl        # python wrapping of OpenGL
from OpenGL import GLU 
import math
import ctypes
import json
from OpenGL.arrays import vbo
import numpy as np

x_pos = 0
y_pos = 0
r_value = 0
y_value = 0
rot_const=0
comp_mode=False
x=0.0
y=0.0
z=0.0

class GLWidget(QGLWidget):
    def __init__(self, parent=None):
        QGLWidget.__init__(self, parent)
            
    def initializeGL(self):
        self.qglClearColor(QColor(0, 0, 0))    # initialize the screen to blue
        gl.glEnable(gl.GL_DEPTH_TEST)                  # enable depth testing
        self.initGeometry()
        self.rotX = 0.0
        self.rotY = 0.0
        self.rotZ = 0.0
         
    def resizeGL(self, width, height):
        gl.glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        aspect = width / float(height)

        GLU.gluPerspective(45.0, aspect, 1.0, 100.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)

    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        gl.glPushMatrix()    # push the current matrix to the current stack

        gl.glTranslate(0.0, 0.0, -50.0)    # third, translate cube to specified depth
        gl.glScale(20.0, 20.0, 20.0)       # second, scale cube
        gl.glRotate(self.rotX, 1.0, 0.0, 0.0)
        gl.glRotate(self.rotY, 0.0, 1.0, 0.0)
        gl.glRotate(self.rotZ, 0.0, 0.0, 1.0)
        gl.glTranslate(-0.5, -0.5, -0.5)   # first, translate cube center to origin

        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_COLOR_ARRAY)

        gl.glVertexPointer(3, gl.GL_FLOAT, 0, self.vertVBO)
        gl.glColorPointer(3, gl.GL_FLOAT, 0, self.colorVBO)

        gl.glDrawElements(gl.GL_LINES, len(self.cubeIdxArray), gl.GL_UNSIGNED_INT, self.cubeIdxArray)

        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisableClientState(gl.GL_COLOR_ARRAY)

        gl.glPopMatrix()    # restore the previous modelview matrix
        
    def initGeometry(self):
        vertices = [
            # Front face
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [0.0, 1.0, 0.0],
            # Back face
            [0.0, 0.0, 1.0],
            [1.0, 0.0, 1.0],
            [1.0, 1.0, 1.0],
            [0.0, 1.0, 1.0],
        ]

        indices = [# Front face
            0, 1, 2, 3,
            4, 5, 6, 7,
            0, 3, 7, 4,
            1, 2, 6, 5,
            2, 3, 7, 6,
            0, 1, 5, 4,]

        self.vertVBO = vbo.VBO(np.array(vertices, dtype=np.float32))
        self.vertVBO.bind()

        self.cubeIdxArray = vbo.VBO(np.array(indices, dtype=np.uint32),
                                    target=gl.GL_ELEMENT_ARRAY_BUFFER)
        self.cubeIdxArray.bind()
        
        self.cubeClrArray = np.array(
                [[0.0, 0.0, 0.0],
                 [1.0, 0.0, 0.0],
                 [1.0, 1.0, 0.0],
                 [0.0, 1.0, 0.0],
                 [0.0, 0.0, 1.0],
                 [1.0, 0.0, 1.0],
                 [1.0, 1.0, 1.0],
                 [0.0, 1.0, 1.0 ]])
        self.colorVBO = vbo.VBO(np.reshape(self.cubeClrArray,
                                           (1, -1)).astype(np.float32))
        self.colorVBO.bind()

    def setRot(self, x,y,z):
        self.rotX = z
        self.rotY = x
        self.rotZ = y
        self.update()

class BluetoothThread(QThread):
    data_received = pyqtSignal(str)
    
    def __init__(self, device_name, drawing_widget,glWidget):
        super().__init__()
        self.device_name = device_name
        self.target_address = None
        self.drawing_widget = drawing_widget
        self.glWidget =glWidget
        self.x_pos_new=x_pos
        self.y_pos_new=y_pos
        self.rot_en=True
        self.rot_en_in=False
        self.prev_pitch=0
        self.x=0.0
        self.y=0.0
        self.z=0.0
        
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
            global x_pos, y_pos,rot_const,x,y,z
            self.x,self.y,self.z=x,y,z
            data = b''
            while len(data) < 8:
                data += s.recv(1)
            self.x, self.y, self.z, r = struct.unpack('<hhhh', data[:8])
            self.z=self.z/100
            y_value = self.x / 100
            r_value = r / 1
            if(self.rot_en_in and r and comp_mode):
                r_value= int(r/1+((self.z-self.prev_pitch)/rot_const))
                self.rot_en=False
            self.data_received.emit(f"x={self.x/100}, y={self.y/100}, z={self.z} ,r={r/1},_r={rot_const}")
            self.glWidget.setRot(self.x/100,self.y/100,self.z)
            data = data[8:]
            self.prev_pitch=self.z
            self.x_pos_new = x_pos + r_value * math.cos(math.radians(y_value))
            self.y_pos_new = y_pos + r_value * math.sin(math.radians(y_value))
            self.drawing_widget.addLine(self.x_pos_new, self.y_pos_new,x_pos,y_pos)
            x_pos = self.x_pos_new
            y_pos = self.y_pos_new
            if(r and self.rot_en and comp_mode):
                self.rot_en_in=True

        s.close()

class DrawingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.path = QPainterPath()
        self.points = []
        self.scale_factor = 1.0
        
    def paintEvent(self, event):
        qp = QPainter(self)
        qp.fillRect(event.rect(), QColor(0, 0, 0))
        pen = QPen(QColor(255, 255, 255))
        pen.setWidth(2)
        qp.setPen(pen)

        # Adjust the coordinate system to make the center of the widget the origin
        qp.translate(self.width() / 2, self.height() / 2)
        qp.scale(self.scale_factor, -self.scale_factor)

        # Draw the path using the adjusted coordinate system
        qp.drawPath(self.path)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            self.scale_factor *= 1.1
        else:
            self.scale_factor /= 1.1
        self.update()

    def addLine(self, x1, y1, x2, y2):
        if x1 != x2 or y1 != y2:
            self.path.lineTo(x2, y2)
            self.points.append((x2, y2))

        self.update()


class MetricsWidget(QWidget):
    def __init__(self):
        super().__init__(parent=None)
        self.scale_factor = 1.0
        self.path = QPainterPath()
        self.points=[]
        self.area = 0.0
        self.perimeter=0.0
        self.xs=0.0
        self.ys=0.0
        self.xe=0.0
        self.ye=0.0
        self.displacement=0.0
        self.x_displacement=0.0
        self.y_displacement=0.0
        self.penBl = QPen(Qt.blue, 2, Qt.SolidLine)
        self.penWt = QPen(Qt.white, 2, Qt.SolidLine)
        self.penGr = QPen(Qt.green, 2, Qt.SolidLine)

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
        # print(f"Area: {self.area:.2f}\nPerimeter: {self.perimeter:.2f}\n")
        self.update()

    def paintEvent(self,e):
        qp = QPainter(self)
        qp.fillRect(e.rect(), QColor(0, 0, 0))
        qp.translate(self.width() / 2, self.height() / 2)
        qp.scale(1, -1)
        qp.scale(self.scale_factor, -self.scale_factor)
        if((self.xs and self.xe and self.ys and self.ye)!=None):
            self.draw_lines(qp)
            self.draw_polygon(qp)
            self.drawPoint(qp)
            self.drawDisplacement(qp)
    
    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            self.scale_factor *= 1.1
        else:
            self.scale_factor /= 1.1
        self.update()

    def drawPoint(self,qp):
        qp.setPen(QPen(Qt.red, 8))
        if len(self.points) >= 1:
            qp.drawPoint(self.xs, self.ys)
            qp.setPen(QPen(Qt.blue, 8))
            qp.drawPoint(self.xe, self.ye)

    def drawDisplacement(self,qp):
        qp.setPen(self.penGr)
        qp.drawLine(int(self.xs), int(self.ys), int(self.xe), int(self.ye))
        qp.setPen(self.penWt)
        qp.drawLine(int(self.xs), int(self.ys), int(self.xs + self.x_displacement), int(self.ys))
        qp.setPen(self.penBl)
        qp.drawLine(int(self.xs), int(self.ys), int(self.xs), int(self.ys + self.y_displacement))

    def draw_lines(self, qp):
        pen = QPen(Qt.black, 2, Qt.SolidLine)
        qp.setPen(pen)
        for i in range(len(self.points) - 1):
            x1, y1 = map(int, self.points[i])
            x2, y2 = map(int, self.points[i+1])
            qp.drawLine(int(x1), int(y1), int(x2), int(y2))

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
        self.feature_collection = {"type": "FeatureCollection", "features": []}
        global rot_const
        # Create a combo box to select the Bluetooth device to connect to
        self.device_combo = QComboBox()
        self.device_combo.setMaximumWidth(300)
        self.device_combo.addItems([bluetooth.lookup_name(address) for address in bluetooth.discover_devices()])

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_clicked)

        # Create a label to display the selected Bluetooth device
        self.data_recv_label = QLabel()
        self.metric_label = QLabel()

        # Create a frame for the label
        self.data_recv_frame = QFrame()
        self.data_recv_frame.setFrameShape(QFrame.WinPanel)
        self.data_recv_frame.setFrameShadow(QFrame.Sunken)
        self.data_recv_frame.setAutoFillBackground(True)

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_clicked)

        self.generate_button = QPushButton("Generate")
        self.generate_button.clicked.connect(self.generate_button_clicked)

        self.geojson_button = QPushButton("Save-GeoJSON")
        self.geojson_button.clicked.connect(self.geoJsonSave)
        self.geojson_button.setEnabled(False)

        self.viewjson_button = QPushButton("View-GeoJSON")
        self.viewjson_button.clicked.connect(self.viewGeoJSON)

        # Create a QDoubleSpinBox widget with a default value of 0.0
        self.length_const = QDoubleSpinBox()
        self.length_const.setRange(-10.0, 10.0)
        self.length_const.setSingleStep(0.01)
        self.length_const.setValue(0.17)

        self.rotation_const = QDoubleSpinBox()
        self.rotation_const.setRange(-360.0,360.0)
        self.rotation_const.setSingleStep(0.5);
        self.rotation_const.setValue(30)
        rot_const=360/self.rotation_const.value()

        constant_layout = QHBoxLayout()
        constant_layout.addWidget(QLabel("Length Const:"))
        constant_layout.addWidget(self.length_const)

        rotation_const_laout = QHBoxLayout()
        rotation_const_laout.addWidget(QLabel("Steps/Rotation:"))
        rotation_const_laout.addWidget(self.rotation_const)

        self.compensator_Switch = QPushButton('Compensator', self)
        self.compensator_Switch.setCheckable(True)
        self.compensator_Switch.move(110, 20)
        self.compensator_Switch.clicked[bool].connect(self.compensatorMode)

        settings_layout =QVBoxLayout()
        settings_layout.addWidget(self.compensator_Switch)
        settings_layout.addLayout(constant_layout)
        settings_layout.addLayout(rotation_const_laout)

        # Button UI
        self.metric_plot = MetricsWidget()
        self.metric_plot.setVisible(True)

        # Add the label to the frame
        frame_layout = QVBoxLayout()
        frame_layout.addWidget(self.data_recv_label)
        frame_layout.addWidget(self.metric_label)
        self.data_recv_frame.setLayout(frame_layout)

        # Create a layout for plotter
        self.paint_plot = DrawingWidget() 
        self.paint_plot.setVisible(True)
        
        plotLayout = QVBoxLayout()
        plotLayout.addWidget(self.paint_plot)
        plotLayout.addWidget(self.metric_plot)

        #Glwidget
        self.glWidget = GLWidget()
        # timer = QTimer(self)
        # timer.setInterval(20)   # period, in milliseconds
        # timer.timeout.connect(self.glWidget.updateGL)
        # timer.start()

        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(self.glWidget)
        buttons_layout.addWidget(QLabel("Select Bluetooth Device: "))
        buttons_layout.addWidget(self.device_combo)
        buttons_layout.addWidget(self.connect_button)

        # Add the QDoubleSpinBox widget and label to the layout
        buttons_layout.addLayout(settings_layout)

        buttons_layout.addWidget(self.generate_button)
        buttons_layout.addWidget(self.reset_button)
        buttons_layout.addWidget(self.geojson_button)
        buttons_layout.addWidget(self.viewjson_button)
        buttons_layout.addWidget(self.data_recv_frame)

        # Create a layout for the UI
        layout = QHBoxLayout()
        layout.addLayout(plotLayout, 3)
        layout.addLayout(buttons_layout, 2)     

        self.setLayout(layout)
        self.thread = None

    def viewGeoJSON(self):
        vpoints=[]
        self.feature_collection = {"type": "FeatureCollection", "features": []}
        # prompt the user to select a file to load
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(self, "Open file", "", "GeoJSON Files (*.geojson)", options=options)
        
        if filename:
            with open(filename) as f:
                data = json.load(f)

            for feature in data['features']:
                if feature['geometry']['type'] == 'Point':
                    x, y = feature['geometry']['coordinates']
                    vpoints.append((x,y))

            self.metric_plot.displayMetrics(vpoints)
            self.metric_label.setText(f"Area:{self.metric_plot.area*self.length_const.value():.2f}\nDistance:{self.metric_plot.perimeter*self.length_const.value():.2f}\nDisplacement:{self.metric_plot.displacement*self.length_const.value():.2f}\nPerimeter:{self.metric_plot.perimeter*self.length_const.value()}\nX-Displacement:{self.metric_plot.x_displacement*self.length_const.value()}\nY-Displacement:{self.metric_plot.y_displacement*self.length_const.value()}\n")

    def geoJsonSave(self):
        # create a GeoJSON feature collection object
        for point in self.metric_plot.points:
            x,y = point
            self.feature_collection['features'].append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [x, y]}})
        # prompt the user to choose a filename and location
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getSaveFileName(self, "Save file", "", "GeoJSON Files (*.geojson)", options=options)
        
        if filename:
            with open(filename, "w") as outfile:
                json.dump(self.feature_collection, outfile)
        
    def compensatorMode(self,pressed):
        global comp_mode
        if pressed:
            comp_mode=True
        else:
            comp_mode=False
        
    def generate_button_clicked(self):
        coordinates=self.paint_plot.points
        self.metric_plot.displayMetrics(coordinates)
        self.geojson_button.setEnabled(True)
    
    def connect_clicked(self):
        device_name = self.device_combo.currentText()
        
        if self.thread is not None:
            self.thread.terminate()
        self.thread = BluetoothThread(device_name,self.paint_plot,self.glWidget)
        self.thread.data_received.connect(self.data_received_text)
        self.thread.finished.connect(self.connect_finished)
        self.connect_button.setEnabled(False)
        self.thread.start()

    
    def data_received_text(self, data):
        self.data_recv_label.setText(data)
        self.metric_label.setText(f"Area:{self.metric_plot.area*self.length_const.value():.2f}\nDistance:{self.metric_plot.perimeter*self.length_const.value():.2f}\nDisplacement:{self.metric_plot.displacement*self.length_const.value():.2f}\nPerimeter:{self.metric_plot.perimeter*self.length_const.value()}\nX-Displacement:{self.metric_plot.x_displacement*self.length_const.value()}\nY-Displacement:{self.metric_plot.y_displacement*self.length_const.value()}\n")

    def connect_finished(self):
        self.connect_button.setEnabled(True)

    def reset_clicked(self):
        self.geojson_button.setEnabled(False)
        self.paint_plot.path = QPainterPath()
        self.metric_plot.path=QPainterPath()
        self.paint_plot.update()
        self.metric_plot.update()
        global x_pos, y_pos,rot_const
        x_pos = 0
        y_pos = 0
        rot_const=360/self.rotation_const.value()
        self.paint_plot.points.clear()
        self.metric_plot.points.clear()
        self.metric_plot.area=0.0
        self.metric_plot.perimeter=0.0
        self.metric_plot.xs=0.0
        self.metric_plot.xe=0.0
        self.metric_plot.ys=0.0
        self.metric_plot.ye=0.0
        self.metric_plot.x_displacement=self.metric_plot.y_displacement=0.0
        self.metric_plot.displacement=0.0
        self.feature_collection.clear()
        self.metric_label.clear()
        
    def handle_text_changed(self, text):
        self.textbox.insertPlainText(text)
        self.textbox.insertPlainText("\n")
        self.keyboard.type(text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
