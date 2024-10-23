from PIL import Image
import os
import ntpath
import numpy as np
from skimage.metrics import peak_signal_noise_ratio as psnrFunction
from lsb import codeExampleMessage, convertImage, lsbDecoding, convertToString

def nameOfTheStegoImage(path):
    _, tail = ntpath.split(path)
    img = Image.open(path)
    print(tail, img.size)
    if tail.endswith(('jpg')): 
        tail = tail[:-4] + '.png'
    stego_name = 'STEGO_' + tail
    return stego_name


def imageInfo(input_path):
    img = Image.open(input_path)
    print(img.filename, img.size)


def mse(original_image, stego_image):
    original_image = np.array(original_image)
    stego_image = np.array(stego_image)

    value = np.sum((original_image.astype("float") - stego_image.astype("float")) ** 2)
    value /= float(original_image.shape[0] * original_image.shape[1])
    return value

def psnr(original_image, stego_image):
    original_image = np.array(original_image)
    stego_image = np.array(stego_image)

    psnr_value = psnrFunction(original_image, stego_image, data_range=stego_image.max() - stego_image.min())
    return psnr_value



def processImagesInFolder(input_folder, output_folder):
    for filename in os.listdir(input_folder):
        if filename.endswith(('.png', 'jpg')): 
            input_path = os.path.join(input_folder, filename)
            image, _ = convertImage(input_path)
            stego_image_name = nameOfTheStegoImage(input_path)
            stego_image = codeExampleMessage(input_path)
            output_path = os.path.join(output_folder, stego_image_name)
            stego_image.save(output_path)
            mess = lsbDecoding(output_path)
            print(convertToString(mess))
            mse_value = mse(image, stego_image)
            psnr_value = psnr(image, stego_image)
            print("MSE: ", mse_value, '\nPSNR: ', psnr_value)

def canWeReadMessage(stego_folder):
    for filename in os.listdir(stego_folder):
        if filename.endswith(('.png', '.jpg')):
            path = os.path.join(stego_folder, filename)
            img = Image.open(path)
            print("________________", filename, "__________________", img.size)
            try:
                mess = lsbDecoding(path)
                print(convertToString(mess))
            except ValueError:
                print("We can't read message on this image.")




if __name__ == '__main__':
    input_folder = 'D:\STUDIA\Cyberka\Inzynierka\Zbior_obrazow' 
    output_folder = 'D:\STUDIA\Cyberka\Inzynierka\Zbior_Stego'
    facebook_folder = 'D:\STUDIA\Cyberka\Inzynierka\Zbior_Facebook\Folder'
    # processImagesInFolder(input_folder, output_folder)
    canWeReadMessage(facebook_folder)
