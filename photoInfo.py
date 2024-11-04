from PIL import Image
import os
import sys
import ntpath
import xlsxwriter
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
    _, tail = ntpath.split(input_path)
    img = Image.open(input_path)
    print(tail, ': ', img.size, img.height, img.width)
    return tail, img.size


def mse(original_image, stego_image):
    original_image = np.array(Image.open(original_image))
    stego_image = np.array(Image.open(stego_image))

    value = np.sum((original_image.astype("float") - stego_image.astype("float")) ** 2)
    value /= float(original_image.shape[0] * stego_image.shape[1])
    return value

def psnr(original_image, stego_image):
    original_image = np.array(Image.open(original_image))
    stego_image = np.array(Image.open(stego_image))

    psnr_value = psnrFunction(original_image, stego_image, data_range=stego_image.max() - stego_image.min())
    return psnr_value


#  na podstawie: https://medium.com/@thusharabandara/measure-the-compression-performance-of-an-image-compression-algorithm-ea68c1839ec6
def compression_ratio(original, encoded):
    original_size = os.path.getsize(original)
    encoded_size = os.path.getsize(encoded)
    return (encoded_size) / (original_size)



def processImagesInFolder(input_folder, output_folder):
    for filename in os.listdir(input_folder):
        if filename.endswith(('.png', 'jpg', '.bmp', '.gif')): 
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


def changeNames(input_folder):
    png = 1
    jpg = 1
    bmp = 1
    gif = 1
    for filename in os.listdir(input_folder):
        if filename.endswith(('.pnga', 'jpga', '.bmpa', '.gifa')):
            if filename.endswith(('.pnga')):
                new_name = '\PNG_'+str(png)
                end = '.png'
                png += 1
            elif filename.endswith(('.jpga')):
                new_name = '\JPG_'+str(jpg)
                end = '.jpg'
                jpg += 1
            elif filename.endswith(('.bmpa')):
                new_name = '\BMP_'+str(bmp)
                end = '.bmp'
                bmp += 1
            elif filename.endswith(('.gifa')):
                new_name = '\GIF_'+str(gif)
                end = '.gif'
                gif += 1
            input_path = input_folder + '\\' + filename
            output_path = input_folder + new_name + end
            try:
                os.rename(input_path, output_path)    
            except FileExistsError:
                output_path = input_folder + new_name + 'a' + end
                os.rename(input_path, output_path)


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


def compareImages(before_folder, after_folder, worksheet):
    scores = []
    for filename in os.listdir(after_folder):
        before_img = os.path.join(before_folder, filename)
        after_img = os.path.join(after_folder, filename)
        print("-------------------------------------------------------")
        name_be, size_be = imageInfo(before_img)
        _, size_af = imageInfo(after_img)
        cr_value = compression_ratio(before_img, after_img)
        print("CR: ", cr_value)
        mse_value = False
        psnr_value = False
        try:
            mse_value = mse(before_img, after_img)
            print("MSE: ", mse_value)
        except ValueError:
            print("Nie ten sam rozmiar.")
        
        if mse_value:
            if mse_value == 0.0:
                print('PSNR: infinity')
                psnr_value = 'inf'
            else:
                try:
                    psnr_value = psnr(before_img, after_img)
                    print("PSNR: ", psnr_value)
                except ValueError:
                    pnsr_value = '-'
                    print("Nie ten sam rozmiar. ")
        score = [name_be, size_be, size_af, cr_value, mse_value, psnr_value]
        scores.append(score)
    
    row = 0
    col = 0
    for name, size1, size2, vcr, vmse, vpsnr in scores:
        worksheet.write(row, col, name)
        worksheet.write(row, col+1, str(size1))
        worksheet.write(row, col+2, str(size2))
        worksheet.write(row, col+3, vcr)
        worksheet.write(row, col+4, vmse)
        worksheet.write(row, col+5, vpsnr)
        row += 1
    
    





if __name__ == '__main__':
    workbook = xlsxwriter.Workbook('Wyniki.xlsx')
    worksheet = workbook.add_worksheet("My sheet")
    input_folder = 'D:\STUDIA\Cyberka\Inzynierka\Zbior_obrazow' 
    output_folder = 'D:\STUDIA\Cyberka\Inzynierka\Zbior_Stego'
    facebook_folder = 'D:\STUDIA\Cyberka\Inzynierka\Zbior_Facebook'
    after_folder = 'D:\STUDIA\Cyberka\Inzynierka\Facebook_bez_info'
    # processImagesInFolder(input_folder, output_folder)
    # canWeReadMessage(facebook_folder)
    # changeNames(input_folder)
    compareImages(input_folder, after_folder, worksheet)
    workbook.close()