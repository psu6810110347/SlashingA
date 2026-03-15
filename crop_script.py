from PIL import Image
import os

tilemap_path = 'd:/SlashingA/images/backgrounds/ground_tiles.png'
out_path = 'd:/SlashingA/images/backgrounds/grass_tile.png'

print(f'Looking for tilemap at {tilemap_path}')
if os.path.exists(tilemap_path):
    img = Image.open(tilemap_path)
    # The actual clean grass tile in Tiny Swords is usually around (0, 0) to (64, 64)
    # But let's check if the file is even there
    print(f'Image size: {img.size}')
    grass_tile = img.crop((0, 64, 64, 128)) # Try a different tile if 0,0 was cliff
    grass_tile.save(out_path)
    print('Cropped grass tile.')
else:
    print('Tilemap not found.')
