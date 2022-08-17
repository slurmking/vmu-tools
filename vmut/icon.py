"""Set of functions and tools for creating VMS icons"""
from PIL import Image, ImageOps
import math

ICONDATA_header = b'ICONDATA_VMS     \x00\x00\x00\xa0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'


def get_icon_color(colors):
    converted_color = []
    for color in colors:
        if math.ceil((color / 16) - 1) == -1:
            converted_color.append(0)
        else:
            converted_color.append(math.ceil((color / 16) - 1))
    reordered_color = (converted_color[1], converted_color[2], converted_color[3], converted_color[0])
    return tuple(reordered_color)


def get_icon_palette(image):
    palette_list = (image.convert('RGBA').getcolors())
    color_palette = []
    for color in palette_list:
        color_palette.append(get_icon_color(color[1]))
    return color_palette


def img_palette_gen(palette_bytes):
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


def img_gen(bitmap_bytes, palette_bytes, mono=False):
    """Generates VMS icon from bitmap and palette bytes"""
    icon_render = []
    palette_map = (img_palette_gen(palette_bytes))
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


class ICONDATA:

    @staticmethod
    def img_to_mono(file, invert=False, threshold=120, export=False, export_location=""):
        # converts square image to 32x32 monochrome image
        img = Image.open(file)
        maxsize = (32, 32)
        img.thumbnail(maxsize)
        image_file = img.convert('L')
        image_file = image_file.point(lambda p: 255 if p > threshold else 0)
        if invert:
            image_file = ImageOps.invert(image_file)
        image_file = image_file.convert(mode="1", dither=0)
        if export:
            image_file.save(f"{export_location}ICONDATA_mono.bmp")
        # Get color value of pixles
        pixle_grid = []
        for y in range(32):
            for x in range(32):
                if image_file.getpixel(xy=(x, y)) == 0:
                    pixle_grid.append(0)
                else:
                    pixle_grid.append(1)
        # Split data into bytes
        hex_data = []
        for chunk in range(0, 1024, 8):
            string = (pixle_grid[chunk:chunk + 8])
            hex_data.append(''.join(str(x) for x in string))

        # Convert data into byte array
        mono_bytes = bytearray()
        for byte_step in hex_data:
            mono_bytes.append((int(byte_step, 2)))
        return mono_bytes

    def img_to_icon(self, image, export=False, export_location=""):
        im = Image.open(image)
        result = im.convert('P', palette=Image.Palette.ADAPTIVE, colors=16)
        maxsize = (32, 32)
        result.thumbnail(maxsize)
        if export:
            result.save(f"{export_location}ICONDATA_color.bmp")
        # Get color value of pixles
        converted_image = result.convert('RGBA')
        palette = get_icon_palette(converted_image)
        self.palette = palette
        filler_palette = (0, 0, 15, 0)
        if len(palette) < 16:
            for x in range(16 - len(palette)):
                palette.append(filler_palette)

        # Get palette bytes
        palette_bytes = bytearray()
        for color in palette:
            palette_bytes.append(int(f"{color[0]:x}{color[1]:x}", 16))
            palette_bytes.append(int(f"{color[2]:x}{color[3]:x}", 16))
        # loop through image and find corresponding palette color

        palette_value = []
        image_bytes = bytearray()
        for y in range(32):
            for x in range(32):
                pixel_value = get_icon_color(converted_image.getpixel(xy=(x, y)))
                index = palette.index(pixel_value)
                palette_value.append(index)
        for x in range(0, 1023, 2):
            image_bytes.append(int(f"{palette_value[x]:x}{palette_value[x + 1]:x}", 16))

        image_padding = bytearray()
        for x in range(320):
            image_padding.append(26)

        return palette_bytes + image_bytes + image_padding

    """ICONDATA Object"""

    def save(self, location=""):
        with open(f"{location}ICONDATA.VMS", "wb", buffering=0) as vms_file:
            vms_file.write(self.data)

    def __init__(self, image, threshold=160, invert=False, export=False, export_location=""):
        self.palette = []
        self.mono = self.img_to_mono(image, invert, threshold, export, export_location="")
        self.img = self.img_to_icon(image, export)
        self.data = ICONDATA_header + self.mono + self.img


class Img:
    """VMS Image object"""

    @staticmethod
    def gen_img(bitmaps, palette, frames, speed, save, mono=False):
        """Generates the image from VMU bytes"""
        if frames > 1:
            gif = []
            for i in range(0, frames * 1024, 1024):
                frame = img_gen(bitmaps[i:i + 1024], palette, mono=False)
                gif.append(frame.resize((512, 512), resample=4))
                gif[0].save(f"{save}", save_all=True,
                            append_images=gif, duration=(speed / 30) * frames, loop=0)
        elif not mono:
            img_gen(bitmaps, palette, mono=False).save(save)
        else:
            img_gen(bitmaps, palette, mono=True).save(save)

    def __init__(self, bitmaps, palette, animated=False, mono=False, frames=0):
        self.frames = frames
        self.mono = mono
        self.animated = animated
        self.bitmaps = bitmaps
        self.palette = palette
