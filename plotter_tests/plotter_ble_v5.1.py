import bluetooth
import struct
import socket
import pygame
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

d="0"
s.send(d.encode())

x_pos = 400
y_pos = 300
r_value = 0
y_value = 0
previous_points = []
area = 0

def draw_line(x1, y1, x2, y2):
    pygame.draw.line(screen, (255, 255, 255), (x1, y1), (x2, y2))

def calculate_area(points):
    area = 0
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        area += (x1 * y2 - x2 * y1)
    return abs(area / 2)

pygame.init()
screen = pygame.display.set_mode((800, 600))

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    data = b''
    while len(data) < 8:
        data += s.recv(1)
    y, _, _, r = struct.unpack('<hhhh', data[:8])
    y_value = y/100 
    r_value = r/1 
    print(f"y={y/100},r={r/1}")
    data=data[8:]
    x_pos_new = x_pos + r_value * math.cos(math.radians(y_value)) 
    y_pos_new = y_pos + r_value * math.sin(math.radians(y_value))
    
    if previous_points and (x_pos_new, y_pos_new) == previous_points[-1]:
        print(f"Area: {area}")
        distance = math.sqrt((x_pos_new - previous_points[0][0])**2 + (y_pos_new - previous_points[0][1])**2)
        displacement = math.sqrt((x_pos_new - x_pos)**2 + (y_pos_new - y_pos)**2)
        print(f"Distance: {distance}")
        print(f"Displacement: {displacement}")
    else:
        draw_line(x_pos, y_pos, x_pos_new, y_pos_new)
        previous_points.append((x_pos, y_pos))
        area = calculate_area(previous_points)
    
    x_pos = x_pos_new
    y_pos = y_pos_new 
    pygame.display.flip()

s.close()
pygame.quit()
