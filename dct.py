from PIL import Image
from scipy.fftpack import fft, dct
import numpy as np
import huffman
from collections import Counter

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

    return table_of_bin, message_in_binary

def convertToString(message_in_binary):
    table_of_strings = []
    message = ""
    for char in range(0, len(message_in_binary), 7):
        table_of_strings.append(chr(int(message_in_binary[char:char+7], 2)))

    for i in table_of_strings:
        message += i

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

def hideMessageInDCT(dct_blocks, message):
    bits_message = convertToBinary(message)



def dctTransformation(blocks):    
    height, width = blocks.shape[:2]
    zigzag_table = np.zeros((height, width, 3, 64), dtype=np.int16)
    prev_dc_value = [0, 0, 0]
    dct_blocks = np.zeros_like(blocks)
    ac_table = []
    dc_table = []
    for i in range(0, height):
        for j in range(0, width):
            for channel in range(3):
                # if channel == 0:
                #     quant_table = lumi_quant_table
                # else:
                #     quant_table = chrom_quant_table
                
                # block = blocks[i, j, :, :, channel]
                #     # print("Wskaźnik: ", i, j, channel)
                # dct_block = dct(dct(block.T, norm='ortho').T, norm='ortho')
                #     # print(dct_block)
                # dct_blocks[i, j, :, :, channel] = dct_block
                for k in range(0, 8):
                    for l in range(0, 8):
                        if k == 0 and l == 0:
                            continue
                        dct_blocks[i, j, k, l, channel] = np.round(dct_blocks[i, j, k, l, channel]//quant_table[k, l])
                    # print("Block, channel: ", channel, "\n", block)
                new_dc_value = dct_blocks[i, j, 0, 0, channel]
                # print("Sprawdzenie dc value: ", dct_blocks[i, j, 0, 0, channel], "Prev dc value: ", prev_dc_value[channel])
                dc_diff = dct_blocks[i, j, 0, 0, channel] - prev_dc_value[channel] 
                prev_dc_value[channel] = new_dc_value
                dc_table.append(dc_diff)

                block = dct_blocks[i, j, :, :, channel]
                # print("Block, channel: ", channel, "\n", block)
                new_zigzag_representation = zigZagEncoding(block)
                # zigzag_table[i, j, channel] = runLenghtEncoding(new_zigzag_represeantation) #zigzag table będzie niepotrzebna
                ac_table.append(runLenghtEncoding(new_zigzag_representation))
                # print(runLenghtEncoding(new_zigzag_representation))
                

                

                


                # print(dct_blocks)
    # print("In dct Transformation, dct blocks: \n", dct_blocks)
    # print(dct_blocks.shape, dct_blocks.strides, dct_blocks.itemsize)
    # print(zigzag_table)
    dc_table = np.array(dc_table)
    # print("DC table ", dc_table)
    # print("AC table ", ac_table)
    dc_freq_table = creatingHuffmanTree(dc_table)
    dc_encoded_data = huffmanEncoding(dc_freq_table, dc_table)
    # print("Huffman tree: ", dc_freq_table, "\nEncoded data: ", dc_encoded_data)
    element_ac_array = np.array([item for sublist in ac_table for item in sublist])
    ac_array = np.reshape(element_ac_array, np.size(element_ac_array))
    # print("AC table ", ac_array, np.size(ac_array), np.shape(ac_array))
    ac_freq_table = creatingHuffmanTree(ac_array)
    ac_encoded_data = huffmanEncoding(ac_freq_table, element_ac_array)
    print("Huffman tree: ", ac_freq_table, "\nEncoded data: ", ac_encoded_data)


    return dct_blocks   


if __name__ == '__main__':
    path = 'd:/STUDIA/Cyberka/Inzynierka/Proby/16x16_mem.png'
    blocks = prepareImage(path)
    dct_blocks = dctTransformation(blocks)
    # quantization(dct_blocks)

