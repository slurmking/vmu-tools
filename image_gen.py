"""tools to read and generate images from vms icons"""
import re
from PIL import Image


color_render = []
bnw_render = []


def palette_get_color(palette):
    """generates RGB string from VMS palette"""
    bits = palette.hex()
    green = f"{bits[0]}{bits[0]}"
    blue = f"{bits[1]}{bits[1]}"
    alpha = f"{bits[2]}{bits[2]}"
    red = f"{bits[3]}{bits[3]}"
    return (int(red, base=16), int(green, base=16), int(blue, base=16))


def color_gen(color_image, pallet):
    """Generates color image from VMS"""
    for i, pixel in enumerate(color_image.hex()):
        position = (i % 32, int(i / 32))
        color_map = int(str(pixel), base=16)
        pixel_value = (position, pallet[color_map])
        color_render.append(pixel_value)
    img = Image.new('RGB', (32, 32))
    for line in color_render:
        img.putpixel(line[0], line[1])
    big_img = img.resize((512, 512), resample=4)
    return big_img


def bnw_gen(bits, save):
    """Generates image from black and white icon"""
    for i, value in enumerate(bits):
        position = (i % 32, int(i / 32))
        value = int(value)
        if value == 0:
            color = (143, 205, 175)
        else:
            color = (8, 20, 128)
        pixel_value = (position, color)
        bnw_render.append(pixel_value)
    img = Image.new('RGB', (32, 32))
    for line in bnw_render:
        img.putpixel(line[0], line[1])
    # img.save('bnw.png')
    big_img = img.resize((512, 512), resample=4)
    big_img.save(f'{save}bnw.png')
    return big_img


def animated_gen(bitmaps, pallet, frames, save, speed):
    """Generates gif from VMS frames"""
    save = re.sub(r'\W+', '', save)
    save.strip("/")
    pallet_list = []
    for number in range(0, 31, 2):
        pallet_list.append(palette_get_color(pallet[number:number + 2]))
    if frames > 1:
        gif = []
        for i in range(0, frames * 512, 512):
            frame = color_gen(bitmaps[i:i + 512], pallet_list)
            gif.append(frame.resize((512, 512), resample=4))
            gif[0].save(f"{save}.gif", save_all=True,
                        append_images=gif, duration=(speed / 30) * frames, loop=0)
    else:
        color_gen(bitmaps, pallet_list).save(f'{save}.png')
