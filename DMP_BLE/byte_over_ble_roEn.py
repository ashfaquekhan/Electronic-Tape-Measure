import bluetooth 
target_name = "HC-05"
target_address = None
import socket
import struct

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
# sock=bluetooth.BluetoothSocket(bluetooth.RFCOMM)
s=socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
size = 2048
s.connect((target_address, port))
# sock.connect((target_address, port))
print("CONNECTED")
while True:
    data = b''
    while len(data) < 8:
        data += s.recv(1)
    x, y, z, r = struct.unpack('<hhhh', data[:8])
    # print(f"raw data={data} : x={x/100}, y={y/100}, z={z/100}")
    print(f"x={x/100}, y={y/100}, z={z/100} ,r={r/1}")
    data = data[8:]
