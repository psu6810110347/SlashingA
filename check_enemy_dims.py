from kivy.core.image import Image as CoreImage
import os

files = [
    "d:/SlashingA/images/enemy/normal.png",
    "d:/SlashingA/images/enemy/tank.png",
    "d:/SlashingA/images/enemy/shooter.png"
]

for f in files:
    if os.path.exists(f):
        img = CoreImage(f).texture
        print(f"{os.path.basename(f)}: {img.width}x{img.height}")
    else:
        print(f"{f} not found")
