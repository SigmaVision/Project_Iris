from PIL import Image

img = Image.open('bee.jpg')
img.show()
new_image = img.copy()
new_image.show()
