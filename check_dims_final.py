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

results = []
for f in files:
    if os.path.exists(f):
        img = Image.open(f)
        w, h = img.size
        results.append(f"{os.path.basename(f)},{w},{h}")
    else:
        results.append(f"{os.path.basename(f)},0,0")

with open("d:/SlashingA/dims_final.txt", "w") as f:
    f.write("\n".join(results))
