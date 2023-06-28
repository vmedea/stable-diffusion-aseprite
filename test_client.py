#!/usr/bin/env python3
import sys

import websocket
from PIL import Image

def colorize(fg, bg, glyph):
    sgr = []
    sgr.extend([38, 2, fg[0], fg[1], fg[2]] if fg is not None else [39])
    sgr.extend([48, 2, bg[0], bg[1], bg[2]] if bg is not None else [49])
    sgr_str = ';'.join(str(item) for item in sgr)
    return f'\x1b[{sgr_str}m{glyph}\x1b[0m'

def from_image(img):
    '''
    Return image converted to terminal grid (half-height).
    '''
    lines = []
    for y in range(0, img.height, 2):
        line = []
        for x in range(img.width):
            rgb1 = img.getpixel((x, y))
            try: # could be out of range if image has odd number of rows, pad with terminal default in that case
                rgb2 = img.getpixel((x, y + 1))
            except IndexError:
                rgb2 = None
            line.append(colorize(rgb1, rgb2, '▀'))
        lines.append(''.join(line))
    return '\n'.join(lines)

def bool_str(x):
    if x:
        return 'true'
    else:
        return 'false'

def main():
    ws = websocket.WebSocket()
    ws.connect("ws://127.0.0.1:8765")
    device = 'cuda'
    precision = 'autocast'
    #precision = 'float'
    optimized = False # true makes it much slower
    prompt = sys.argv[1]
    negative = "muted, dull, hazy, muddy colors, blurry, mutated, deformed, noise, stock image, borders, watermark, text"
    width = 512
    height = 512
    dpath = "./"
    model = "model.pxlm"
    pixel = True
    steps = 20
    scale = 7.0
    seed = 3
    num_iter = 1
    tilingx = False
    tilingy = False

    ws.send("load{ddevice}" + device + "{doptimized}" + bool_str(optimized) + "{dprecision}" + precision + "{dpath}" + dpath + "{dmodel}" + model + "{end}")
    while True:
        msg = ws.recv()
        print(msg)
        if msg == 'loaded model':
            break

    ws.send("txt2img{dpixel}" + bool_str(pixel) + "{ddevice}" + device + "{dprecision}" + precision + "{dprompt}" + prompt + "{dnegative}" + negative + "{dwidth}" + str(width) + "{dheight}" + str(height) + "{dstep}" + str(steps) + "{dscale}" + str(scale) + "{dseed}" + str(seed) + "{diter}" + str(num_iter) + "{dtilingx}" + bool_str(tilingx) + "{dtilingy}" + bool_str(tilingy) + "{end}")
    while True:
        msg = ws.recv()
        print(msg)
        if msg == 'returning txt2img':
            break
        if msg == 'returning error':
            sys.exit(1)

    ws.close()

    i = Image.open("temp/temp.png")
    print(from_image(i))
    print()

if __name__ == '__main__':
    main()
