from PIL import Image
import os

paths = [
    'd:/SlashingA/images/decorations/bush1.png',
    'd:/SlashingA/images/decorations/bush2.png',
    'd:/SlashingA/images/decorations/rock1.png',
    'd:/SlashingA/images/decorations/rock2.png',
    'd:/SlashingA/images/decorations/tree.png'
]

for p in paths:
    if os.path.exists(p):
        img = Image.open(p)
        print(f'{p}: {img.width}x{img.height}')
    else:
        print(f'{p}: Not found')
