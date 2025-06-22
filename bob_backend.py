import socket
import struct
import base64
import time
from common_crypto import *

def start_bob(log_fn):
    def recv_all(sock, length):
        data = b''
        while len(data) < length:
            more = sock.recv(length - len(data))
            if not more:
                raise EOFError("Socket closed")
            data += more
        return data

    bob_ecdh_priv = generate_key_pair()
    bob_signing_priv = generate_key_pair()

    bob_ecdh_pub = bob_ecdh_priv.public_key()
    bob_signing_pub = bob_signing_priv.public_key()

    bob_ecdh_pub_bytes = serialize_public_key(bob_ecdh_pub)
    bob_signing_pub_bytes = serialize_public_key(bob_signing_pub)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 65432))
    server.listen(1)
    log_fn("🟢 Bob nasłuchuje...")

    conn, addr = server.accept()
    log_fn(f"🔗 Połączono z: {addr}")

    ecdh_len = struct.unpack('!I', recv_all(conn, 4))[0]
    alice_ecdh_pub_bytes = recv_all(conn, ecdh_len)

    signing_len = struct.unpack('!I', recv_all(conn, 4))[0]
    alice_signing_pub_bytes = recv_all(conn, signing_len)

    alice_ecdh_pub = deserialize_public_key(alice_ecdh_pub_bytes)
    alice_signing_pub = deserialize_public_key(alice_signing_pub_bytes)

    conn.send(struct.pack('!I', len(bob_ecdh_pub_bytes)))
    conn.send(bob_ecdh_pub_bytes)

    conn.send(struct.pack('!I', len(bob_signing_pub_bytes)))
    conn.send(bob_signing_pub_bytes)

    aes_key = derive_shared_key(bob_ecdh_priv, alice_ecdh_pub)

    packet = conn.recv(4096)
    nonce_b64, ciphertext_b64, signature_b64 = packet.split(b'||')

    nonce = base64.b64decode(nonce_b64)
    ciphertext = base64.b64decode(ciphertext_b64)
    signature = base64.b64decode(signature_b64)

    try:
        verify_signature(alice_signing_pub, signature, ciphertext)
        log_fn("✅ Podpis Alice zweryfikowany.")
    except Exception as e:
        log_fn(f"❌ Błąd weryfikacji podpisu: {e}")
        return

    try:
        timestamp, message_text = decrypt_message(aes_key, nonce, ciphertext)
    except Exception as e:
        log_fn(f"❌ Błąd odszyfrowania: {e}")
        return

    current_time = int(time.time())
    if abs(current_time - timestamp) > 30:
        log_fn("⚠️ Odrzucono wiadomość – timestamp za stary.")
    else:
        log_fn(f"📨 Wiadomość od Alice: {message_text}")

    conn.close()
