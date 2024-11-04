from dct import prepareImage, zigZagEncoding, dctTransformation


def convertToString(message_in_binary):
    table_of_strings = []
    message = ""
    for char in range(0, len(message_in_binary), 7):
        table_of_strings.append(chr(int(message_in_binary[char:char+7], 2)))

    for i in table_of_strings:
        message += i

    # print(message)
    return message