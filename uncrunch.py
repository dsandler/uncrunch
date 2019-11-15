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

class Log(object):
  def __init__(self, _indent=0):
    self._indent = _indent
  def log(self, *args):
    sys.stdout.write("  " * self._indent)
    sys.stdout.write("".join(args))
    sys.stdout.write("\n")
  def indent(self, num=1):
    self._indent += num
  def dedent(self, num=1):
    self._indent -= num
  def indented(self, num=1):
    return Log(self._indent + num)
  def __exit__(self, a, b, c): pass
  def __enter__(self):
    return self

def extractBitmapData(path, log=Log()):
  buf = memoryview(open(path, 'rb').read())
  log.log("extractBitmapData: read %d bytes from %s" % (len(buf), path))
  i = 0
  width = struct.unpack_from(INT32_PACK, buf)[0]
  height = struct.unpack_from(INT32_PACK, buf[4:8])[0]

  log.log("extractBitmapData: %d (%x) x %d (%x)" % (width, width, height, height))

  log.log("extractBitmapData: flag byte: %x" % ord(buf[8]))

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
    log.log("extractBitmapData: " + repr(e))
  except IOError, e:
    log.log("extractBitmapData: " + repr(e))

  return (bitmap[0:pixi], width, height)

"baz"

def processDatafile(dataFile, outdir, log):
  bitmap, bitWidth, bitHeight = extractBitmapData(dataFile, log)

  name = os.path.splitext(dataFile)[0]

  rawfile = os.path.join(outdir, name + ".raw")
  if not os.path.exists(os.path.dirname(rawfile)):
    os.makedirs(os.path.dirname(rawfile))
  open(rawfile, 'wb').write(bitmap)
  log.log("wrote texture (%dx%d) to %s" % (bitWidth, bitHeight, rawfile))

  if png:
    try:
      pngfile = os.path.join(outdir, name + ".png")
      png.from_array([bitmap[i*bitWidth*4:(i+1)*bitWidth*4] for i in range(bitHeight)],
        mode='RGBA',
        info=dict(
          height=bitHeight,
          width=bitWidth)).write(open(pngfile, 'wb'))
      log.log("wrote PNG to " + pngfile)
    except Exception, e:
      log.log("error writing PNG: " + repr(e))

"bar"

def processMetafile(path, outdir, log):
  if path.endswith(".meta"):
    metafile = path
    path = os.path.dirname(path)
  else:
    metafile = path + ".meta"

  name = os.path.splitext(metafile)[0]
  monolithicDataFile = name + ".data"
  if os.path.exists(monolithicDataFile):
    log.log("using monolithic datafile: " + monolithicDataFile)
  else:
    monolithicDataFile = None
    if not (os.path.exists(path) and os.path.isdir(path)):
      log.log("warning: not an asset directory: " + path)

  if not (os.path.exists(metafile)):
    raise Exception("error: missing metafile: " + metafile)

  infile = open(metafile, 'rb')

  infile.read(4) #skip
  read_string(infile) #skip
  infile.read(4)
  num = read_uint16(infile)

  log.log("%s (%d textures)" % (path, num))

  for i in range(num):
    with log.indented() as log:
      path3 = read_string(infile)
      path4 = os.path.join(path, path3)
      num2 = read_uint16(infile)
      log.log("%s (%d)" % (path3, num2))
      for j in range(num2):
        with log.indented() as log:
          text3 = read_string(infile).replace('\\', '/')
          x = read_uint16(infile)
          y = read_uint16(infile)
          w1 = read_uint16(infile)
          h1 = read_uint16(infile)
          num7 = read_uint16(infile)
          num8 = read_uint16(infile)
          frameWidth = read_uint16(infile)
          frameHeight = read_uint16(infile)

          log.log("[%d,%d] texture %s: %dx%d@%d,%d" % (i, j, text3,
            frameWidth, frameHeight, x, y))

          dataFile = os.path.join(path, text3 + ".data")
          # TODO(dsandler): monolithicDataFile

          processDatafile(dataFile, outdir=outdir, log=log)

"foo"

def main(argv):
  ap = argparse.ArgumentParser()
  ap.add_argument('-o', '--output', default='.', help='Output directory')
  ap.add_argument('targets', nargs='+')
  args = ap.parse_args()

  log = Log()

  for d in args.targets:
    if d.endswith(".meta") or os.path.isdir(d):
      processMetafile(d, outdir=args.output, log=log)
    elif d.endswith(".data"):
      processDatafile(d, outdir=args.output, log=log)
    else:
      log.log("error: unrecognized file input: " + d)

if __name__ == '__main__':
  sys.exit(main(sys.argv))
