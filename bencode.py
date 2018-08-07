import io

############################
# Encode to bencode format #
############################

def _str_encode(string):
    str_len = len(string)
    return f'{str_len}:{string}'

def _int_encode(num):
    return f'i{num}e'

def _list_encode(std_list):
    be_list = 'l' + ''.join([encode(item) for item in std_list]) + 'e'
    return be_list

def _dict_encode(std_dict):
    be_dict = 'd' + ''.join([f'{encode(key)}{encode(std_dict[key])}' for key in std_dict])+ 'e'
    return be_dict

def encode(item):
    if isinstance(item, int):
        return _int_encode(item)
    if isinstance(item, list):
        return _list_encode(item)
    if isinstance(item, dict):
        return _dict_encode(item)
    if isinstance(item, str):
        return _str_encode(item)

    return ValueError("Input invalid for bencoding")

##########################################
###### Decode from bencode format ########
#                                        #
### Support for file and string decoding #
##########################################

def _str_decode(fd, str_len):
    len_digits = [str(str_len)]
    char = fd.read(1)
    while char != ':':
        len_digits.append(char)
        char = fd.read(1)
    try:
        str_len = int(''.join(len_digits))
    except ValueError:
        print(f"Malformed bencode str: {''.join(len_digits)}")
    return fd.read(str_len)

def _int_decode(fd):
    num_digits = []
    char = fd.read(1)
    while char and char != 'e':
        num_digits.append(char)
        char = fd.read(1)
    try:
        num = int(''.join(num_digits))
        return num
    except ValueError:
        print(f"Malformed bencode int: {str_num}")

def _list_decode(fd):
    be_list = []
    e = decode(fd)
    while e:
        be_list.append(e)
        e = decode(fd)
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
    if char == 'i':
        return _int_decode(fd)
    elif char == 'l':
        return _list_decode(fd)
    elif char == 'd':
        return _dict_decode(fd)
    elif char == 'e':
        return ''
    elif char == '':
        return ''
    else:
        try:
            strlen = int(char)
            return _str_decode(fd, strlen)
        except ValueError:
            print(f"Malformed bencode input: {char}")

def filename_decode(filename):
    with open(filename, 'r', encoding='latin1') as f:
        s = f.read()
    return string_decode(s)

def string_decode(string):
    with io.StringIO(string) as s:
        result = decode(s)
    return result
