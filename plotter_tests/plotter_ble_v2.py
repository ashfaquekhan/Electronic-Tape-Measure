import bluetooth
import socket
import struct
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math

target_name = "HC-05"
target_address = None
nearby_devices = bluetooth.discover_devices()

for bdaddr in nearby_devices:
    if target_name == bluetooth.lookup_name(bdaddr):
        target_address = bdaddr
        break

if target_address is not None:
    print ("found target bluetooth device with address ", target_address)
else:
    print ("could not find target bluetooth device nearby")

port = 1
s=socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
size = 2048
s.connect((target_address, port))

print("CONNECTED")

vertices = []
x = 0
y = 0
z = 0
r = 0

def draw_line():
    global x, y, z, r
    data = b''
    while len(data) < 8:
        data += s.recv(1)
    x, y, z, r = struct.unpack('<hhhh', data[:8])
    x = x / 100
    y = y / 100
    z = z / 100
    r = r / 1
    print(f"x={x}, y={y}, z={z} ,r={r}")
    data = data[8:]
    if r > 0:
        angle = y * math.pi / 180
        x = x + r * math.cos(angle)
        y = y + r * math.sin(angle)
        vertices.append((x, y, z))
    glBegin(GL_LINE_STRIP)
    for vertex in vertices:
        glVertex3fv(vertex)
    glEnd()

def main():
    pygame.init()
    display = (800,600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    glTranslatef(0.0,0.0, -5)
    glRotatef(0, 0, 0, 0)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        draw_line()
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == '__main__':
    main()

s.close()
