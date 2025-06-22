import os
import base64
import time
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend

def generate_key_pair():
    return ec.generate_private_key(ec.SECP256R1(), default_backend())

def serialize_public_key(pubkey):
    return pubkey.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

def deserialize_public_key(data):
    return serialization.load_pem_public_key(data, backend=default_backend())

def derive_shared_key(private_key, peer_public_key):
    shared_secret = private_key.exchange(ec.ECDH(), peer_public_key)
    return shared_secret[:32]  # używamy pierwszych 32 bajtów jako klucza AES

def encrypt_message(aes_key, message):
    aesgcm = AESGCM(aes_key)
    nonce = os.urandom(12)
    timestamp = int(time.time())
    message_bytes = f"{timestamp}||{message}".encode('utf-8')
    ciphertext = aesgcm.encrypt(nonce, message_bytes, None)
    return nonce, ciphertext

def decrypt_message(aes_key, nonce, ciphertext):
    aesgcm = AESGCM(aes_key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    decoded = plaintext.decode('utf-8')
    timestamp_str, message_text = decoded.split('||', 1)
    timestamp = int(timestamp_str)
    return timestamp, message_text

def sign_data(private_key, data):
    return private_key.sign(data, ec.ECDSA(hashes.SHA256()))

def verify_signature(public_key, signature, data):
    public_key.verify(signature, data, ec.ECDSA(hashes.SHA256()))
