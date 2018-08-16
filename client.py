import asyncio
import bencode as be
import hashlib
import io
import os
import requests
import sys
import time

## Unique machine ID: PEER_ID
PID = os.getpid()
CURTIME = time.time()
PEER_ID = hashlib.sha1(bytes(str(int(CURTIME*PID)).encode())).digest()

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
        'peer_id': PEER_ID, # 20 byte SHA1 hash of machineID (timestamp+pid?)
        'port': port, # 6881-6889 (usually); give up if can't establish port in range
        'uploaded': ul_bytes, # amount uploaded since start in base ten ASCII (total bytes)
        'downloaded': dl_bytes, # amount downloaded since start in base ten ASCII (total bytes)
        'left': torrent.total_bytes - dl_bytes, # amount left to download, base ten ASCII (total bytes remaining)
        'compact': 1, # 1 to accept: peers_list -> peers_string w/ 6 bytes per peer -- 4:host+2:port (network byte order)
        'no_PEER_ID': '', # ignored w/ compact mode
        'event': event # must be 'started', 'stopped', 'completed', or ''
    }

    announce = torrent.torrent_hash[b'announce'].decode()
    response = requests.get(announce, params=request_params)
    response = be.raw_decode(response.content)
    peers = compact_peers_decode(response[b'peers'])

    return peers

async def peer_connection(peer, torrent, loop):
    # peer => tuple(host, port)
    host, port = peer
    # host = '127.0.0.1'
    # port = 8888

    pstr = b'BitTorrent protocol'
    pstrlen = bytes([len(pstr)])
    reserved = bytearray(8)

    peer_handshake = pstrlen+pstr+reserved+torrent.info_hash+PEER_ID

    print(f"waiting for connection with peer: {peer}")
    reader, writer = await asyncio.open_connection(host, port, loop=loop)
    print("connected")



    writer.write(peer_handshake)
    print(f"waiting for write with peer: {peer}")
    await writer.drain()
    print(f"waiting for response from peer: {peer}")
    response = await reader.read(1024)
    writer.close()
    return response

    # import socket
    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #     s.connect((host, port))
    #     s.sendall(peer_handshake)
    #     response = s.recv(1024)
    # return response

def valid_handshake(handshake_response, torrent):
    return {
        handshake_response
        and torrent.info_hash in handshake_response
    }

async def bt_client(peers, loop, torrent):
    # for peer in peers:
        # p = (peer, peers[peer])
    # try:
        responses = await asyncio.gather(*[peer_connection((peer, peers[peer]), torrent, loop) for peer in peers])
        print(f'responses from peers: {responses}')
        # handshake_response = await peer_connection(p, torrent, loop)
        # if valid_handshake(handshake_response, torrent):
        #     confirmed_peers.append(handshake_response)
    # except (ConnectionRefusedError, TimeoutError):
    #     continue

def main():

    # filename = 'torrentfiles/archlinux-2018.08.01-x86_64.iso.torrent'
    filename = 'torrentfiles/ubuntu-18.04.1-desktop-amd64.iso.torrent'
    torrent = Torrent(filename)
    event = 'started'
    uploaded_bytes = 0
    downloaded_bytes = 0
    peers = send_tracker_request(torrent, uploaded_bytes, downloaded_bytes, event)
    confirmed_peers = []
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bt_client(peers, loop, torrent))
    loop.close()
    print(f'peer responses: {confirmed_peers}')

if __name__ == '__main__':
    main()
