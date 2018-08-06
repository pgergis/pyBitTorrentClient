import io

def strdecode(s, slen):
    c = s.read(1)
    if c == ':':
        return s.read(slen)
    else:
        try:
            slen = int(str(slen) + c)
            return strdecode(s, slen)
        except ValueError:
            print("Malformed bencode str: %s" %(str(slen) + c))

def intdecode(s):
    strn = ""
    c = s.read(1)
    while c and c != 'e':
        strn += c
        c = s.read(1)
    try:
        n = int(strn)
        return n
    except ValueError:
        print("Malformed bencode int: %s" %(strn))

def listdecode(s, l):
    e = decode(s)
    if e:
        l.append(e)
        return listdecode(s, l)
    else:
        return l

def dictdecode(s, d, key):
    if key:
        value = decode(s)
        d[key] = value
        key = ""
    else:
        key = decode(s)
        if not key:
            return d
    return dictdecode(s, d, key)

def decode(s):
    c = s.read(1)
    if c == 'i':
        return intdecode(s)
    elif c == 'l':
        return listdecode(s,[])
    elif c == 'd':
        return dictdecode(s,{},'')
    elif c == 'e':
        return ''
    elif c== '':
        return ''
    else:
        try:
            strlen = int(c)
            return strdecode(s, strlen)
        except ValueError:
            print("Malformed bencode input: %s" %c)

def fdecode(filename):
    f = open(filename, 'r', encoding='latin1')
    s = f.read()
    f.close()
    return sdecode(s)

def sdecode(string):
    s = io.StringIO(string)
    result = decode(s)
    s.close()
    return result

if __name__ == '__main__':
    # Tests
    decode_values = [
        ['4:spam', 'spam'],
        ['0:', ''],
        ['i3e', 3],
        ['i-3e', -3],
        ['i0e', 0],
        # ['i-0e', 0], # Should Error
        # ['i03e', 3], # Should Error
        ['l4:spam4:eggse', ["spam", "eggs"]],
        ['le', []],
        ['d3:cow3:moo4:spam4:eggse', {'cow': 'moo', 'spam': 'eggs'}],
        ['d4:spaml1:a1:bee', {'spam': ['a', 'b']}],
        ['de', {}],
    ]

    test_num = 1
    for t in decode_values:
        print("TEST #%d" %test_num)
        r = sdecode(t[0])
        if r == t[1]:
            print("PASSED")
        else:
            print("FAILED\nExpected: %s\nGot: %s" %(str(t[1]), str(r)))
        test_num += 1
