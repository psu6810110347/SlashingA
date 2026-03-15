import struct
import os

def get_image_info(data):
    w, h = struct.unpack('>LL', data[16:24])
    return int(w), int(h)

files = [
    "d:/SlashingA/images/enemy/normal_attack.png",
    "d:/SlashingA/images/enemy/tank_attack.png",
    "d:/SlashingA/images/enemy/shooter_attack.png",
    "d:/SlashingA/images/enemy/normal_idle.png",
    "d:/SlashingA/images/enemy/tank_idle.png",
    "d:/SlashingA/images/enemy/shooter_idle.png"
]

for f in files:
    if os.path.exists(f):
        with open(f, 'rb') as fp:
            data = fp.read(24)
            w, h = get_image_info(data)
            print(f"{os.path.basename(f)}: {w}x{h}")
    else:
        print(f"{f} not found")
