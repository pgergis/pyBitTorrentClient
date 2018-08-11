import bencode as be
import hashlib
import io
import os
import requests
import sys
import time

## Unique machine ID: peer_id
pid = os.getpid()
curtime = time.time()
peer_id = hashlib.sha1(bytes(str(int(curtime*pid)).encode())).digest()
print(peer_id)

class Torrent(object):
    def __init__(self, filename):
        self.torrent_hash = be.filename_decode(filename)
        self.info_hash = hashlib.sha1(be.encode(self.torrent_hash[b'info'])).digest()

        self.total_bytes = 0
        try:
            for f in self.torrent_hash[b'info'][b'files']:
                self.total_bytes += f[b'length']
        except KeyError:
            self.total_bytes += self.torrent_hash[b'info'][b'length']


def compact_peers_decode(peer_bytes):
    peers = {}
    with io.BytesIO(peer_bytes) as b:
        peer = b.read(6)
        while len(peer) == 6:
            ip = '.'.join([str(int(n)) for n in peer[:4]])
            port = int.from_bytes(peer[4:6], 'big')
            peers[ip] = port
            peer = b.read(6)
    if len(peer) != 0:
        raise Exception(f'{len(peer)} residual peer bytes')
    return peers

def send_tracker_request(torrent, ul_bytes, dl_bytes, event='', port=6885, compact=1, no_peer_id=''):
    request_params = {
        'info_hash': torrent.info_hash, # 20-byte SHA1 hash of torrent[info]
        'peer_id': peer_id, # 20 byte SHA1 hash of machineID (timestamp+pid?)
        'port': port, # 6881-6889 (usually); give up if can't establish port in range
        'uploaded': ul_bytes, # amount uploaded since start in base ten ASCII (total bytes)
        'downloaded': dl_bytes, # amount downloaded since start in base ten ASCII (total bytes)
        'left': torrent.total_bytes - dl_bytes, # amount left to download, base ten ASCII (total bytes remaining)
        'compact': 1, # 1 to accept: peers_list -> peers_string w/ 6 bytes per peer -- 4:host+2:port (network byte order)
        'no_peer_id': '', # ignored w/ compact mode
        'event': event # must be 'started', 'stopped', 'completed', or ''
    }

    announce = torrent.torrent_hash[b'announce'].decode()
    response = requests.get(announce, params=request_params)
    response = be.string_decode(response.content)
    peers = compact_peers_decode(response[b'peers'])
    return peers

def main():

    filename = 'testfiles/archlinux-2018.08.01-x86_64.iso.torrent'
    torrent = Torrent(filename)
    event = 'started'
    uploaded_bytes = 0
    downloaded_bytes = 0
    print(send_tracker_request(torrent, uploaded_bytes, downloaded_bytes, event))



if __name__ == '__main__':
    main()
