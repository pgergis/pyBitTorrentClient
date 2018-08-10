import io

############################
# Encode to bencode format #
############################

def _str_encode(string):
    str_len = len(string)
    return b'%d:%b' %(str_len, string)

def _int_encode(num):
    return b'i%de' %(num)

def _list_encode(std_list):
    be_list = b'l' + b''.join([encode(item) for item in std_list]) + b'e'
    return be_list

def _dict_encode(std_dict):
    byte_dict = b'd'
    for key in std_dict:
        byte_dict += encode(key)
        byte_dict += encode(std_dict[key])
    byte_dict += b'e'
    return byte_dict

def encode(item):
    if isinstance(item, int):
        return _int_encode(item)
    if isinstance(item, list):
        return _list_encode(item)
    if isinstance(item, dict):
        return _dict_encode(item)
    # if isinstance(item, str):
    #     return _str_encode(item)
    if isinstance(item, bytes):
        return _str_encode(item)

    return ValueError(f"Input invalid for bencoding: {item}")

##########################################
###### Decode from bencode format ########
#                                        #
### Support for file and string decoding #
##########################################

def _str_decode(fd, str_len):
    len_digits = [str(str_len)]
    char = fd.read(1)
    while char and char != b':':
        len_digits.append(char.decode())
        char = fd.read(1)
    try:
        str_len = int(''.join(len_digits))
    except ValueError:
        print(f"Malformed bencode str: {''.join(len_digits)}")
    return fd.read(str_len)

def _int_decode(fd):
    num_digits = []
    char = fd.read(1)
    while char and char != b'e':
        num_digits.append(char)
        char = fd.read(1)
    try:
        num = int(b''.join(num_digits))
        return num
    except ValueError:
        print(f"Malformed bencode int: {num_digits}")

def _list_decode(fd):
    be_list = []
    element = decode(fd)
    while element:
        be_list.append(element)
        element = decode(fd)
    return be_list

def _dict_decode(fd):
    be_dict = {}
    key = ""
    value = ""
    while not key or not value:
        if key:
            value = decode(fd)
            be_dict[key] = value
            key = ""
            value = ""
        else:
            key = decode(fd)
            if not key:
                return be_dict

def decode(fd):
    char = fd.read(1)
    if char == b'i':
        return _int_decode(fd)
    elif char == b'l':
        return _list_decode(fd)
    elif char == b'd':
        return _dict_decode(fd)
    elif char == b'e' or char == b'':
        return None
    else:
        try:
            strlen = int(char)
            return _str_decode(fd, strlen) #.decode()
        except ValueError:
            print(f"Malformed bencode input at position {fd.tell()-1}: {char}")

def filename_decode(filename):
    with open(filename, 'rb') as f:
        result = decode(f)
    return result

def string_decode(string):
    if isinstance(string, str):
        string = bytes(string, encoding='utf-8')
    elif not isinstance(string, bytes):
        raise ValueError('Invalid input: Use this to decode string or bytes')

    with io.BytesIO(string) as s:
        result = decode(s)
    return result
