import bencode as be
import hashlib
import os
import requests
import sys
import time

filename = 'testfiles/archlinux-2018.08.01-x86_64.iso.torrent'
torrent = be.filename_decode(filename)

info_hash = hashlib.sha1(be.encode(torrent[b'info']).encode('utf-8')).digest()
print(info_hash)

peer_id = str(hashlib.sha1(str(time.time() * os.getpid()).encode('utf-8')).digest())
print(peer_id)

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
print(be.string_decode(response.text))
