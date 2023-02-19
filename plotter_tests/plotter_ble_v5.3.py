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

def draw_line(x1, y1, x2, y2):
    pygame.draw.line(screen, (255, 255, 255), (x1, y1), (x2, y2))

def draw_region(region):
    if len(region) >= 3:
        pygame.draw.polygon(screen, (255, 0, 0), region)

def intersect_line(p1, p2, q1, q2):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = q1
    x4, y4 = q2

    denominator = (y4 - y3)*(x2 - x1) - (x4 - x3)*(y2 - y1)

    if denominator == 0:
        return False

    ua = ((x4-x3)*(y1-y3)-(y4-y3)*(x1-x3))/denominator
    ub = ((x2-x1)*(y1-y3)-(y2-y1)*(x1-x3))/denominator

    if ua >= 0 and ua <= 1 and ub >= 0 and ub <= 1:
        return True

    return False


pygame.init()
screen = pygame.display.set_mode((800, 600))

running = True

region = []
prev_points = []
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
    if (x_pos, y_pos) not in prev_points:
        region.append((x_pos, y_pos))
        prev_points.append((x_pos, y_pos))
    draw_line(x_pos, y_pos, x_pos_new, y_pos_new)
    x_pos = x_pos_new
    y_pos = y_pos_new 
    pygame.display.flip()

    if len(region) >= 3:
        intersect = False
        for i in range(len(region)-2):
            for j in range(i+2, len(region)-1):
                if intersect_line(region[i], region[i+1], region[j], region[j+1]):
                    intersect = True
                    break
            if intersect:
                break
        if intersect:
            new_region = region[i+1:j+2]
            draw_region(new_region)
            region = new_region
        else:
            draw_region(region)

s.close()
pygame.quit()
