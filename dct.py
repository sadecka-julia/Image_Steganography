from PIL import Image
from scipy.fftpack import fft, dct
import numpy as np

def convertToBinary(message):
    table_of_bin = []
    len_of_message = str((len(message)*7) + 49)
    print(len_of_message)
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

def convertToString(message_in_binary):
    table_of_strings = []
    message = ""
    for char in range(0, len(message_in_binary), 7):
        table_of_strings.append(chr(int(message_in_binary[char:char+7], 2)))

    for i in table_of_strings:
        message += i

    # print(message)
    return message

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

def runLenghtEncoding(block):
    zero_flag = 0
    block_after_run_lenght = []
    for i in range(0, 63):
        if block[i] == 0:
            zero_flag += 1
        else:
            block_after_run_lenght.append([zero_flag, 0, int(block[i])])
            zero_flag = 0
    if zero_flag > 0:
        block_after_run_lenght.append('EOB')
    return block_after_run_lenght




def dctTransformation(blocks):
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
    zigzag_table = np.zeros((height, width, 3, 64), dtype=np.int16)
    print(zigzag_table)
    prev_dc_value = [0, 0, 0]
    dct_blocks = np.zeros_like(blocks)
    run_length_table = []
    for i in range(0, height):
        for j in range(0, width):
            for channel in range(3):
                if channel == 0:
                    quant_table = lumi_quant_table
                else:
                    quant_table = chrom_quant_table
                
                block = blocks[i, j, :, :, channel]
                    # print("Wskaźnik: ", i, j, channel)
                dct_block = dct(dct(block.T, norm='ortho').T, norm='ortho')
                    # print(dct_block)
                dct_blocks[i, j, :, :, channel] = dct_block
                for k in range(0, 8):
                    for l in range(0, 8):
                        dct_blocks[i, j, k, l, channel] = np.round(dct_blocks[i, j, k, l, channel]//quant_table[k, l])
                    # print("Block, channel: ", channel, "\n", block)
                new_dc_value = dct_blocks[i, j, 0, 0, channel]
                # print("Sprawdzenie dc value: ", dct_blocks[i, j, 0, 0, channel], "Prev dc value: ", prev_dc_value[channel])
                dct_blocks[i, j, 0, 0, channel] -= prev_dc_value[channel] 
                prev_dc_value[channel] = new_dc_value

                block = dct_blocks[i, j, :, :, channel]
                # print("Block, channel: ", channel, "\n", block)
                new_zigzag_represeantation = zigZagEncoding(block)
                zigzag_table[i, j, channel] = runLenghtEncoding(new_zigzag_represeantation) #zigzag table będzie niepotrzebna
                print(runLenghtEncoding(new_zigzag_represeantation))
                

                

                


                # print(dct_blocks)
    # print("In dct Transformation, dct blocks: \n", dct_blocks)
    # print(dct_blocks.shape, dct_blocks.strides, dct_blocks.itemsize)
    print(zigzag_table)
    return dct_blocks   


if __name__ == '__main__':
    path = 'd:/STUDIA/Cyberka/Inzynierka/Proby/16x16_mem.png'
    blocks = prepareImage(path)
    dct_blocks = dctTransformation(blocks)
    # quantization(dct_blocks)


