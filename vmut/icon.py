"""Set of functions and tools for creating VMS icons"""
from PIL import Image


def palette_gen(palette_bytes):
    """Generates a list of RGBA values from palette bytes"""
    palette_list = []
    for number in range(0, 31, 2):
        palette_list.append(palette_bytes[number:number + 2])

    palette_rgb = []
    for entry in palette_list:
        bits = entry.hex()
        green = f"{bits[0]}{bits[0]}"
        blue = f"{bits[1]}{bits[1]}"
        alpha = f"{bits[2]}{bits[2]}"
        red = f"{bits[3]}{bits[3]}"
        palette_rgb.append((int(red, base=16), int(green, base=16), int(blue, base=16), int(alpha, base=16)))
    return palette_rgb


def image_gen(bitmap_bytes, palette_bytes, mono=False):
    """Generates VMS icon from bitmap and palette bytes"""
    icon_render = []
    palette_map = (palette_gen(palette_bytes))
    if not mono:
        for i, pixel in enumerate(bitmap_bytes):
            position = (i % 32, int(i / 32))
            pixel_value = (palette_map[int(str(pixel), base=16)])
            icon_render.append((position, pixel_value))
        img = Image.new('RGB', (32, 32))
    else:
        mono_bites = ""
        for bit in bitmap_bytes:
            # converts hex string into binary string
            mono_bites += ('{:04b}'.format(int(bit, base=16)))
        for i, item in enumerate(mono_bites):
            position = (i % 32, int(i / 32))
            bit = int(item)
            if bit == 0:
                pixel_value = (143, 205, 175)
            else:
                pixel_value = (8, 20, 128)
            icon_render.append((position, pixel_value))
        img = Image.new('RGB', (32, 32))
    for line in icon_render:
        img.putpixel(line[0], line[1])
    img = img.resize((512, 512), resample=4)
    return img


class Icon:
    """VMS Icon object"""

    @staticmethod
    def gen(bitmaps, palette, frames, speed, save, mono=False):
        "Generates the image from VMU bytes"
        if frames > 1:
            gif = []
            for i in range(0, frames * 1024, 1024):
                frame = image_gen(bitmaps[i:i + 1024], palette, mono=False)
                gif.append(frame.resize((512, 512), resample=4))
                gif[0].save(f"{save}.gif", save_all=True,
                            append_images=gif, duration=(speed / 30) * frames, loop=0)
        elif not mono:
            image_gen(bitmaps, palette, mono=False).save(save)
        else:
            image_gen(bitmaps, palette, mono=True).save(save)

    def __init__(self, bitmaps, palette, animated=False, mono=False, frames=0):
        self.frames = frames
        self.mono = mono
        self.animated = animated
        self.bitmaps = bitmaps
        self.palette = palette
