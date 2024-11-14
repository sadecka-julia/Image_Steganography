from PIL import Image
import os
import sys
import ntpath
import xlsxwriter
import numpy as np
from skimage.metrics import peak_signal_noise_ratio as psnrFunction
from lsb import codeExampleMessage, convertImage, lsbDecoding, convertToString
from dct import codeExampleMessageDCT
from readDCT import dctDecoding, convertToStringDCT

def nameOfTheStegoImage(path):
    _, tail = ntpath.split(path)
    img = Image.open(path)
    print(tail, img.size)
    if tail.endswith(('jpg')): 
        tail = tail[:-4] + '.png'
    # stego_name = 'STEGO_' + tail
    stego_name = tail
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
            # image, _ = convertImage(input_path)
            stego_image_name = nameOfTheStegoImage(input_path)
            stego_image = codeExampleMessage(input_path)
            output_path = os.path.join(output_folder, stego_image_name)
            stego_image.save(output_path)
            mess = lsbDecoding(output_path)
            print(convertToString(mess))
            # mse_value = mse(image, stego_image)
            # psnr_value = psnr(image, stego_image)
            # print("MSE: ", mse_value, '\nPSNR: ', psnr_value)


def makeStegoImageLSB(input_folder, output_folder):
    for filename in os.listdir(input_folder):
        if filename.endswith(('.png', 'jpg', '.bmp', '.gif')):
            input_path = os.path.join(input_folder, filename)
            stego_image_name = nameOfTheStegoImage(input_path)
            output_path = os.path.join(output_folder, stego_image_name)
            
            stego_image = codeExampleMessage(input_path)
            stego_image.save(output_path)

            try:
                mess = lsbDecoding(output_path)
                print(f'{stego_image_name}: OK')
            except:
                print(f'{stego_image_name}: Błąd')


def makeStegoImageDCT(input_folder, output_folder):
    for filename in os.listdir(input_folder):
        if filename.endswith(('.png', '.jpg', '.bmp')):
            input_path = os.path.join(input_folder, filename)
            stego_image_name = nameOfTheStegoImage(input_path)
            output_path = os.path.join(output_folder, stego_image_name)
            
            codeExampleMessageDCT(input_path, output_path)

            # try:
            #     mess = dctDecoding(output_path)
            #     if mess.startswith(('0013286Lorem ipsum dolor cit amet,')):
            #         print(f'{stego_image_name}: OK')
            #     else:
            #         print(f'{stego_image_name}: OK')
            # except:
            #     print(f'{stego_image_name}: Błąd')


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


def canWeReadMessageLSB(stego_folder, worksheet):
    scores = []
    for filename in os.listdir(stego_folder):
        if filename.endswith(('.png', '.jpg', '.bmp', '.gif', '.jpeg')):
            mess = '--'
            path = os.path.join(stego_folder, filename)
            img = Image.open(path)
            before_bytes = os.path.getsize(path)
            name, size = imageInfo(path)
            print("________________", filename, "__________________", img.size)
            try:
                mess = lsbDecoding(path)
                mess = convertToString(mess)
                value = 'OK'
                print("OK")
            except ValueError:
                value = 'CAN\'T'
                print("We can't read message on this image.")
            except IndexError:
                value = 'poprawa'
                print("Czytanie do poprawy")
            
            score = [name, size, before_bytes, value, mess]
            scores.append(score)
    
    row = 1
    col = 1
    worksheet.write(0, 1, "Nazwa")
    worksheet.write(0, 2, "Rozmiar")
    worksheet.write(0, 3, "KB obrazu")
    worksheet.write(0, 4, "Czy można")
    worksheet.write(0, 5, "Wiadomość")

    for vname, vsize, vbytes, vvalue, vmess in scores:
        worksheet.write(row, col, vname)
        worksheet.write(row, col+1, str(vsize))
        worksheet.write(row, col+2, vbytes//1000)
        worksheet.write(row, col+3, vvalue)
        worksheet.write(row, col+4, vmess)
        row += 1


def canWeReadMessageDCT(stego_folder, worksheet):
    scores = []
    for filename in os.listdir(stego_folder):
        if filename.endswith(('.png', '.jpg', '.bmp', '.gif', '.jpeg')):
            mess = '--'
            path = os.path.join(stego_folder, filename)
            img = Image.open(path)
            before_bytes = os.path.getsize(path)
            name, size = imageInfo(path)
            print("________________", filename, "__________________", img.size)
            try:
                mess = dctDecoding(path)
                if mess.startswith(('0006335Lorem ipsum')):
                    print(f'OK')
                    value = 'OK'
                else:
                    print(f'CAN\'T')
                    value = 'CAN\'T'
            # except ValueError:
            #     value = 'CAN\'T'
            #     print("We can't read message on this image.")
            except IndexError:
                value = 'poprawa'
                print("Czytanie do poprawy")
            
            score = [name, size, before_bytes, value, mess]
            scores.append(score)
    
    row = 1
    col = 1
    worksheet.write(0, 1, "Nazwa")
    worksheet.write(0, 2, "Rozmiar")
    worksheet.write(0, 3, "KB obrazu")
    worksheet.write(0, 4, "Czy można")
    worksheet.write(0, 5, "Wiadomość")

    for vname, vsize, vbytes, vvalue, vmess in scores:
        worksheet.write(row, col, vname)
        worksheet.write(row, col+1, str(vsize))
        worksheet.write(row, col+2, vbytes//1000)
        worksheet.write(row, col+3, vvalue)
        worksheet.write(row, col+4, vmess)
        row += 1


def compareImages(before_folder, after_folder, worksheet):
    scores = []
    for filename in os.listdir(after_folder):
        after_img = os.path.join(after_folder, filename)
        name_af, size_af = imageInfo(after_img)
        after_bytes = os.path.getsize(after_img)
        try:
            before_img = os.path.join(before_folder, filename)
            before_bytes = os.path.getsize(before_img)
            print("-------------------------------------------------------")
            _, size_be = imageInfo(before_img)
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
        except FileNotFoundError:
            before_bytes, size_be, cr_value, mse_value, psnr_value = 0.0, '--', '--', '--', '--' 

        score = [name_af, size_be, size_af, before_bytes, after_bytes, cr_value, mse_value, psnr_value]
        scores.append(score)
    
    row = 1
    col = 1
    worksheet.write(0, 1, "Nazwa")
    worksheet.write(0, 2, "Rozmiar przed")
    worksheet.write(0, 3, "Rozmiar po")
    worksheet.write(0, 4, "KB przed")
    worksheet.write(0, 5, "KB po")
    worksheet.write(0, 6, "CR")
    worksheet.write(0, 7, "MSE")
    worksheet.write(0, 8, "PSNR")

    for name, size1, size2, bytes1, bytes2, vcr, vmse, vpsnr in scores:
        worksheet.write(row, col, name)
        worksheet.write(row, col+1, str(size1))
        worksheet.write(row, col+2, str(size2))
        worksheet.write(row, col+3, bytes1//1000)
        worksheet.write(row, col+4, bytes2//1000)
        worksheet.write(row, col+5, vcr)
        worksheet.write(row, col+6, vmse)
        worksheet.write(row, col+7, vpsnr)
        row += 1
    
    
def compareImagesJPEG(before_folder, after_folder, worksheet):
    scores = []
    for filename in os.listdir(after_folder):
        if filename.startswith('JPG'):
            after_img = os.path.join(after_folder, filename)
            name_af, size_af = imageInfo(after_img)
            after_bytes = os.path.getsize(after_img)
            try:
                filename = filename[:-4] + '.jpg'
                before_img = os.path.join(before_folder, filename)
                print(os.path.join(before_folder, filename))
                before_bytes = os.path.getsize(before_img)
                print("-------------------------------------------------------")
                _, size_be = imageInfo(before_img)
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
            except FileNotFoundError:
                before_bytes, size_be, cr_value, mse_value, psnr_value = 0.0, '--', '--', '--', '--' 

            score = [name_af, size_be, size_af, before_bytes, after_bytes, cr_value, mse_value, psnr_value]
            scores.append(score)
    
    row = 1
    col = 1
    worksheet.write(0, 1, "Nazwa")
    worksheet.write(0, 2, "Rozmiar przed")
    worksheet.write(0, 3, "Rozmiar po")
    worksheet.write(0, 4, "KB przed")
    worksheet.write(0, 5, "KB po")
    worksheet.write(0, 6, "CR")
    worksheet.write(0, 7, "MSE")
    worksheet.write(0, 8, "PSNR")

    for name, size1, size2, bytes1, bytes2, vcr, vmse, vpsnr in scores:
        worksheet.write(row, col, name)
        worksheet.write(row, col+1, str(size1))
        worksheet.write(row, col+2, str(size2))
        worksheet.write(row, col+3, bytes1//1000)
        worksheet.write(row, col+4, bytes2//1000)
        worksheet.write(row, col+5, vcr)
        worksheet.write(row, col+6, vmse)
        worksheet.write(row, col+7, vpsnr)
        row += 1




if __name__ == '__main__':
    workbook = xlsxwriter.Workbook('D:\STUDIA\Cyberka\Inzynierka\Wyniki_excel\Signal_mozna_dct.xlsx')    
    worksheet = workbook.add_worksheet("DCT")
    input_folder = 'D:\STUDIA\Cyberka\Inzynierka\Zbiory\Zbior_obrazow' 
    output_folder = 'D:\STUDIA\Cyberka\Inzynierka\Zbior_Stego'
    facebook_folder = 'D:\STUDIA\Cyberka\Inzynierka\Zbiory\Signal_dct'
    after_folder = 'D:\STUDIA\Cyberka\Inzynierka\Zbiory\Signal_bez_info'
    dct_folder = 'D:\STUDIA\Cyberka\Inzynierka\Zbiory\Zbior_DCT_mode5'
    mini_dct_folder = 'D:\STUDIA\Cyberka\Inzynierka\Zbiory\Mini_DCT'
    mini_folder = 'D:\STUDIA\Cyberka\Inzynierka\Zbiory\Mini_zbior'
    # processImagesInFolder(input_folder, output_folder)
    # canWeReadMessage(facebook_folder, worksheet)
    # changeNames(input_folder)
    # compareImagesJPEG(input_folder, dct_folder, worksheet)
    # makeStegoImageDCT(input_folder, dct_folder)
    canWeReadMessageDCT(facebook_folder, worksheet)
    workbook.close()
    # makeStegoImage(input_folder, output_folder)