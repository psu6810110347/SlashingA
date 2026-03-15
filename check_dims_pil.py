from PIL import Image
import os

files = [
    "d:/SlashingA/images/enemy/normal_attack.png",
    "d:/SlashingA/images/enemy/tank_attack.png",
    "d:/SlashingA/images/enemy/shooter_attack.png",
    "d:/SlashingA/images/enemy/normal_idle.png",
    "d:/SlashingA/images/enemy/tank_idle.png",
    "d:/SlashingA/images/enemy/shooter_idle.png",
    "d:/SlashingA/images/enemy/normal.png",
    "d:/SlashingA/images/enemy/tank.png",
    "d:/SlashingA/images/enemy/shooter.png"
]

for f in files:
    if os.path.exists(f):
        with Image.open(f) as img:
            w, h = img.size
            print(f"{os.path.basename(f)}: {w}x{h}")
    else:
        print(f"{f} not found")
