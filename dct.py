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
    if not img.mode == 'RGB':
        img = img.convert('RGB')  # pozniej przy zapisywaniu .save("nazwa.jpg", "JPEG")
    img = np.array(img)
    height, width, channels = img.shape
    height_skip, width_skip = img.strides[:2]
    print(img.shape)
    print(img.strides, height_skip, width_skip)
    img = img[:img.shape[0] - img.shape[0] % 8, :img.shape[1] - img.shape[1] % 8]  
    blocks = np.lib.stride_tricks.as_strided(img, 
                                    shape=(height//8, width//8, 8, 8, channels), 
                                    strides=(height_skip*8, width_skip*8, height_skip, width_skip, 1))
    print(blocks.shape, blocks.strides)
    print(blocks)
    return blocks

def dctTransformation(blocks):
    


if __name__ == '__main__':
    path = 'd:/STUDIA/Cyberka/Inzynierka/Proby/16x8_mem.png'
    prepareImage(path)


