import math
import sys
import numpy as np
from PIL import Image


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

# DO USUNIĘCIA - kod sprawdzający
    # print("Message in binary: ", message_in_binary)
    
    # for number in table_of_bin:
    #     print(type(number))
    #     print(number)
    print(len(message))
    print(len(message_in_binary))
    return table_of_bin, message_in_binary

def convertToString(message_in_binary):
    table_of_strings = []
    message = ""
    for char in range(0, len(message_in_binary), 7):
        table_of_strings.append(chr(int(message_in_binary[char:char+7], 2)))

    for i in table_of_strings:
        message += i

    print(message)
    return message


def convertImage(path):
    img = Image.open(path)
    numpy_img = np.array(img)
    # numpy_img = numpy_img.astype(np.uint8)
    # print(numpy_img)
    print(numpy_img.shape, numpy_img.ndim, numpy_img.dtype)
    return numpy_img


def lsbCoding(img, message):
    shape = img.shape
    size = img.size
    # print(shape, img.size)
    # print(img)
    resized_img = img.reshape(1, size)
    # print(resized_img, "\n", resized_img.shape, resized_img.size)
    flag = 2
    # print(resized_img)
    for bit in range(0, len(message)-1):
        # print(resized_img[0, flag])
        if message[bit] == '0':
            resized_img[0, flag] = resized_img[0, flag] & ~1  # wyzerowanie ostatniego bitu
        elif message[bit] == '1':
            # print("RESIZED:  ", resized_img[0, flag])
            resized_img[0, flag] = resized_img[0, flag] | 1   # ustawia ostatni bit na 1
        else:
            print("Błąd")
        # print(resized_img[0, flag])
        flag += 3
    
    # print("_________________proba_________________")
    # print(resized_img)
    print("______________wynik__________")

    new_img = resized_img.reshape(shape)
    pil_image = Image.fromarray(new_img)
    # print(new_img)
    return new_img, pil_image


def lsbDecoding(img):
    message = ''
    resized_img = img.reshape(1, img.size)
    size_of_text = ''
    # print(img.size)
    # print(resized_img)
    for bit in range(2, 149, 3):
        if resized_img[0, bit] % 2 == 0:
            size_of_text += '0'
        elif resized_img[0, bit] % 2 == 1:
            size_of_text += '1'
        else:
            print("Błąd")
    
    size = int(convertToString(size_of_text))
    
    print("size_of_text", size_of_text)
    for bit in range(2, (size*3)+2, 3):

        # print(resized_img[0, bit])
        if resized_img[0, bit] % 2 == 0:
            message += '0'
        elif resized_img[0, bit] % 2 == 1:
            message += '1'
        else:
            print("Błąd")
    # print(message)
    return message









    
if __name__ == '__main__':
    message = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc at arcu lorem. Pellentesque iaculis, odio non volutpat consequat, velit lectus vehicula ipsum, a maximus metus tortor et metus. Donec massa elit, viverra id dignissim in, dignissim at ex. Suspendisse in faucibus nibh. Proin pretium sodales ante ut ultricies. Mauris vel diam iaculis, finibus tellus sit amet, convallis diam. Pellentesque et felis aliquam, finibus dolor at, commodo odio. In fringilla imperdiet lectus, eu rutrum ligula pulvinar nec. Sed malesuada tellus in sapien pellentesque pulvinar. Ut quis metus faucibus elit pretium aliquam. Vestibulum at nulla et risus tristique tincidunt. Nunc porttitor et eros feugiat consectetur. Suspendisse mauris elit, ultrices non risus nec, aliquet pretium purus. Vestibulum dignissim urna eget egestas porta. Aenean eget eros dapibus, fringilla nisi vel, tincidunt ex. Integer vitae vulputate nisi. Cras egestas sem lorem, vel maximus metus ultricies ac. Praesent lobortis egestas dignissim. Etiam porttitor faucibus erat. Curabitur dapibus sem at faucibus facilisis.Maecenas congue odio sed ultricies consectetur. Nullam venenatis orci ac diam maximus, nec elementum erat fermentum. Nullam nisl nibh, luctus id blandit at, luctus eu purus. Duis ultrices, velit eu consequat semper, arcu nisl dapibus elit, commodo egestas ante odio vitae justo. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Suspendisse libero lectus, condimentum a eleifend pellentesque, ultrices a mi. Nam eu mi vehicula, porttitor eros varius, dictum justo. In fringilla vel purus eu ultrices. Donec imperdiet, nulla eget aliquam aliquet, diam eros iaculis erat, at venenatis nunc magna sollicitudin erat. Donec diam odio, hendrerit nec fermentum eu, fermentum non eros. Suspendisse sit amet augue nibh. Suspendisse eget magna at orci malesuada porttitor id et eros."
    table_of_bin, message_in_binary = convertToBinary(message)
    convertToString("10010001100101110110011011001101111")
    message_in_binary1 = convertToString(message_in_binary)

    print("Przetlumaczona wiadomosc: ", message_in_binary1)
    path = 'd:/STUDIA/Cyberka/Inzynierka/Proby/photo.jpg'


    starter = np.zeros((10, 10, 3)) # 42 znaki
    img = convertImage(path)
    img_with_info, pil_img = lsbCoding(img, message_in_binary)
    pil_img.save("wiadomosc.jpg")
    np.set_printoptions(threshold=sys.maxsize)
    # print("Img with info\n", img_with_info[0:1, 0:15])
    hide_massage = lsbDecoding(img_with_info)
    convertToString(hide_massage)
