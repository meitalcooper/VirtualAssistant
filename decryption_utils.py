import base64
import os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def decrypt_recording(encrypted_audio, encrypted_cek, iv, private_key_path="/Users/mecooper/Desktop/projects/VirtualAssistant/private_keys/private_key.pem"):
    """
    Decrypts Twilio encrypted call recordings.
    :param encrypted_audio: The encrypted audio file content (bytes)
    :param encrypted_cek: The encrypted content encryption key (base64 encoded)
    :param iv: The initialization vector (base64 encoded)
    :param private_key_path: Path to the private key file
    :return: Decrypted audio content as bytes
    """
    try:
        print("\n=== Starting Decryption Process ===")
        
        # Load private key from file
        with open(private_key_path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
            )
        print("Loaded private key successfully.")
        
        # Decode encrypted CEK and IV
        encrypted_cek_bytes = base64.b64decode(encrypted_cek)
        iv_bytes = base64.b64decode(iv)
        
        # Decrypt CEK using RSA private key
        decrypted_cek = private_key.decrypt(
            encrypted_cek_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        print("Decrypted CEK successfully.")
        
        # Extract authentication tag (last 16 bytes of encrypted audio)
        auth_tag = encrypted_audio[-16:]
        encrypted_audio = encrypted_audio[:-16]
        
        # Initialize AES256-GCM decryptor
        cipher = Cipher(
            algorithms.AES(decrypted_cek),
            modes.GCM(iv_bytes, auth_tag),
        )
        decryptor = cipher.decryptor()
        
        # Decrypt the audio content
        decrypted_audio = decryptor.update(encrypted_audio) + decryptor.finalize()
        print("Decryption complete.")
        
        return decrypted_audio
    except Exception as e:
        print(f"Decryption error: {str(e)}")
        return None
