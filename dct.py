from PIL import Image
from scipy.fftpack import fft, dct, idct
import numpy as np
import huffman
from collections import Counter

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
    img = Image.open(path)
    img = img.convert("YCbCr")  # to można rozbudować i napisać własny kod na podstawie wzorów
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
                if bit_index >= len(message_in_bits):
                    return dct_blocks  # zakończ jeśli wszystkie bity zostały ukryte
                
                # Wyciągnięcie współczynników AC z bloku
                block = dct_blocks[i, j, :, :, channel]
                # print("b", block)
                zigzag = zigZagEncoding(block)
                
                # Zakodowanie jednego bitu wiadomości w niskim współczynniku AC
                if int(message_in_bits[bit_index]) == 1:
                    if zigzag[1] % 2 == 0:
                        zigzag[1] += 1  # ustaw bit LSB na 1
                else:
                    if zigzag[1] % 2 != 0:
                        zigzag[1] -= 1  # ustaw bit LSB na 0

                # Aktualizacja współczynników po wprowadzeniu wiadomości
                block[0, 1] = zigzag[1]
                # print("n", block)
                dct_blocks[i, j, :, :, channel] = block
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


def dctTransformation(blocks, apply_quantization=True):
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
                dct_block = dct(dct(block.T, norm='ortho').T, norm='ortho')
                
                if apply_quantization:
                    dct_block = np.round(dct_block / quant_table)
                
                dct_blocks[i, j, :, :, channel] = dct_block

    return dct_blocks   


def inverseDCT(dct_blocks):
    height, width = dct_blocks.shape[:2]
    image_reconstructed = np.zeros((height * 8, width * 8, 3), dtype=np.uint8)
    for i in range(0, height):
        for j in range(0, width):
            for channel in range(3):
                
                block = dct_blocks[i, j, :, :, channel]
                idct_block = idct(idct(block.T, norm='ortho').T, norm='ortho')
                
                idct_block += 128
                idct_block = np.clip(idct_block, 0, 255)
                image_reconstructed[i*8:(i+1)*8, j*8:(j+1)*8, channel] = idct_block
    return image_reconstructed


def saveImage(image_data, output_path):
    # Konwersja z przestrzeni YCbCr do RGB dla zapisu
    img = Image.fromarray(image_data, 'YCbCr').convert('RGB')
    img.save(output_path, 'PNG')



if __name__ == '__main__':
    path = 'd:/STUDIA/Cyberka/Inzynierka/Proby/Zdjecia/photo.jpg'
    output_path = 'd:/STUDIA/Cyberka/Inzynierka/Proby/Zdjecia/16x16_stego.png'
    message = "Hello World"
    _, mess_in_binary = convertToBinary(message)

    blocks = prepareImage(path)
    dct_blocks = dctTransformation(blocks, False)
    stego_dct_blocks = hideMessageInDCT(dct_blocks, mess_in_binary)
    # quantization(dct_blocks)

    image_with_mess = inverseDCT(stego_dct_blocks)
    saveImage(image_with_mess, output_path)

