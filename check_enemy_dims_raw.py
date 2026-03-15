import struct
import os

def get_image_info(data):
    w, h = struct.unpack('>LL', data[16:24])
    return int(w), int(h)

files = [
    "d:/SlashingA/images/enemy/normal.png",
    "d:/SlashingA/images/enemy/tank.png",
    "d:/SlashingA/images/enemy/shooter.png"
]

for f in files:
    if os.path.exists(f):
        with open(f, 'rb') as fp:
            data = fp.read(24)
            w, h = get_image_info(data)
            print(f"{os.path.basename(f)}: {w}x{h}")
    else:
        print(f"{f} not found")
