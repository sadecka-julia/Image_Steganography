from PIL import Image
import os
from skimage.metrics import peak_signal_noise_ratio as psnr
from skimage.metrics import mean_squared_error as mse

def imageInfo(input_path):
    img = Image.open(input_path)
    print(img.filename, img.size)


def process_images_in_folder(input_folder):
    for filename in os.listdir(input_folder):
        if filename.endswith(('.png', '.jpg', '.jpeg')): 
            input_path = os.path.join(input_folder, filename)
            imageInfo(input_path)


if __name__ == '__main__':
    input_folder = 'D:\STUDIA\Cyberka\Inzynierka\Zbior_obrazow' 
    process_images_in_folder(input_folder)
