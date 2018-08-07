import bencode as be
import requests

if __name__ == '__main__':
    filename = 'test/ubuntu-18.04.1-desktop-amd64.iso.torrent'
    torrent = be.filename_decode(filename)
    print(torrent['announce'])
    print(torrent.keys())
    print(torrent['info'].keys())
