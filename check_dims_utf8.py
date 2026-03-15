from PIL import Image
import os

paths = [
    'd:/SlashingA/images/decorations/bush1.png',
    'd:/SlashingA/images/decorations/bush2.png',
    'd:/SlashingA/images/decorations/rock1.png',
    'd:/SlashingA/images/decorations/rock2.png',
    'd:/SlashingA/images/decorations/tree.png'
]

with open('d:/SlashingA/dims_utf8.txt', 'w', encoding='utf-8') as f:
    for p in paths:
        if os.path.exists(p):
            img = Image.open(p)
            f.write(f'{p}: {img.width}x{img.height}\n')
        else:
            f.write(f'{p}: Not found\n')
print('Dims written to dims_utf8.txt')
