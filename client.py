import bencode as be
import hashlib
import io
import os
import requests
import sys
import time

def compact_peers_decode(peer_bytes):
    peers = {}
    with io.BytesIO(peer_bytes) as b:
        peer = b.read(6)
        while len(peer) == 6:
            ip = int.from_bytes(peer[:4], 'big')
            port = int.from_bytes(peer[4:6], 'big')
            peers[ip] = port
            peer = b.read(6)
    if len(peer) != 0:
        raise Exception(f'{len(peer)} residual peer bytes')
    print(peers)

def main():

    filename = 'testfiles/archlinux-2018.08.01-x86_64.iso.torrent'
    torrent = be.filename_decode(filename)

    # print(torrent[b'info'])
    info_hash = hashlib.sha1(be.encode(torrent[b'info'])).digest()
    print(info_hash)

    curtime = time.time()
    pid = os.getpid()
    myid = int(curtime * pid)
    myid = bytes(str(myid).encode())
    peer_id = hashlib.sha1(myid).digest()
    # print(peer_id)

    port = 6885

    ul_bytes = 0

    dl_bytes = 0

    total_bytes = 0
    try:
        for f in torrent[b'info'][b'files']:
            total_bytes += f[b'length']
    except KeyError:
        total_bytes += torrent[b'info'][b'length']

    event = 'started'

    request_params = {
        'info_hash': info_hash, # 20-byte SHA1 hash of torrent[info]
        'peer_id': peer_id, # 20 byte SHA1 hash of machineID (timestamp+pid?)
        'port': port, # 6881-6889 (usually); give up if can't establish port in range
        'uploaded': ul_bytes, # amount uploaded since start in base ten ASCII (total bytes)
        'downloaded': dl_bytes, # amount downloaded since start in base ten ASCII (total bytes)
        'left': total_bytes - dl_bytes, # amount left to download, base ten ASCII (total bytes remaining)
        'compact': 1, # 1 to accept: peers_list -> peers_string w/ 6 bytes per peer -- 4:host+2:port (network byte order)
        'no_peer_id': '', # ignored w/ compact mode
        'event': event # must be 'started', 'stopped', 'completed', or ''
    }

    announce = torrent[b'announce'].decode()
    print(announce)
    response = requests.get(announce, params=request_params)
    response = be.string_decode(response.content)
    compact_peers_decode(response[b'peers'])


if __name__ == '__main__':
    main()
