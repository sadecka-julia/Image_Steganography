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
    # y, cb, cr = img.split()
    # y.show()
    # cb.show()
    # cr.show()
    # img.show()
    # if not img.mode == 'RGB':
    #     img = img.convert('RGB')  # pozniej przy zapisywaniu .save("nazwa.jpg", "JPEG")
    img = np.array(img)
    # print(img)
    # R, G, B = img[:, :, 0], img[:, :, 1], img[:, :, 2]
    # r_image = Image.fromarray(np.uint8(B))
    # r_image.show()

    height, width, channels = img.shape
    height_skip, width_skip = img.strides[:2]
    # print(img.shape)
    print(img.strides, height_skip, width_skip)
    img = img[:img.shape[0] - img.shape[0] % 8, :img.shape[1] - img.shape[1] % 8]  # Dodać podpis, że zmniejszyliśmy obraz
    blocks = np.lib.stride_tricks.as_strided(img, 
                                    shape=(height//8, width//8, 8, 8, channels), 
                                    strides=(height_skip*8, width_skip*8, height_skip, width_skip, 1))
    print(blocks.shape, blocks.strides)
    # print(blocks[:, :, :, :, 0])
    # print(blocks)

    y, cb, cr = blocks[:, :, :, :, 0], blocks[:, :, :, :, 1], blocks[:, :, :, :, 2]
    # y_image = Image.fromarray(np.uint8(y))
    # y_image.show()
    def  subtraction(x):
        return x-128
    sub_blocks = np.vectorize(subtraction)
    blocks = sub_blocks(blocks)
    print(blocks)


 
    return blocks

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
    print(type(lumi_quant_table[0, 0]))
    
    chrom_quant_table = [[17, 18, 24, 47, 99, 99, 99, 99], 
                         [18, 21, 26, 66, 99, 99, 99, 99], 
                         [24, 26, 56, 99, 99, 99, 99, 99], 
                         [47, 66, 99, 99, 99, 99, 99, 99],
                         [99, 99, 99, 99, 99, 99, 99, 99],
                         [99, 99, 99, 99, 99, 99, 99, 99], 
                         [99, 99, 99, 99, 99, 99, 99, 99], 
                         [99, 99, 99, 99, 99, 99, 99, 99]]
    chrom_quant_table = np. array(chrom_quant_table)
    
    height, width = blocks.shape[:2]
    print(blocks.shape)
    dct_blocks = np.zeros_like(blocks)
    for i in range(0, height):
        for j in range(0, width):
            for channel in range(3):
                # print("halo")
                print(channel, type(channel))
                if channel == 0:
                    block = blocks[i, j, :, :, channel]
                    # print(block)
                    dct_block = dct(dct(block.T, norm='ortho').T, norm='ortho')
                    print(dct_block)
                    dct_blocks[i, j, :, :, channel] = dct_block
                    for k in range(0, 8):
                        for l in range(0, 8):
                            dct_blocks[i, j, k, l, channel] = dct_blocks[i, j, k, l, channel]//lumi_quant_table[k, l]
                elif channel == 1 or channel == 2:
                    block = blocks[i, j, :, :, channel]
                    # print(block)
                    dct_block = dct(dct(block.T, norm='ortho').T, norm='ortho')
                    print(dct_block)
                    dct_blocks[i, j, :, :, channel] = dct_block
                    for k in range(0, 8):
                        for l in range(0, 8):
                            dct_blocks[i, j, k, l, channel] = dct_blocks[i, j, k, l, channel]//chrom_quant_table[k, l]

                # print(dct_blocks)
    print(dct_blocks)
    # print(dct_blocks.shape, dct_blocks.strides, dct_blocks.itemsize)
    return dct_blocks

def quantization(dct_blocks):
    lumi_quant_table = [[16, 11, 10, 16, 24, 40, 51, 61], 
                        [12, 12, 14, 19, 26, 58, 60, 55],
                        [14, 13, 16, 24, 40, 57, 69, 56],
                        [14, 17, 22, 29, 51, 87, 80, 62],
                        [18, 22, 37, 56, 68, 109, 103, 77],
                        [24, 35, 55, 64, 81, 104, 113, 92],
                        [49, 64, 78, 87, 103, 121, 120, 101],
                        [72, 92, 95, 98, 112, 100, 103, 99]]
    
    chrom_quant_table = [[17, 18, 24, 47, 99, 99, 99, 99], 
                         [18, 21, 26, 66, 99, 99, 99, 99], 
                         [24, 26, 56, 99, 99, 99, 99, 99], 
                         [47, 66, 99, 99, 99, 99, 99, 99],
                         [99, 99, 99, 99, 99, 99, 99, 99],
                         [99, 99, 99, 99, 99, 99, 99, 99], 
                         [99, 99, 99, 99, 99, 99, 99, 99], 
                         [99, 99, 99, 99, 99, 99, 99, 99]]
    y, cb, cr = dct_blocks[:, :, :, :, 0], dct_blocks[:, :, :, :, 1], dct_blocks[:, :, :, :, 2]
    print(y)
    # for i in range(0, )


   


if __name__ == '__main__':
    path = 'd:/STUDIA/Cyberka/Inzynierka/Proby/16x16_mem.png'
    blocks = prepareImage(path)
    dct_blocks = dctTransformation(blocks)
    # quantization(dct_blocks)


