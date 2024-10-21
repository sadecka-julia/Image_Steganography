import math
import sys
import numpy as np
from PIL import Image


'''Zamienia wiadomość na postać binarną. 
Najpierw obliczana jest długość wiadomości + 49 bitów (w których jest zakodowana długość wiadomości)
Następnie każdy znak jest zamieniany na postać binarną (każdy znak to 7 bitów)
Zwracane zostają:
1. Tablica z wartościami każdego znaku (table)
2. Połączona wiadomość w postaci binarnej (str)'''
def convertToBinary(message):
    table_of_bin = []
    len_of_message = str((len(message)*7) + 49)
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


'''Zamienia postać binarną na wiadomość
Zwraca wiadomość (str)'''
def convertToString(message_in_binary):
    table_of_strings = []
    message = ""
    for char in range(0, len(message_in_binary), 7):
        table_of_strings.append(chr(int(message_in_binary[char:char+7], 2)))

    for i in table_of_strings:
        message += i

    return message


# Zamienia obraz na macierz numpy
def convertImage(path):
    img = Image.open(path)
    numpy_img = np.array(img)
    print(numpy_img.shape, numpy_img.ndim, numpy_img.dtype)
    return numpy_img


'''Koduje w obrazie ukrytą wiadomość, robi to ukrywając bity wiadomości w najmniej znaczących bitach pikseli
Zwracamy:
1. Stego obraz w wersji numpy
2. Obraz z zakodowaną wiadomością'''
def lsbCoding(img, message):
    shape = img.shape     # Kształt obrazu, potrzebny, aby później przywrócić obraz do tego kształtu
    size = img.size       # Rozmiar obrazu
    resized_img = img.reshape(1, size)  # Zmienia macierz obrazu, aby była była jednowymiarowa
    print(img)
    pixel = 0              # Przemieszczamy się po kolejnych wartościach pikseli 
    for bit in range(0, len(message)-1):
        if message[bit] == '0':
            resized_img[0, pixel] = resized_img[0, pixel] & ~1  # Wyzerowanie ostatniego bitu
        elif message[bit] == '1':
            resized_img[0, pixel] = resized_img[0, pixel] | 1   # Ustawia ostatni bit na 1
        else:
            print("Błąd")
        pixel += 1

    new_img = resized_img.reshape(shape)
    pil_image = Image.fromarray(new_img)
    return new_img, pil_image


# Odkodowuje wiadomość z obrazu
def lsbDecoding(img):
    message = ''
    resized_img = img.reshape(1, img.size)
    size_of_text = ''

# Odczytanie długości wiadomości (zakodowanej w 7 znakach = 49 bitach)
    for bit in range(0, 49):      # (2, 149, 3) - jeżeli chcemy zakodować wiadomość tylko w pikselach B (blue), wtedy należy zmeinić też pętlę poniżej (2, (size*3)+2, 3), a rakże w funkcji coding
        if resized_img[0, bit] % 2 == 0:
            size_of_text += '0'
        elif resized_img[0, bit] % 2 == 1:
            size_of_text += '1'
        else:
            print("Błąd")
    size = int(convertToString(size_of_text))

# Odczytujemy ukrytą wiadomość
    for bit in range(0, size):
        if resized_img[0, bit] % 2 == 0:
            message += '0'
        elif resized_img[0, bit] % 2 == 1:
            message += '1'
        else:
            print("Błąd")
    return message[49:] # Zostaje zwrócona wiadomość w postaci bitowej (bez długości wiadomości)

    
if __name__ == '__main__':
    message1 = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc at arcu lorem. Pellentesque iaculis, odio non volutpat consequat, velit lectus vehicula ipsum, a maximus metus tortor et metus. Donec massa elit, viverra id dignissim in, dignissim at ex. Suspendisse in faucibus nibh. Proin pretium sodales ante ut ultricies. Mauris vel diam iaculis, finibus tellus sit amet, convallis diam. Pellentesque et felis aliquam, finibus dolor at, commodo odio. In fringilla imperdiet lectus, eu rutrum ligula pulvinar nec. Sed malesuada tellus in sapien pellentesque pulvinar. Ut quis metus faucibus elit pretium aliquam. Vestibulum at nulla et risus tristique tincidunt. Nunc porttitor et eros feugiat consectetur. Suspendisse mauris elit, ultrices non risus nec, aliquet pretium purus. Vestibulum dignissim urna eget egestas porta. Aenean eget eros dapibus, fringilla nisi vel, tincidunt ex. Integer vitae vulputate nisi. Cras egestas sem lorem, vel maximus metus ultricies ac. Praesent lobortis egestas dignissim. Etiam porttitor faucibus erat. Curabitur dapibus sem at faucibus facilisis.Maecenas congue odio sed ultricies consectetur. Nullam venenatis orci ac diam maximus, nec elementum erat fermentum. Nullam nisl nibh, luctus id blandit at, luctus eu purus. Duis ultrices, velit eu consequat semper, arcu nisl dapibus elit, commodo egestas ante odio vitae justo. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Suspendisse libero lectus, condimentum a eleifend pellentesque, ultrices a mi. Nam eu mi vehicula, porttitor eros varius, dictum justo. In fringilla vel purus eu ultrices. Donec imperdiet, nulla eget aliquam aliquet, diam eros iaculis erat, at venenatis nunc magna sollicitudin erat. Donec diam odio, hendrerit nec fermentum eu, fermentum non eros. Suspendisse sit amet augue nibh. Suspendisse eget magna at orci malesuada porttitor id et eros."
    message = 'a a1'
    table_of_bin, message_in_binary = convertToBinary(message)
    print(table_of_bin, message_in_binary)
    print(convertToString("10010001100101110110011011001101111"))
    message_in_binary1 = convertToString(message_in_binary)

    print("Przetlumaczona wiadomosc: ", message_in_binary1)
    path = 'd:/STUDIA/Cyberka/Inzynierka/Proby/photo.jpg'


    # starter = np.zeros((10, 10, 3)) # 42 znaki
    img = convertImage(path)
    img_with_info, stego_img = lsbCoding(img, message_in_binary)
    stego_img.save("wiadomosc1.png")
    # np.set_printoptions(threshold=sys.maxsize)
    # print("Img with info\n", img_with_info[0:1, 0:15])
    stego_path = 'D:\STUDIA\Cyberka\Inzynierka\wiadomosc1.png' # jpg zmienia obraz, że nie da się późneij go odczytać
    stego = convertImage(stego_path)
    # stego = np.array(stego_img)
    hide_massage = lsbDecoding(stego)
    print(convertToString(hide_massage))
