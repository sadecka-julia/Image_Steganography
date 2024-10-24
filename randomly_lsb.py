"""
Ten skrypt implementuje metodę ukrywania wiadomości w obrazach za pomocą zmodyfikowanego algorytmu LSB (Least Significant Bit).
Wiadomość jest zakodowana w najmniej znaczących bitach obrazu. Aby zakodować wiadomość, najpierw konwertuje się ją do postaci
binarnych ciągów, a następnie wstawia do wybranych pikseli obrazu, na podstawie obliczonego kroku. Odkodowanie działa na podobnej zasadzie
odczytując bity ukrytej wiadomości z najmniej znaczących bitów pikseli.

Moduły:
- `convertToBinary`  Zamienia wiadomość tekstową na postać binarną, z dodatkowym nagłówkiem zawierającym długość wiadomości.
- `convertToString`  Konwertuje wiadomość z formatu binarnego z powrotem na tekst.
- `convertImage`  Konwertuje obraz na macierz numpy w celu ułatwienia manipulacji.
- `calculateStep`  Oblicza krok, co ile pikseli będzie zakodowany bit wiadomości.
- `lsbCoding`  Koduje wiadomość w obrazie, zmieniając ostatnie bity wybranych pikseli.
- `lsbDecoding`  Odkodowuje wiadomość z obrazu, odczytując najmniej znaczące bity pikseli.
- `codeExampleMessage`  Przykład zakodowania wiadomości w obrazie.
"""

import math
import sys
import numpy as np
from PIL import Image


'''Konwertuje wiadomość tekstową na format binarny z nagłówkiem zawierającym długość wiadomości i krok.
Zwraca:
1. Nagłówek zakodowany w postaci binarnej (header_in_binary)
2. Zakodowaną wiadomość w postaci binarnej (message_in_binary)
'''
def convertToBinary(message, step):
    table_of_bin = []
    step = str(step)
    header = str((len(message)*7) + 77)  # Obliczenie długości wiadomości + 77 bitów (nagłówel)
    header_in_binary = ""
    message_in_binary = ""

    # Dodanie zer do długości i kroku, aby krok miał zawsze znaki, a długość 7
    while len(step) < 4:
        step = '0' + step
    while len(header) < 7:
        header = '0' + header

    header = step + header


    # Konwersja nagłówka do postaci binarnej
    for char in header:
        bin_repr = bin(ord(char))[2:].zfill(7)
        table_of_bin.append(bin_repr)

    for b in table_of_bin:
        header_in_binary += b

    table_of_bin = []
    
    # Konwersja wiadomości do posatci binarnej
    for char in message:
        bin_repr = bin(ord(char))[2:].zfill(7)
        table_of_bin.append(bin_repr)

    for b in table_of_bin:
        message_in_binary += b
    
    return header_in_binary, message_in_binary


'''Zamienia wiadomość z postaci binarnej na tekst
Zwraca:
- Wiadomość w postaci tekstowej'''
def convertToString(message_in_binary):
    table_of_strings = []
    message = ""
    for char in range(0, len(message_in_binary), 7):
        table_of_strings.append(chr(int(message_in_binary[char:char+7], 2)))

    for i in table_of_strings:
        message += i

    return message


# Konwertuje obraz na macierz numpy w celu manipulacji pikselami
def convertImage(path):
    img = Image.open(path)
    numpy_img = np.array(img)
    return img, numpy_img


'''Oblicza krok co ile pikseli zostaną zakodowane bity wiadomości.
Jeśli wiadomość jest za długa dla danego obrazu, zwraca błąd.
Zwraca:
- Obliczony krok.
'''
def calculateStep(message_size, img):
    if (message_size*7) > (img.size-77):
        raise ValueError("The message is too long to encode in this picture")
    return (img.size - 77) // (message_size*7)


'''Koduje wiadomość w obrazie poprzez zmianę najmniej znaczących bitów wybranych pikseli.
Zwraca:
1. Obraz zakodowany w formacie numpy
2. Obraz zakodowany w formacie PIL (do zapisu)
'''
def lsbCoding(img, message, header, step):
    shape = img.shape     # Kształt obrazu do przywrócenia po modyfikacji
    size = img.size       # Rozmiar obrazu
    resized_img = img.reshape(1, size)  # Zmiena obrazu na tablicę jednowymiarową
    pixel = 0              # Zmienna kontrolująca przemieszczanie się po pikselach 
    
    # Kodowanie nagłówka
    for bit in range(0, len(header)-1):
        if header[bit] == '0':
            resized_img[0, pixel] = resized_img[0, pixel] & ~1  # Wyzerowanie ostatniego bitu
        elif header[bit] == '1':
            resized_img[0, pixel] = resized_img[0, pixel] | 1   # Ustawia ostatni bit na 1
        else:
            print("Błąd")
        pixel += 1
    
    pixel += 1
    # Kodowanie wiadomości
    for bit in range(0, len(message)):
        if message[bit] == '0':
            resized_img[0, pixel] = resized_img[0, pixel] & ~1  # Wyzerowanie ostatniego bitu
        elif message[bit] == '1':
            resized_img[0, pixel] = resized_img[0, pixel] | 1   # Ustawia ostatni bit na 1
        else:
            print("Błąd")
        pixel += step

    new_img = resized_img.reshape(shape)  # Przywrócenie pierwotnego kształtu obrazu
    pil_image = Image.fromarray(new_img)  # Tworzenie obrazu w formacie PIL
    return new_img, pil_image


# Odkodowuje wiadomość z obrazu, czytając najmniej znaczące bity pikseli
def lsbDecoding(img_path):
    _, img = convertImage(img_path)
    message = ''
    resized_img = img.reshape(1, img.size)
    size_of_text = ''

    # Odczytanie nagłówka (77 bitów)
    for bit in range(0, 77):      # (2, 149, 3) - jeżeli chcemy zakodować wiadomość tylko w pikselach B (blue), wtedy należy zmeinić też pętlę poniżej (2, (size*3)+2, 3), a rakże w funkcji coding
        if resized_img[0, bit] % 2 == 0:
            size_of_text += '0'
        elif resized_img[0, bit] % 2 == 1:
            size_of_text += '1'
        else:
            print("Błąd")
    size = int(convertToString(size_of_text)[4:]) - 77
    step = int(convertToString(size_of_text)[:4])

    # Odczytanie ukrytej wiadomości
    for bit in range(77, (size*step)+77, step):
        if resized_img[0, bit] % 2 == 0:
            message += '0'
        elif resized_img[0, bit] % 2 == 1:
            message += '1'
        else:
            print("Błąd")
    return message 



def codeExampleMessage(path):
    message = "Lorem ipsum dolor sit amet, cibus nibh. uspendisse sit amet augue nibh. Suspendisse eget "
    _, img = convertImage(path)
    step = calculateStep(len(message), img)
    header_in_binary, message_in_binary= convertToBinary(message, step)
    _, stego_img = lsbCoding(img, message_in_binary, header_in_binary, step)
    stego_img.save("stego.png")
    return stego_img


def codeInputMessage(path): # do poprawki
    message = input("Enter message to code in the image: \n")
    message_in_binary, size_of_mess = convertToBinary(message)
    _, img = convertImage(path)
    _, stego_img = lsbCoding(img, message_in_binary)
    return stego_img


if __name__ == '__main__':
    # # message1 = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc at arcu lorem. Pellentesque iaculis, odio non volutpat consequat, velit lectus vehicula ipsum, a maximus metus tortor et metus. Donec massa elit, viverra id dignissim in, dignissim at ex. Suspendisse in faucibus nibh. Proin pretium sodales ante ut ultricies. Mauris vel diam iaculis, finibus tellus sit amet, convallis diam. Pellentesque et felis aliquam, finibus dolor at, commodo odio. In fringilla imperdiet lectus, eu rutrum ligula pulvinar nec. Sed malesuada tellus in sapien pellentesque pulvinar. Ut quis metus faucibus elit pretium aliquam. Vestibulum at nulla et risus tristique tincidunt. Nunc porttitor et eros feugiat consectetur. Suspendisse mauris elit, ultrices non risus nec, aliquet pretium purus. Vestibulum dignissim urna eget egestas porta. Aenean eget eros dapibus, fringilla nisi vel, tincidunt ex. Integer vitae vulputate nisi. Cras egestas sem lorem, vel maximus metus ultricies ac. Praesent lobortis egestas dignissim. Etiam porttitor faucibus erat. Curabitur dapibus sem at faucibus facilisis.Maecenas congue odio sed ultricies consectetur. Nullam venenatis orci ac diam maximus, nec elementum erat fermentum. Nullam nisl nibh, luctus id blandit at, luctus eu purus. Duis ultrices, velit eu consequat semper, arcu nisl dapibus elit, commodo egestas ante odio vitae justo. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Suspendisse libero lectus, condimentum a eleifend pellentesque, ultrices a mi. Nam eu mi vehicula, porttitor eros varius, dictum justo. In fringilla vel purus eu ultrices. Donec imperdiet, nulla eget aliquam aliquet, diam eros iaculis erat, at venenatis nunc magna sollicitudin erat. Donec diam odio, hendrerit nec fermentum eu, fermentum non eros. Suspendisse sit amet augue nibh. Suspendisse eget magna at orci malesuada porttitor id et eros."
    path = 'd:/STUDIA/Cyberka/Inzynierka/Proby/Zdjecia/16x16_mem.png'
    path_random = 'D:\STUDIA\Cyberka\Inzynierka\stego.png'
    codeExampleMessage(path)
    mess = lsbDecoding(path_random)
    print(convertToString(mess))

