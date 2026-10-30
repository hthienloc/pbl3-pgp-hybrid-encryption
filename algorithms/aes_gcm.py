"""
Mô-đun mã hóa đối xứng xác thực AES-GCM (Galois/Counter Mode).
Đảm bảo đồng thời tính bí mật dữ liệu và kiểm thực toàn vẹn bằng Authentication Tag.
"""

import os
from Cryptodome.Cipher import AES


def aes_gcm_encrypt(session_key, plaintext_bytes):
    """
    Mã hóa dữ liệu bằng AES-GCM với Nonce chuẩn 12 bytes (96 bits).
    Trả về: (ciphertext_bytes, nonce_bytes, auth_tag_bytes)
    """
    nonce = os.urandom(12)
    cipher = AES.new(session_key, AES.MODE_GCM, nonce=nonce)
    ciphertext, auth_tag = cipher.encrypt_and_digest(plaintext_bytes)
    return ciphertext, nonce, auth_tag


def aes_gcm_decrypt(session_key, nonce_bytes, ciphertext_bytes, auth_tag_bytes):
    """
    Giải mã và kiểm thực toàn vẹn dữ liệu bằng AES-GCM.
    Ném lỗi ValueError nếu Authentication Tag không khớp.
    """
    cipher = AES.new(session_key, AES.MODE_GCM, nonce=nonce_bytes)
    plaintext = cipher.decrypt_and_verify(ciphertext_bytes, auth_tag_bytes)
    return plaintext


if __name__ == "__main__":
    key = os.urandom(16)
    msg = "Kiểm thử AES-GCM độc lập".encode("utf-8")
    ct, nonce, tag = aes_gcm_encrypt(key, msg)
    recovered = aes_gcm_decrypt(key, nonce, ct, tag)
    print("Kiểm thử module AES-GCM:")
    print(f"Bản rõ: {msg.decode('utf-8')}")
    print(f"Nonce ({len(nonce)} bytes): {nonce.hex()}")
    print(f"Ciphertext ({len(ct)} bytes): {ct.hex()[:32]}...")
    print(f"Auth Tag ({len(tag)} bytes): {tag.hex()}")
    print(f"Khôi phục: {recovered.decode('utf-8')}")
    assert msg == recovered
    print("Khôi phục thành công.")
