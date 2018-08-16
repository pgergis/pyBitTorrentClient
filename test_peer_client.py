import asyncio

PID = os.getpid()
CURTIME = time.time()
PEER_ID = hashlib.sha1(bytes(str(int(CURTIME*PID)).encode())).digest()

class EchoClientProtocol(asyncio.Protocol):
    def __init__(self, message, loop):
        self.message = message
        self.loop = loop

    def connection_made(self, transport):
        transport.write(self.message.encode())
        print('Data sent: {!r}'.format(self.message))

    def data_received(self, data):
        print('Data received: {!r}'.format(data.decode()))

    def connection_lost(self, exc):
        print('The server closed the connection')
        print('Stop the event loop')
        self.loop.stop()

class PeerClientProtocol(asyncio.Protocol):
    def __init__(self, handshake_message, torrent, peer_tuple):
        self.handshake_message = handshake_message
        self.info_hash = torrent.info_hash
        self.peer_id = PEER_ID
        self.peer_ip, self.peer_port = peer_tuple

loop = asyncio.get_event_loop()
message = 'Hello World!'
coro = loop.create_connection(lambda: EchoClientProtocol(message, loop),
                              '127.0.0.1', 8888)
loop.run_until_complete(coro)
loop.run_forever()
loop.close()
