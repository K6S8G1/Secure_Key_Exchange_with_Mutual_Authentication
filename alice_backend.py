import socket
import struct
import base64
from common_crypto import *

def start_alice(message):
    alice_ecdh_priv = generate_key_pair()
    alice_signing_priv = generate_key_pair()

    alice_ecdh_pub = alice_ecdh_priv.public_key()
    alice_signing_pub = alice_signing_priv.public_key()

    alice_ecdh_pub_bytes = serialize_public_key(alice_ecdh_pub)
    alice_signing_pub_bytes = serialize_public_key(alice_signing_pub)

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 65432))

    client.send(struct.pack('!I', len(alice_ecdh_pub_bytes)))
    client.send(alice_ecdh_pub_bytes)

    client.send(struct.pack('!I', len(alice_signing_pub_bytes)))
    client.send(alice_signing_pub_bytes)

    def recv_all(sock, length):
        data = b''
        while len(data) < length:
            more = sock.recv(length - len(data))
            if not more:
                raise EOFError("Socket closed")
            data += more
        return data

    ecdh_len = struct.unpack('!I', recv_all(client, 4))[0]
    bob_ecdh_pub_bytes = recv_all(client, ecdh_len)

    signing_len = struct.unpack('!I', recv_all(client, 4))[0]
    bob_signing_pub_bytes = recv_all(client, signing_len)

    bob_ecdh_pub = deserialize_public_key(bob_ecdh_pub_bytes)
    aes_key = derive_shared_key(alice_ecdh_priv, bob_ecdh_pub)

    nonce, ciphertext = encrypt_message(aes_key, message)
    signature = sign_data(alice_signing_priv, ciphertext)

    packet = base64.b64encode(nonce) + b'||' + base64.b64encode(ciphertext) + b'||' + base64.b64encode(signature)
    client.send(packet)
    client.close()
