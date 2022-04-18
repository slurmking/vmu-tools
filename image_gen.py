from PIL import Image
import re
colorRender = []
bnwRender = []

def palletGetColor(input):
    bits = input.hex()
    green = f"{bits[0]}{bits[0]}"
    blue = f"{bits[1]}{bits[1]}"
    alpha = f"{bits[2]}{bits[2]}"
    red = f"{bits[3]}{bits[3]}"
    return (int(red, base=16), int(green, base=16), int(blue, base=16))


def colorGen(colorImage,pallet,save):
    for i, pixel in enumerate(colorImage.hex()):
        position = (i % 32, int(i / 32))
        colorMap = int(str(pixel), base=16)
        pixelValue = (position, pallet[colorMap])
        colorRender.append(pixelValue)
    img = Image.new('RGB', (32, 32))
    for line in colorRender:
        img.putpixel(line[0],line[1])
    # img.save(f'{save}.png')
    bigImg = img.resize((512,512),resample=4)
    # bigImg.save(f'{save}.png')
    return bigImg


def bnwGen(bits, save):
    for i, value in enumerate(bits):
        position = (i % 32, int(i / 32))
        value = int(value)
        if value == 0:
            color = (143, 205, 175)
        else:
            color = (8,20,128)
        pixelValue = (position, color)
        bnwRender.append(pixelValue)
    img = Image.new('RGB', (32, 32))
    for line in bnwRender:
        img.putpixel(line[0],line[1])
    # img.save('bnw.png')
    bigImg = img.resize((512,512),resample=4)
    bigImg.save(f'{save}bnw.png')
    return bigImg
def animatedGen(bitmaps,pallet,frames,save,speed):
    save = re.sub(r'\W+', '', save)
    save.strip("/")
    palletList = []
    hashCheck = []
    for x in range(0, 31, 2):
        palletList.append(palletGetColor(pallet[x:x + 2]))
    if frames > 1:
        gif = []
        for i in range(0, frames * 512, 512):
            frame = colorGen(bitmaps[i:i + 512], palletList,f"{save}")
            gif.append(frame.resize((512,512),resample=4))
            gif[0].save(f"{save}.gif", save_all=True,
                             append_images=gif, duration=(speed/30)*frames, loop=0)
    else:
        colorGen(bitmaps, palletList,save).save(f'{save}.png')



