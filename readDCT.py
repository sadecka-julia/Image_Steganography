from dct import prepareImage, zigZagEncoding, dctTransformation


def convertToStringDCT(message_in_binary):
    table_of_strings = []
    message = ""
    for char in range(0, len(message_in_binary), 7):
        table_of_strings.append(chr(int(message_in_binary[char:char+7], 2)))

    for i in table_of_strings:
        message += i

    # print(message)
    return message

def extractBitsFromImage(image_path, mess_lenght):
    # Dzieli na bloki 8x8 i odejmuje 128
    blocks = prepareImage(image_path)
    dct_blocks = dctTransformation(blocks)
    bit_index = 0
    extracted_bits = ''
    height, width = dct_blocks.shape[:2]

    for i in range(height):
        for j in range(width):
            for channel in range(3):
                if channel in [2]:
                    if bit_index >= mess_lenght:
                        print("Finished extracting all bits")
                        return extracted_bits
                    
                    block = dct_blocks[i, j, :, :, channel]
                    # zigzag = zigZagEncoding(block)
                    value = int(dct_blocks[i, j, 0, 0, channel])
                    if (value%6) in [4, 5, 0]:
                        bit = 0
                    else:
                        bit = 1

                    # idx = 0


                    extracted_bits += str(bit)
                    # print(f"Extracted bit {value % 2} from position ({i}, {j}, {channel}), coefficient {value}")

                    bit_index += 1

    return extracted_bits

def dctDecoding(stego_path):
    bits = extractBitsFromImage(stego_path, 448)
    mess = convertToStringDCT(bits)
    return mess


if __name__ == '__main__':
    path = 'D:\STUDIA\Cyberka\Inzynierka\Proby\Zdjecia\stego.png'
    # bits = extractBitsFromImage(path, 126)
    # mess = convertToString(bits)
    mess = dctDecoding(path)
    print("Decoded message: ", mess)
