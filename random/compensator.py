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

pygame.init()
screen = pygame.display.set_mode((800, 600))

running = True
rot_en=True
rot_en_in=False
in_pitch=0
prev_pitch=0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    data = b''
    while len(data) < 8:
        data += s.recv(1)
    yaw, roll, pitch, rot = struct.unpack('<hhhh', data[:8])
    pitch=pitch/100
    y_value = yaw/100 
    r_value = rot/1
    
    if(rot_en_in and rot):
        r_value= int(rot/1+((pitch-prev_pitch)/12))
        rot_en=False

    print(f"Rot={rot/1} | r_Value={r_value} | pitch={pitch} | p_prev={prev_pitch}")
    data=data[8:]
    x_pos_new = x_pos + r_value * math.cos(math.radians(y_value)) 
    y_pos_new = y_pos + r_value * math.sin(math.radians(y_value))

    prev_pitch=pitch
    
    draw_line(x_pos, y_pos, x_pos_new, y_pos_new)
    x_pos = x_pos_new
    y_pos = y_pos_new 
    if(rot and rot_en):
        rot_en_in=True
    

    pygame.display.flip()

s.close()
pygame.quit()
