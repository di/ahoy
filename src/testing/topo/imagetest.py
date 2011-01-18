import Image

size = (100,100)
img = Image.new('RGB', size)
pixels = img.load()

for i in range(img.size[0]):
    for j in range(img.size[1]):
            pixels[i,j] = (i, j, 100)

img.save('out.png')
