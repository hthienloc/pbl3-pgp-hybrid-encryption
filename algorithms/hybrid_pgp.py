"""
Mô-đun tích hợp Hybrid Encryption theo mô hình PGP (RSA + AES-GCM).
- Phía Alice: Sinh Session Key 128-bit ngẫu nhiên, mã hóa dữ liệu qua AES-GCM,
  mã hóa trọn vẹn Session Key qua RSA của Bob và đóng gói package.
- Phía Bob: Dùng Private Key RSA giải mã khôi phục Session Key, giải mã AES-GCM và đối chiếu Tag.
"""

import os
from .rsa import rsa_encrypt, rsa_decrypt
from .aes_gcm import aes_gcm_encrypt, aes_gcm_decrypt


def alice_encrypt_package(plaintext_str, bob_pub_key):
    """
    Quy trình đóng gói phía Alice.
    Trả về: (package_dict, session_key_raw)
    """
    session_key = os.urandom(16)  # Khóa phiên AES-128 (16 bytes = 128 bits)
    plaintext_bytes = plaintext_str.encode("utf-8")

    ciphertext, nonce, auth_tag = aes_gcm_encrypt(session_key, plaintext_bytes)

    # Mã hóa trọn vẹn Session Key 16 bytes bằng RSA Public Key của Bob
    key_int = int.from_bytes(session_key, byteorder="big")
    enc_session_key = rsa_encrypt(bob_pub_key, key_int)

    package = {
        "enc_session_key": enc_session_key,
        "nonce": nonce,
        "ciphertext": ciphertext,
        "auth_tag": auth_tag,
    }
    return package, session_key


def bob_decrypt_package(package, bob_priv_key):
    """
    Quy trình tiếp nhận và giải mã phía Bob.
    Ném ngoại lệ nếu xác thực Tag thất bại hoặc khóa không khớp.
    """
    enc_session_key = package["enc_session_key"]
    recovered_key_int = rsa_decrypt(bob_priv_key, enc_session_key)

    # Khôi phục trực tiếp 16 bytes Session Key từ kết quả giải mã RSA
    try:
        recovered_session_key = recovered_key_int.to_bytes(16, byteorder="big")
    except OverflowError:
        # Nếu C_key bị thay đổi hoặc giải mã bằng sai Private Key làm số nguyên > 16 bytes
        recovered_session_key = (recovered_key_int & ((1 << 128) - 1)).to_bytes(16, byteorder="big")

    plaintext_bytes = aes_gcm_decrypt(
        session_key=recovered_session_key,
        nonce_bytes=package["nonce"],
        ciphertext_bytes=package["ciphertext"],
        auth_tag_bytes=package["auth_tag"],
    )
    return plaintext_bytes.decode("utf-8")


if __name__ == "__main__":
    from .rsa import generate_rsa_keys

    bob_pub, bob_priv = generate_rsa_keys(bits=256)
    msg = "PGP Hybrid Encryption tích hợp thành công!"
    pkg, s_key = alice_encrypt_package(msg, bob_pub)
    decrypted = bob_decrypt_package(pkg, bob_priv)
    print("Kiểm thử tích hợp Hybrid PGP:")
    print(f"Session Key (16B): {s_key.hex()}")
    print(f"Bản rõ khôi phục : {decrypted}")
    assert msg == decrypted
    print("Khôi phục thành công.")
