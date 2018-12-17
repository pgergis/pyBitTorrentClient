import unittest
from bencode import encode, decode, filename_decode, raw_decode

class TestBencode(unittest.TestCase):
    string_bencode_to_actual_pairs = {
        '4:spam': b'spam',
        '12:hello, world': b'hello, world',
        '0:': b'',
        'i3e': 3,
        'i-100e': -100,
        'i0e': 0,
        # 'i-0e': ValueError,
        # 'i03e': ValueError,
        'l4:spam4:eggse': [b"spam", b"eggs"],
        'le': [],
        'd3:cow3:moo4:spam4:eggse': {b'cow': b'moo', b'spam': b'eggs'},
        'd4:spaml1:a1:bee': {b'spam': [b'a', b'b']},
        'de': {},
    }
    byte_bencode_to_actual_pairs = {
        b'4:spam': b'spam',
        b'12:hello, world': b'hello, world',
        b'0:': b'',
        b'i3e': 3,
        b'i-100e': -100,
        b'i0e': 0,
        # b'i-0e': ValueError,
        # b'i03e': ValueError,
        b'l4:spam4:eggse': [b"spam", b"eggs"],
        b'le': [],
        b'd3:cow3:moo4:spam4:eggse': {b'cow': b'moo', b'spam': b'eggs'},
        b'd4:spaml1:a1:bee': {b'spam': [b'a', b'b']},
        b'de': {},
    }
    filenames = [
        "torrentfiles/archlinux-2018.08.01-x86_64.iso.torrent",
        "torrentfiles/ubuntu-18.04.1-desktop-amd64.iso.torrent",
    ]

    def test_from_bencode_str(self):
        tester = self.string_bencode_to_actual_pairs
        for bencoded in tester:
            self.assertEqual(raw_decode(bencoded), tester[bencoded])

    def test_from_bencode_byte(self):
        tester = self.byte_bencode_to_actual_pairs
        for bencoded in tester:
            self.assertEqual(raw_decode(bencoded), tester[bencoded])

    def test_to_bencode(self):
        tester = self.byte_bencode_to_actual_pairs
        for bencoded in tester:
            self.assertEqual(bencoded, encode(tester[bencoded]))

    def test_decode_by_filename(self):
        for name in self.filenames:
            with open(name, 'rb') as f:
                d1 = filename_decode(name)
                f.seek(0)
                d2 = raw_decode(f.read())
                self.assertEqual(d1, d2)

    def test_decode_open_file(self):
        for name in self.filenames:
            with open(name, 'rb') as f:
                d1 = decode(f)
                f.seek(0)
                d2 = raw_decode(f.read())
                self.assertEqual(d1, d2)

if __name__ == '__main__':
    unittest.main()
