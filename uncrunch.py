#!/usr/bin/env python3

import argparse
import struct
import sys
import os

try:
  import png
except:
  png = None

INT16_PACK="<h"
INT16_LEN = struct.calcsize(INT16_PACK)

UINT16_PACK="<H"
UINT16_LEN = struct.calcsize(UINT16_PACK)

INT32_PACK="<l"
INT32_LEN = struct.calcsize(INT32_PACK)

UINT32_PACK="<L"
UINT32_LEN = struct.calcsize(UINT32_PACK)

def read_7bitint(infile):
  n = 0
  n2 = 0
  while True:
    if (n2 == 35): raise Exception("invalid 7bit int")
    b = ord(infile.read(1))
    n |= (b & 0x7F) << n2
    n2 += 7
    if ((b & 0x80) == 0): break
  return n

def read_string(infile):
  n = read_7bitint(infile)
  if n == 0: return ""
  return infile.read(n)

def read_uint16(infile):
  return struct.unpack(UINT16_PACK, infile.read(UINT16_LEN))[0]

def loadTextureFile(path):
  buf = memoryview(open(path, 'rb').read())
  print("loadTextureFile: read %d bytes from %s" % (len(buf), path))
  i = 0
  width = struct.unpack_from(INT32_PACK, buf)[0]
  height = struct.unpack_from(INT32_PACK, buf[4:8])[0]

  print("loadTextureFile: %d (%x) x %d (%x)" % (width, width, height, height))

  print("loadTextureFile: flag byte: %x" % ord(buf[8]))

  flag = ord(buf[8]) == 1 # has alpha
  i += 9
  size = width * height * 4

  bitmapsize = size #67108864  # another magic number?
  bitmap = bytearray(bitmapsize)
  pixi = 0
  try:
    while pixi < bitmapsize:
      rle = ord(buf[i]) * 4
      i += 1
      if (flag):
        if ord(buf[i]) > 0:
          bitmap[pixi:pixi+4] = bytearray([buf[i+3], buf[i+2], buf[i+1], buf[i+0]])
          i += 4
        else:
          bitmap[pixi:pixi+4] = bytearray([0,0,0,0])
          i += 1
      else:
        bitmap[pixi:pixi+4] = bytearray([buf[i+2], buf[i+1], buf[i+0], 0xFF])
        i += 3
      if rle > 4:
        j = pixi+4
        while j < rle+pixi:
          bitmap[j:j+4] = bytearray(bitmap[pixi:pixi+4])
          j += 4
      pixi += rle
  except IndexError, e:
    print("loadTextureFile: " + repr(e))
  except IOError, e:
    print("loadTextureFile: " + repr(e))

  return (bitmap[0:pixi], width, height)


def process(path, outdir):
  if not (os.path.exists(path) and os.path.isdir(path)):
    raise Exception("error: not an asset directory: " + path)

  metafile = path + ".meta"
  if not (os.path.exists(metafile)):
    raise Exception("error: missing metafile: " + metafile)

  infile = open(metafile, 'rb')

  infile.read(4) #skip
  read_string(infile) #skip
  infile.read(4)
  num = read_uint16(infile)

  print("[" + path + "]")

  for i in range(num):
    path3 = read_string(infile)
    path4 = os.path.join(path, path3)
    num2 = read_uint16(infile)
    for j in range(num2):
      text3 = read_string(infile).replace('\\', '/')
      x = read_uint16(infile)
      y = read_uint16(infile)
      w1 = read_uint16(infile)
      h1 = read_uint16(infile)
      num7 = read_uint16(infile)
      num8 = read_uint16(infile)
      frameWidth = read_uint16(infile)
      frameHeight = read_uint16(infile)

      textureFile = os.path.join(path, text3 + ".data")

      print("  [%d,%d] texture %s: %d x %d" % (i, j, text3, frameWidth, frameHeight))

      bitmap, bitWidth, bitHeight = loadTextureFile(textureFile)

      rawfile = os.path.join(outdir, text3 + ".raw")
      if not os.path.exists(os.path.dirname(rawfile)):
        os.makedirs(os.path.dirname(rawfile))
      open(rawfile, 'wb').write(bitmap)
      print("  wrote texture (%dx%d) to %s" % (bitWidth, bitHeight, rawfile))

      if png:
        try:
          pngfile = os.path.join(outdir, text3 + ".png")
          png.from_array([bitmap[i*bitWidth*4:(i+1)*bitWidth*4] for i in range(bitHeight)],
            mode='RGBA',
            info=dict(
              height=bitHeight,
              width=bitWidth)).write(open(pngfile, 'wb'))
          print("wrote PNG to " + pngfile)
        except Exception, e:
          print("error writing PNG: " + repr(e))

def main(argv):
  ap = argparse.ArgumentParser()
  ap.add_argument('-o', '--output', default='.', help='Output directory')
  ap.add_argument('dirs', nargs='+')
  args = ap.parse_args()

  for d in args.dirs:
    process(d, outdir=args.output)

if __name__ == '__main__':
  sys.exit(main(sys.argv))
