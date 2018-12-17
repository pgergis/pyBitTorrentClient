import bencode as be
import hashlib
import io
import logging
import os
import requests
import sys
import time
import trio

logging.getLogger().setLevel(logging.INFO)

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

async def peer_handshake(torrent_info, stream):
    logging.info("started handshake")
    pstr = b'BitTorrent protocol'
    pstrlen = bytes([len(pstr)])
    reserved = bytearray(8)

    peer_handshake = pstrlen+pstr+reserved+torrent_info+PEER_ID

    await stream.send_all(peer_handshake)
    response = await stream.receive_some(1024)
    return response

def valid_handshake(handshake_response, torrent_info):
    return {
        handshake_response
        and torrent_info in handshake_response
    }

async def download_from_peer(peer, torrent):
    # peer => tuple(host, port)
    host, port = peer
    logging.info("connecting to peer: {}:{}".format(host, port))
    try:
        stream = await trio.open_tcp_stream(host, port)
        async with stream:
            handshake_response = await peer_handshake(torrent.info_hash, stream)
            if not valid_handshake(handshake_response, torrent.info_hash):
                stream.aclose()
            else:
                logging.info("valid handshake from peer {}:{}".format(host,port))
                stream.aclose()

    except OSError:
        logging.error("failed to connect to peer: {}:{}".format(host, port))

async def download(peers, torrent):
    async with trio.open_nursery() as nursery:
        for peer in peers:
            p = (peer, peers[peer])
            nursery.start_soon(download_from_peer, p, torrent)
    logging.info('finished downloading!')

def main():

    # filename = 'torrentfiles/archlinux-2018.09.01-x86_64.iso.torrent'
    filename = 'torrentfiles/ubuntu-18.04.1-desktop-amd64.iso.torrent'
    torrent = Torrent(filename)
    event = 'started'
    uploaded_bytes = 0
    downloaded_bytes = 0
    peers = send_tracker_request(torrent, uploaded_bytes, downloaded_bytes, event)
    trio.run(download, peers, torrent)

if __name__ == '__main__':
    main()
