from PIL import Image
from scipy.fftpack import dct, idct
import numpy as np
from collections import Counter
import cv2
# from readDCT import extractBitsFromImage

def convertToBinary(message):
    table_of_bin = []
    len_of_message = str((len(message)*7) + 49)
    # print(len_of_message)
    message_in_binary = ""
    while len(len_of_message) < 7:
        len_of_message = '0' + len_of_message
    message = len_of_message + message

    
    for char in message:
        bin_repr = bin(ord(char))[2:].zfill(7)
        table_of_bin.append(bin_repr)

    for b in table_of_bin:
        message_in_binary += b

    # print(len(message))
    # print(len(message_in_binary))
    return table_of_bin, message_in_binary


# Wczytanie obrazu, podzielenie go na bloki 8x8
def prepareImage(path):
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)  # to można rozbudować i napisać własny kod na podstawie wzorów
    img = np.array(img)

    height, width, channels = img.shape
    height_skip, width_skip = img.strides[:2]

    img = img[:img.shape[0] - img.shape[0] % 8, :img.shape[1] - img.shape[1] % 8]  # Dodać podpis, że zmniejszyłam obraz. Zmniejszyłam aby był podizelny przez 8
    blocks = np.lib.stride_tricks.as_strided(img, 
                                    shape=(height//8, width//8, 8, 8, channels), 
                                    strides=(height_skip*8, width_skip*8, height_skip, width_skip, 1)) # Dzielenie obrazu na bloki 8x8 za pomocą wykorzystania strides z biblioteki numpy

    y, cb, cr = blocks[:, :, :, :, 0], blocks[:, :, :, :, 1], blocks[:, :, :, :, 2]
    # Funkcja która każdą z wartości zmniejszy o 128
    def  subtraction(x):
        return x-128
    sub_blocks = np.vectorize(subtraction)
    blocks = sub_blocks(blocks)
 
    return blocks


def hideMessageInDCT(dct_blocks, message_in_bits):
    bit_index = 0
    height, width = dct_blocks.shape[:2]
    for i in range(height):
        for j in range(width):
            for channel in range(3):
                if channel in [2]:
                    if bit_index >= len(message_in_bits):
                        return dct_blocks  # zakończ jeśli wszystkie bity zostały ukryte
                    # block = dct_blocks[i, j, :, :, channel]

                    # zigzag = zigZagEncoding(block)

                    idx = 0 # Miejsce zakodowania wiadomości
                    zigzag = int(dct_blocks[i, j, 0, 0, channel])

                    if int(message_in_bits[bit_index]) == 0:
                        if zigzag % 6 == 4:
                            zigzag += 1
                        elif zigzag % 6 == 0:
                            zigzag -= 1
                        elif zigzag % 6 == 1:
                            zigzag -= 2
                        elif zigzag % 6 == 2:
                            zigzag += 3
                        elif zigzag % 6 == 3:
                            zigzag += 2
                    else:
                        if zigzag % 6 == 0:
                            zigzag += 2
                        elif zigzag % 6 == 1:
                            zigzag += 1
                        elif zigzag % 6 == 3:
                            zigzag -= 1
                        elif zigzag % 6 == 4:
                            zigzag -= 2
                        elif zigzag % 6 == 5:
                            zigzag -= 3
                    # print(f"Embedding bit {message_in_bits[bit_index]} at position ({i}, {j}, {channel}), coefficient {zigzag}")
                    # Aktualizacja współczynników po wprowadzeniu wiadomości
                    # block[0, 0] = zigzag[idx]
                    dct_blocks[i, j, 0, 0, channel] = zigzag
                    bit_index += 1
    return dct_blocks



# Funkcja implementująca zig zag encoding - dzięki temu można odczytać bloki jako ciąg wartości
def zigZagEncoding(block):
    i, j = 0, 0
    new_table = []
    flag = True
    while(flag):
        new_table.append(block[i, j])

        if i == 7 and j == 7:
            flag = False
        elif i == 0 and j%2==0:
            j += 1
            continue
        elif i==7 and j%2==0:
            j+=1
            continue
        elif j==0 and i%2==1:
            i += 1
            continue
        elif j==7 and i%2==1:
            i += 1
            continue
        elif (i-j)%2 ==0:
            j+=1
            i-=1
            continue
        elif (i-j)%2 ==1:
            j-=1
            i+=1
            continue
        else:
            print("Error")
    return new_table


def dctTransformation(blocks, apply_quantization=False):
    lumi_quant_table = [[16, 11, 10, 16, 24, 40, 51, 61], 
                        [12, 12, 14, 19, 26, 58, 60, 55],
                        [14, 13, 16, 24, 40, 57, 69, 56],
                        [14, 17, 22, 29, 51, 87, 80, 62],
                        [18, 22, 37, 56, 68, 109, 103, 77],
                        [24, 35, 55, 64, 81, 104, 113, 92],
                        [49, 64, 78, 87, 103, 121, 120, 101],
                        [72, 92, 95, 98, 112, 100, 103, 99]]
    lumi_quant_table = np.array(lumi_quant_table)
    
    chrom_quant_table = [[17, 18, 24, 47, 99, 99, 99, 99], 
                         [18, 21, 26, 66, 99, 99, 99, 99], 
                         [24, 26, 56, 99, 99, 99, 99, 99], 
                         [47, 66, 99, 99, 99, 99, 99, 99],
                         [99, 99, 99, 99, 99, 99, 99, 99],
                         [99, 99, 99, 99, 99, 99, 99, 99], 
                         [99, 99, 99, 99, 99, 99, 99, 99], 
                         [99, 99, 99, 99, 99, 99, 99, 99]]
    chrom_quant_table = np.array(chrom_quant_table)
    
    height, width = blocks.shape[:2]
    dct_blocks = np.zeros_like(blocks)

    for i in range(0, height):
        for j in range(0, width):
            for channel in range(3):
                if channel == 0:
                    quant_table = lumi_quant_table
                else:
                    quant_table = chrom_quant_table
                
                block = blocks[i, j, :, :, channel]
                # dct_block = dct(dct(block.T, norm='ortho').T, norm='ortho')
                dct_block = cv2.dct(block.astype(np.float32))

                if apply_quantization:
                    dct_block = np.round(dct_block / quant_table)
                
                dct_blocks[i, j, :, :, channel] = dct_block

    return dct_blocks   


def inverseDCT(dct_blocks):
    height, width = dct_blocks.shape[:2]
    image_reconstructed = np.zeros((height * 8, width * 8, 3), dtype=np.float32)
    for i in range(0, height):
        for j in range(0, width):
            for channel in range(3):
                
                block = dct_blocks[i, j, :, :, channel]
                # idct_block = idct(idct(block.T, norm='ortho').T, norm='ortho')
                idct_block = cv2.idct(block.astype(np.float32))

                idct_block += 128
                idct_block = np.clip(idct_block, 0, 255)
                image_reconstructed[i*8:(i+1)*8, j*8:(j+1)*8, channel] = idct_block
    return image_reconstructed


def saveImage(image_data, output_path):
    # Konwersja z przestrzeni YCbCr do RGB dla zapisu
    # img = cv2.cvtColor(image_data, cv2.COLOR_YCrCb2BGR)
    cv2.imwrite(output_path, image_data)

def codeExampleMessageDCT(input_path, output_path):
    message = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc at arcu lorem. Pellentesque iaculis, odio non volutpat consequat, velit lectus vehicula ipsum, a maximus metus tortor et metus. Donec massa elit, viverra id dignissim in, dignissim at ex. Suspendisse in faucibus nibh. Proin pretium sodales ante ut ultricies. Mauris vel diam iaculis, finibus tellus sit amet, convallis diam. Pellentesque et felis aliquam, finibus dolor at, commodo odio. In fringilla imperdiet lectus, eu rutrum ligula pulvinar nec. Sed malesuada tellus in sapien pellentesque pulvinar. Ut quis metus faucibus elit pretium aliquam. Vestibulum at nulla et risus tristique tincidunt. Nunc porttitor et eros feugiat consectetur. Suspendisse mauris elit, ultrices non risus nec, aliquet pretium purus. Vestibulum dignissim urna eget egestas porta. Aenean eget eros dapibus, fringilla nisi vel, tincidunt ex. Integer vitae vulputate nisi. Cras egestas sem lorem, vel maximus metus ultricies ac. Praesent lobortis egestas dignissim. Etiam porttitor faucibus erat. Curabitur dapibus sem at faucibus facilisis.Maecenas congue odio sed ultricies consectetur. Nullam venenatis orci ac diam maximus, nec elementum erat fermentum. Nullam nisl nibh, luctus id blandit at, luctus eu purus. Duis ultrices, velit eu consequat semper, arcu nisl dapibus elit, commodo egestas ante odio vitae justo. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Suspendisse libero lectus, condimentum a eleifend pellentesque, ultrices a mi. Nam eu mi vehicula, porttitor eros varius, dictum justo. In fringilla vel purus eu ultrices. Donec imperdiet, nulla eget aliquam aliquet, diam eros iaculis erat, at venenatis nunc magna sollicitudin erat. Donec diam odio, hendrerit nec fermentum eu, fermentum non eros. Suspendisse sit amet augue nibh. Suspendisse eget magna at orci malesuada porttitor id et eros."
    message2 = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
    _, message_in_binary = convertToBinary(message2)
    
    blocks = prepareImage(input_path)
    # print(len(message), len(message_in_binary))
    dct_blocks = dctTransformation(blocks)
    stego_dct_blocks = hideMessageInDCT(dct_blocks, message_in_binary)
    image_with_mess = inverseDCT(stego_dct_blocks)
    saveImage(image_with_mess, output_path)




if __name__ == '__main__':
    path = 'd:/STUDIA/Cyberka/Inzynierka/Proby/Zdjecia/photo.jpg'
    output_path = 'd:/STUDIA/Cyberka/Inzynierka/Proby/Zdjecia/stego.png'
    message = "Hello World"
    # _, mess_in_binary = convertToBinary(message)
    # print(mess_in_binary, len(mess_in_binary))

    # blocks = prepareImage(path)
    # dct_blocks = dctTransformation(blocks)
    # stego_dct_blocks = hideMessageInDCT(dct_blocks, mess_in_binary)
    # # quantization(dct_blocks)

    # image_with_mess = inverseDCT(stego_dct_blocks)
    # saveImage(image_with_mess, output_path)
    codeExampleMessageDCT(path, output_path)

