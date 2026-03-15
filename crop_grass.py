from PIL import Image
import os

tilemap_path = 'd:/SlashingA/images/backgrounds/ground_tiles.png'
out_path = 'd:/SlashingA/images/backgrounds/grass_tile.png'

if os.path.exists(tilemap_path):
    img = Image.open(tilemap_path)
    # Crop a middle grass tile [64,64 to 128,128] which is usually more seamless
    # Tiny Swords: Tile at (1,1) in 8x8 grid of 64px tiles
    grass_tile = img.crop((64, 64, 128, 128))
    grass_tile.save(out_path)
    print('Cropped seamless grass tile.')
else:
    print('Tilemap not found.')
