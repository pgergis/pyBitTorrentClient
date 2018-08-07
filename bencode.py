import io

def _str_decode(string_buf, str_len):
    char = string_buf.read(1)
    if char == ':':
        return string_buf.read(str_len)
    else:
        try:
            str_len = int(str(str_len) + char)
            return _str_decode(string_buf, str_len)
        except ValueError:
            print(f"Malformed bencode str: {str(str_len) + char}")

def _int_decode(string_buf):
    num_digits = []
    char = string_buf.read(1)
    while char and char != 'e':
        num_digits.append(char)
        char = string_buf.read(1)
    try:
        num = int(''.join(num_digits))
        return num
    except ValueError:
        print(f"Malformed bencode int: {str_num}")

def _list_decode(string_buf, be_list):
    e = _decode(string_buf)
    if e:
        be_list.append(e)
        return _list_decode(string_buf, be_list)
    else:
        return be_list

def _dict_decode(string_buf, be_dict, key):
    if key:
        value = _decode(string_buf)
        be_dict[key] = value
        key = ""
    else:
        key = _decode(string_buf)
        if not key:
            return be_dict
    return _dict_decode(string_buf, be_dict, key)

def _decode(string_buf):
    char = string_buf.read(1)
    if char == 'i':
        return _int_decode(string_buf)
    elif char == 'l':
        return _list_decode(string_buf,[])
    elif char == 'd':
        return _dict_decode(string_buf,{},'')
    elif char == 'e':
        return ''
    elif char == '':
        return ''
    else:
        try:
            strlen = int(char)
            return _str_decode(string_buf, strlen)
        except ValueError:
            print(f"Malformed bencode input: {c}")

def filename_decode(filename):
    with open(filename, 'r', encoding='latin1') as f:
        s = f.read()
    return string_decode(s)

def string_decode(string):
    with io.StringIO(string) as s:
        result = _decode(s)
    return result

if __name__ == '__main__':
    # Tests
    decode_values = [
        ('4:spam', 'spam'),
        ('0:', ''),
        ('i3e', 3),
        ('i-3e', -3),
        ('i0e', 0),
        ('i-0e', 0), # Should Error
        ('i03e', 3), # Should Error
        ('l4:spam4:eggse', ["spam", "eggs"]),
        ('le', []),
        ('d3:cow3:moo4:spam4:eggse', {'cow': 'moo', 'spam': 'eggs'}),
        ('d4:spaml1:a1:bee', {'spam': ['a', 'b']}),
        ('de', {}),
    ]

    test_num = 1
    for be_in, expected in decode_values:
        print("TEST #%d" %test_num)
        r = string_decode(be_in)
        if r == expected:
            print("PASSED")
        else:
            print(f"FAILED\n\tExpected: {expected}\n\tGot: {r}")
        test_num += 1
