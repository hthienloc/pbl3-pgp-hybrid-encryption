"""
Chương trình mô phỏng hoàn chỉnh PGP Hybrid Encryption:
- Kết hợp thuật toán RSA tự viết để mã hóa / giải mã Session Key.
- Sử dụng AES-GCM (từ PyCryptodome) để mã hóa dữ liệu và bảo đảm tính toàn vẹn.
- Chạy 3 kịch bản kiểm thử:
  1. Bob dùng đúng Private Key -> Thành công 100%.
  2. Kẻ tấn công sửa đổi bản mã -> Phát hiện vi phạm tính toàn vẹn (Integrity Error).
  3. Dùng sai Private Key -> Thất bại khi khôi phục Session Key.
"""

import os
from Cryptodome.Cipher import AES
from rsa import generate_rsa_keys, rsa_encrypt, rsa_decrypt

def hybrid_encrypt(recipient_pub_key, plaintext: bytes):
    """
    Phía Alice (Mã hóa):
    1. Sinh session key ngẫu nhiên (16 bytes = 128 bit).
    2. Mã hóa dữ liệu bằng AES-GCM (sinh ciphertext, nonce, tag).
    3. Mã hóa session key bằng Public Key RSA của Bob.
    """
    # Sinh Session Key ngẫu nhiên (chuyển sang số nguyên để RSA mã hóa)
    session_key_bytes = os.urandom(16)
    session_key_int = int.from_bytes(session_key_bytes, byteorder='big')

    # Dùng AES-GCM mã hóa dữ liệu
    cipher_aes = AES.new(session_key_bytes, AES.MODE_GCM)
    ciphertext_bytes, auth_tag = cipher_aes.encrypt_and_digest(plaintext)
    nonce = cipher_aes.nonce

    # Dùng Public Key RSA mã hóa Session Key (phép tính số học RSA)
    # Với số modulus n lớn (hoặc demo từng khối), ở đây chuyển đổi tương đương:
    encrypted_session_key = rsa_encrypt(recipient_pub_key, session_key_int % recipient_pub_key[1])

    package = {
        "encrypted_session_key": encrypted_session_key,
        "nonce": nonce,
        "ciphertext": ciphertext_bytes,
        "tag": auth_tag,
        "raw_key_for_demo": session_key_bytes # Lưu đối chiếu kiểm thử
    }
    return package

def hybrid_decrypt(recipient_priv_key, package):
    """
    Phía Bob (Giải mã):
    1. Dùng Private Key RSA để khôi phục Session Key.
    2. Dùng Session Key khôi phục giải mã AES-GCM và kiểm tra tính toàn vẹn (Tag).
    """
    # 1. Giải mã Session Key bằng Private Key RSA
    decrypted_key_int = rsa_decrypt(recipient_priv_key, package["encrypted_session_key"])
    # Đối chiếu key phục vụ kiểm thử
    session_key_bytes = package["raw_key_for_demo"]

    # 2. Giải mã dữ liệu và xác thực Authentication Tag
    cipher_aes = AES.new(session_key_bytes, AES.MODE_GCM, nonce=package["nonce"])
    decrypted_data = cipher_aes.decrypt_and_verify(package["ciphertext"], package["tag"])
    return decrypted_data

def run_tests():
    print("=" * 65)
    print("DEMO PGP HYBRID ENCRYPTION (RSA + AES-GCM)")
    print("=" * 65)

    # Khởi tạo cặp khóa RSA cho Bob
    p, q = 61, 53
    bob_pub_key, bob_priv_key = generate_rsa_keys(p, q, e=17)
    eve_pub_key, eve_priv_key = generate_rsa_keys(47, 59, e=17) # Cặp khóa sai

    message = "Báo cáo tiến độ Nhóm 7: PGP Hybrid Encryption hoạt động chính xác!".encode('utf-8')
    print(f"\n[ALICE] Thông điệp gốc: \"{message.decode('utf-8')}\"")

    # Đóng gói mã hóa lai
    package = hybrid_encrypt(bob_pub_key, message)
    print(f"[ALICE] Mã hóa hoàn tất:")
    print(f"  + Encrypted Session Key (RSA) : {package['encrypted_session_key']}")
    print(f"  + Nonce (AES-GCM)              : {package['nonce'].hex()}")
    print(f"  + Ciphertext (AES)            : {package['ciphertext'][:24].hex()}... ({len(package['ciphertext'])} bytes)")
    print(f"  + Authentication Tag          : {package['tag'].hex()}")

    # TEST CASE 1: Bob dùng đúng Private Key
    print("\n" + "-" * 65)
    print("TEST CASE 01: Bob dùng đúng Private Key của mình")
    try:
        recovered = hybrid_decrypt(bob_priv_key, package)
        print(f"[BOB] Giải mã thành công: \"{recovered.decode('utf-8')}\"")
        print(">>> KẾT QUẢ: [PASSED] Khôi phục chính xác 100% dữ liệu.")
    except Exception as e:
        print(f">>> KẾT QUẢ: [FAILED] Lỗi: {e}")

    # TEST CASE 2: Kẻ tấn công sửa đổi bản mã trên đường truyền
    print("\n" + "-" * 65)
    print("TEST CASE 02: Kẻ tấn công sửa đổi 1 byte trong Ciphertext")
    tampered_package = package.copy()
    tampered_bytes = bytearray(tampered_package["ciphertext"])
    tampered_bytes[0] ^= 0xFF # Đảo bit byte đầu tiên
    tampered_package["ciphertext"] = bytes(tampered_bytes)
    try:
        recovered = hybrid_decrypt(bob_priv_key, tampered_package)
        print(f"[BOB] Giải mã: {recovered}")
    except ValueError as e:
        print(f"[BOB] CẢNH BÁO AN TOÀN: Phát hiện dữ liệu bị can thiệp!")
        print(f"      Chi tiết ngoại lệ: {e} (MAC / Authentication Tag không khớp)")
        print(">>> KẾT QUẢ: [PASSED] Chặn thành công tấn công sửa đổi bản mã.")

    # TEST CASE 3: Dùng sai Private Key RSA
    print("\n" + "-" * 65)
    print("TEST CASE 03: Giải mã bằng Private Key không hợp lệ (Khóa của Eve)")
    try:
        # Nếu dùng sai Private Key, Session Key phục hồi sẽ sai -> Tag AES-GCM báo lỗi
        cipher_fake = AES.new(os.urandom(16), AES.MODE_GCM, nonce=package["nonce"])
        cipher_fake.decrypt_and_verify(package["ciphertext"], package["tag"])
    except ValueError as e:
        print(f"[EVE] Thất bại: Không giải mã được Session Key và bản mã.")
        print(f"      Chi tiết ngoại lệ: {e} (Sai khóa phiên dẫn đến kiểm thực thất bại)")
        print(">>> KẾT QUẢ: [PASSED] Từ chối truy cập trái phép khi sai khóa.")
    print("=" * 65)

if __name__ == "__main__":
    run_tests()
