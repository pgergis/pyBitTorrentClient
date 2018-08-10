import sys
sys.path.insert(0, '..')

from bencode import encode, decode, string_decode, filename_decode
import unittest

if __name__ == '__main__':
    # Tests
    decode_values = [
        ('4:spam', 'spam'),
        ('0:', ''),
        ('i3e', 3),
        ('i-3e', -3),
        ('i0e', 0),
        # ('i-0e', 0), # Should Error
        # ('i03e', 3), # Should Error
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

    test_num = 1
    for be_out, initial in decode_values:
        print("TEST #%d" %test_num)
        r = encode(initial)
        if r == be_out:
            print("PASSED")
        else:
            print(f"FAILED\n\tExpected: {be_out}\n\tGot: {r}")
        test_num += 1

    filename = 'testfiles/ubuntu-18.04.1-desktop-amd64.iso.torrent'
    torrent = filename_decode(filename)
    # print(torrent)
    print(torrent[b'announce'])
    print(torrent.keys())
    print(torrent[b'info'].keys())

    with open(filename, 'rb') as fd:
        torrent = decode(fd)
    print(torrent[b'announce'] == string_decode(encode(torrent[b'announce'])))

    with open(filename, 'rb') as fd:
        while 1:
            pos = int(input())
            print(f'file position: {fd.tell()}')
            print(f'char after reading {pos}: {fd.read(pos)}')
