from cryptography.fernet import Fernet
from config.settings import KEY_LENGTH

class Encryption:
    def __init__(self):
        self.key = Fernet.generate_key()[:KEY_LENGTH]
        self.cipher = Fernet(self.key)

def encrypt_message(message):
    enc = Encryption()
    return enc.cipher.encrypt(message)

def decrypt_message(encrypted_message):
    enc = Encryption()
    try:
        return enc.cipher.decrypt(encrypted_message)
    except Exception:
        return b"Decryption failed"