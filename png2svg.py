import svgwrite
from PIL import Image
import sys

if len(sys.argv) != 3:
    print('Requires two arguments, source and destination file names')
    sys.exit(1)

source = sys.argv[1]
destination = sys.argv[2]

im = Image.open(source, 'r')
width, height = im.size

pixel_values = list(im.getdata())

print(len(pixel_values))

dwg = svgwrite.Drawing(filename=destination, size=(width, height), profile='tiny')

for y in range(height):
    for x in range(width):
        pixel = pixel_values[x + y * width]

        if pixel[3] == 0:
            continue
        dwg.add(dwg.rect((x, y), (1, 1), fill='rgb(%d,%d,%d)' % pixel[:3]))

dwg.save()
