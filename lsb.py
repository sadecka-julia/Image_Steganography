"""
Ten skrypt implementuje klasyczną metodę ukrywania wiadomości w obrazach przy użyciu algorytmu LSB (Least Significant Bit).
Koduje wiadomość w ostatnich bitach pikseli obrazu, a następnie umożliwia jej odkodowanie.

Moduły:
- `convertToBinary`  Konwertuje wiadomość na format binarny.
- `convertToString`  Odtwarza wiadomość z postaci binarnej.
- `convertImage`  Konwertuje obraz na macierz numpy do manipulacji pikselami.
- `lsbCoding`  Ukrywa binarną wiadomość w ostatnich bitach pikseli obrazu.
- `lsbDecoding`  Odczytuje ukrytą wiadomość z obrazu.
"""

import numpy as np
from PIL import Image


'''Zamienia wiadomość tekstową na binarną, aby mogła być zakodowana w pikselach obrazu.
Zwraca:
- Zakodowaną wiadomość w postaci binarnej.
'''
def convertToBinary(message):
    table_of_bin = []
    len_of_message = str((len(message)*7) + 49)
    message_in_binary = ""
    while len(len_of_message) < 7:
        len_of_message = '0' + len_of_message
    message = len_of_message + message

    # Konwersja każdego znaku do formatu binarnego
    for char in message:
        bin_repr = bin(ord(char))[2:].zfill(7)
        table_of_bin.append(bin_repr)

    for b in table_of_bin:
        message_in_binary += b

    return message_in_binary


'''Zamienia binarną wiadomość na tekst.
Zwraca:
- Wiadomość w postaci tekstowej.
'''
def convertToString(message_in_binary):
    table_of_strings = []
    message = ""
    for char in range(0, len(message_in_binary), 7):
        table_of_strings.append(chr(int(message_in_binary[char:char+7], 2)))

    for i in table_of_strings:
        message += i

    return message


# Konwertuje obraz do macierzy numpy w celu manipulacji pikselami
def convertImage(path):
    img = Image.open(path)
    numpy_img = np.array(img)
    return img, numpy_img


'''Koduje wiadomość w obrazie poprzez zastąpienie ostatnich bitów pikseli obrazem binarnej wiadomości.
Zwraca:
1. Zakodowany obraz w formacie numpy
2. Zakodowany obraz w formacie PIL (do zapisu)
'''
def lsbCoding(img, message):
    shape = img.shape     # Kształt obrazu
    size = img.size       # Rozmiar obrazu
    resized_img = img.reshape(size)  # Zmienia macierz obrazu, aby była była jednowymiarowa
    pixel = 0             # Zmienna kontrolująca przesuwanie się po pikselach 
    for bit in range(0, len(message)-1):
        if bit >= len(resized_img):
            new_img = resized_img.reshape(shape)
            pil_image = Image.fromarray(new_img)
            return new_img, pil_image
        if message[bit] == '0':
            resized_img[pixel] = resized_img[pixel] & ~1  # Wyzerowanie ostatniego bitu
        elif message[bit] == '1':
            resized_img[pixel] = resized_img[pixel] | 1   # Ustawienie ostatniego bitu na 1
        else:
            print("Błąd")
        pixel += 1

    new_img = resized_img.reshape(shape)
    pil_image = Image.fromarray(new_img)
    return new_img, pil_image


'''Odczytuje zakodowaną wiadomość z obrazu, czytając ostatnie bity pikseli.
Zwraca:
- Wiadomość w postaci binarnej.
'''
def lsbDecoding(img_path):
    _, img = convertImage(img_path)
    message = ''
    resized_img = img.reshape(1, img.size)
    size_of_text = ''

    # Odczyt wiadomości z pikseli
    for bit in range(0, 49):      # (2, 149, 3) - jeżeli chcemy zakodować wiadomość tylko w pikselach B (blue), wtedy należy zmeinić też pętlę poniżej (2, (size*3)+2, 3), a rakże w funkcji coding
        if resized_img[0, bit] % 2 == 0:
            size_of_text += '0'
        elif resized_img[0, bit] % 2 == 1:
            size_of_text += '1'
        else:
            print("Błąd")
    size = int(convertToString(size_of_text))

    # Odczyt ukrytej wiadomości
    for bit in range(0, size):
        if resized_img[0, bit] % 2 == 0:
            message += '0'
        elif resized_img[0, bit] % 2 == 1:
            message += '1'
        else:
            print("Błąd")
    return message[49:]


# Funkcja zakodowująca przykładową wiadomość w obrazie i zapisująca wynik do pliku
def codeExampleMessage(path):
    message = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc at arcu lorem. Pellentesque iaculis, odio non volutpat consequat, velit lectus vehicula ipsum, a maximus metus tortor et metus. Donec massa elit, viverra id dignissim in, dignissim at ex. Suspendisse in faucibus nibh. Proin pretium sodales ante ut ultricies. Mauris vel diam iaculis, finibus tellus sit amet, convallis diam. Pellentesque et felis aliquam, finibus dolor at, commodo odio. In fringilla imperdiet lectus, eu rutrum ligula pulvinar nec. Sed malesuada tellus in sapien pellentesque pulvinar. Ut quis metus faucibus elit pretium aliquam. Vestibulum at nulla et risus tristique tincidunt. Nunc porttitor et eros feugiat consectetur. Suspendisse mauris elit, ultrices non risus nec, aliquet pretium purus. Vestibulum dignissim urna eget egestas porta. Aenean eget eros dapibus, fringilla nisi vel, tincidunt ex. Integer vitae vulputate nisi. Cras egestas sem lorem, vel maximus metus ultricies ac. Praesent lobortis egestas dignissim. Etiam porttitor faucibus erat. Curabitur dapibus sem at faucibus facilisis.Maecenas congue odio sed ultricies consectetur. Nullam venenatis orci ac diam maximus, nec elementum erat fermentum. Nullam nisl nibh, luctus id blandit at, luctus eu purus. Duis ultrices, velit eu consequat semper, arcu nisl dapibus elit, commodo egestas ante odio vitae justo. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Suspendisse libero lectus, condimentum a eleifend pellentesque, ultrices a mi. Nam eu mi vehicula, porttitor eros varius, dictum justo. In fringilla vel purus eu ultrices. Donec imperdiet, nulla eget aliquam aliquet, diam eros iaculis erat, at venenatis nunc magna sollicitudin erat. Donec diam odio, hendrerit nec fermentum eu, fermentum non eros. Suspendisse sit amet augue nibh. Suspendisse eget magna at orci malesuada porttitor id et eros."
    message_in_binary = convertToBinary(message)
    _, img = convertImage(path)
    print(len(message), len(message_in_binary))
    _, stego_img = lsbCoding(img, message_in_binary)
    return stego_img

def codeInputMessage():
    message = input("Enter message to code in the image: \n")
    message_in_binary = convertToBinary(message)
    _, img = convertImage(path)
    _, stego_img = lsbCoding(img, message_in_binary)
    return stego_img


if __name__ == '__main__':
    message1 = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc at arcu lorem. Pellentesque iaculis, odio non volutpat consequat, velit lectus vehicula ipsum, a maximus metus tortor et metus. Donec massa elit, viverra id dignissim in, dignissim at ex. Suspendisse in faucibus nibh. Proin pretium sodales ante ut ultricies. Mauris vel diam iaculis, finibus tellus sit amet, convallis diam. Pellentesque et felis aliquam, finibus dolor at, commodo odio. In fringilla imperdiet lectus, eu rutrum ligula pulvinar nec. Sed malesuada tellus in sapien pellentesque pulvinar. Ut quis metus faucibus elit pretium aliquam. Vestibulum at nulla et risus tristique tincidunt. Nunc porttitor et eros feugiat consectetur. Suspendisse mauris elit, ultrices non risus nec, aliquet pretium purus. Vestibulum dignissim urna eget egestas porta. Aenean eget eros dapibus, fringilla nisi vel, tincidunt ex. Integer vitae vulputate nisi. Cras egestas sem lorem, vel maximus metus ultricies ac. Praesent lobortis egestas dignissim. Etiam porttitor faucibus erat. Curabitur dapibus sem at faucibus facilisis.Maecenas congue odio sed ultricies consectetur. Nullam venenatis orci ac diam maximus, nec elementum erat fermentum. Nullam nisl nibh, luctus id blandit at, luctus eu purus. Duis ultrices, velit eu consequat semper, arcu nisl dapibus elit, commodo egestas ante odio vitae justo. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Suspendisse libero lectus, condimentum a eleifend pellentesque, ultrices a mi. Nam eu mi vehicula, porttitor eros varius, dictum justo. In fringilla vel purus eu ultrices. Donec imperdiet, nulla eget aliquam aliquet, diam eros iaculis erat, at venenatis nunc magna sollicitudin erat. Donec diam odio, hendrerit nec fermentum eu, fermentum non eros. Suspendisse sit amet augue nibh. Suspendisse eget magna at orci malesuada porttitor id et eros."
    message = 'a a1'
    message_in_binary = convertToBinary(message)
    # print(table_of_bin, message_in_binary)
    # print(convertToString("10010001100101110110011011001101111"))
    message_in_binary1 = convertToString(message_in_binary)

    # print("Przetlumaczona wiadomosc: ", message_in_binary1)
    path = 'd:/STUDIA/Cyberka/Inzynierka/Proby/Zdjecia/mini_mem.png'

    codeExampleMessage(path)


    # # starter = np.zeros((10, 10, 3)) # 42 znaki
    # _, img = convertImage(path)
    # img_with_info, stego_img = lsbCoding(img, message_in_binary)
    # stego_img.save("wiadomosc1.png")
    # # np.set_printoptions(threshold=sys.maxsize)
    # # print("Img with info\n", img_with_info[0:1, 0:15])
    # stego_path = 'D:\STUDIA\Cyberka\Inzynierka\wiadomosc1.png' # jpg zmienia obraz, że nie da się późneij go odczytać
    # _, stego = convertImage(stego_path)
    # # stego = np.array(stego_img)
    # hide_massage = lsbDecoding(stego_path)

