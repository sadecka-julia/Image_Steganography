from PIL import Image

# Otworzenie obrazu - trzeba dać całą ścieżkę do pliku
image = Image.open('d:/STUDIA/Cyberka/Inzynierka/Proby/photo.jpg')

# alternative way to import an image
# with Image.open('d:/STUDIA/Cyberka/Inzynierka/Proby/photo.jpg') as image:
#     image.show()

# create a new image from scratch
createdImage = Image.new('RGBA', (1000,600))

# show the picture
# image.show()
# createdImage.show()

# saving the picture
# createdImage.save('test_save.png')

# image information
# print(image.size)
# print(image.filename)
# print(image.format)
# print(image.format_description)

# podstawowe modyfikacje
rotate = image.rotate(60, expand= True, fillcolor=(100, 20, 30))
# fillcolor = ImageColor.getcolor('red', 'RGB')
image_crop = image.crop((0, 0, 800, 1300))
# image_crop = image.crop(left_x, top_y, right_x, bottom_y)
# flip
image_flip = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
# FLIP_TOP_BOTTOM, TRANSPOSE
# resize
image_resize = image.resize((300, 1000))
new_image_size = (image.size[0] * 2, image.size[1] * 2)
image_resize_better = image.resize(new_image_size)


# image.show()
# rotate.show()
# image_crop.show()
# image_flip.show()
# image_resize.show()
image_resize_better.show()