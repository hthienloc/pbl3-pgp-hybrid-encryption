"""
Chương trình mô phỏng hoàn chỉnh PGP Hybrid Encryption:
- Kết hợp thuật toán RSA tự viết để mã hóa / giải mã trọn vẹn Session Key 128-bit.
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
    3. Mã hóa trọn vẹn session key bằng Public Key RSA của Bob.
    """
    session_key_bytes = os.urandom(16)
    session_key_int = int.from_bytes(session_key_bytes, byteorder="big")

    # Dùng AES-GCM mã hóa dữ liệu
    cipher_aes = AES.new(session_key_bytes, AES.MODE_GCM)
    ciphertext_bytes, auth_tag = cipher_aes.encrypt_and_digest(plaintext)
    nonce = cipher_aes.nonce

    # Dùng Public Key RSA mã hóa trọn vẹn Session Key 128-bit
    encrypted_session_key = rsa_encrypt(recipient_pub_key, session_key_int)

    package = {
        "encrypted_session_key": encrypted_session_key,
        "nonce": nonce,
        "ciphertext": ciphertext_bytes,
        "tag": auth_tag,
    }
    return package


def hybrid_decrypt(recipient_priv_key, package):
    """
    Phía Bob (Giải mã):
    1. Dùng Private Key RSA để khôi phục Session Key 16 bytes.
    2. Dùng Session Key khôi phục giải mã AES-GCM và kiểm tra tính toàn vẹn (Tag).
    """
    decrypted_key_int = rsa_decrypt(recipient_priv_key, package["encrypted_session_key"])
    try:
        session_key_bytes = decrypted_key_int.to_bytes(16, byteorder="big")
    except OverflowError:
        # Nếu dùng sai Private Key khiến số giải mã vượt quá 16 bytes, lấy 16 bytes cuối
        # để đưa vào AES-GCM kiểm thực và kích hoạt lỗi MAC check failed chuẩn xác
        session_key_bytes = (decrypted_key_int & ((1 << 128) - 1)).to_bytes(16, byteorder="big")

    cipher_aes = AES.new(session_key_bytes, AES.MODE_GCM, nonce=package["nonce"])
    decrypted_data = cipher_aes.decrypt_and_verify(package["ciphertext"], package["tag"])
    return decrypted_data


def run_tests():
    print("=" * 65)
    print("DEMO PGP HYBRID ENCRYPTION (RSA + AES-GCM)")
    print("=" * 65)

    # Khởi tạo cặp khóa RSA 256-bit cho Bob và Eve (đủ chứa trọn khóa AES 128-bit)
    bob_pub_key, bob_priv_key = generate_rsa_keys(bits=256)
    eve_pub_key, eve_priv_key = generate_rsa_keys(bits=256)

    message = "Báo cáo tiến độ Nhóm 7: PGP Hybrid Encryption hoạt động chính xác!".encode("utf-8")
    print(f'\n[ALICE] Thông điệp gốc: "{message.decode("utf-8")}"')

    # Đóng gói mã hóa lai
    package = hybrid_encrypt(bob_pub_key, message)
    print("[ALICE] Mã hóa hoàn tất:")
    print(f"  + Encrypted Session Key (RSA) : {hex(package['encrypted_session_key'])[:36]}...")
    print(f"  + Nonce (AES-GCM)             : {package['nonce'].hex()}")
    print(f"  + Ciphertext (AES)            : {package['ciphertext'][:24].hex()}... ({len(package['ciphertext'])} bytes)")
    print(f"  + Authentication Tag          : {package['tag'].hex()}")

    # TEST CASE 1: Bob dùng đúng Private Key
    print("\n" + "-" * 65)
    print("TEST CASE 01: Bob dùng đúng Private Key của mình")
    try:
        recovered = hybrid_decrypt(bob_priv_key, package)
        print(f'[BOB] Giải mã thành công: "{recovered.decode("utf-8")}"')
        print(">>> KẾT QUẢ: [PASSED] Khôi phục chính xác 100% dữ liệu.")
    except Exception as e:
        print(f">>> KẾT QUẢ: [FAILED] Lỗi: {e}")

    # TEST CASE 2: Kẻ tấn công sửa đổi bản mã trên đường truyền
    print("\n" + "-" * 65)
    print("TEST CASE 02: Kẻ tấn công sửa đổi 1 byte trong Ciphertext")
    tampered_package = package.copy()
    tampered_bytes = bytearray(tampered_package["ciphertext"])
    tampered_bytes[0] ^= 0xFF  # Đảo bit byte đầu tiên
    tampered_package["ciphertext"] = bytes(tampered_bytes)
    try:
        recovered = hybrid_decrypt(bob_priv_key, tampered_package)
        print(f"[BOB] Giải mã: {recovered}")
    except ValueError as e:
        print("[BOB] CẢNH BÁO AN TOÀN: Phát hiện dữ liệu bị can thiệp!")
        print(f"      Chi tiết ngoại lệ: {e} (MAC / Authentication Tag không khớp)")
        print(">>> KẾT QUẢ: [PASSED] Chặn thành công tấn công sửa đổi bản mã.")

    # TEST CASE 3: Dùng sai Private Key RSA
    print("\n" + "-" * 65)
    print("TEST CASE 03: Giải mã bằng Private Key không hợp lệ (Khóa của Eve)")
    try:
        hybrid_decrypt(eve_priv_key, package)
    except ValueError as e:
        print("[EVE] Thất bại: Giải mã RSA ra Session Key sai -> AES-GCM từ chối xác thực.")
        print(f"      Chi tiết ngoại lệ: {e} (Sai khóa phiên dẫn đến kiểm thực thất bại)")
        print(">>> KẾT QUẢ: [PASSED] Từ chối truy cập trái phép khi sai khóa.")
    print("=" * 65)


if __name__ == "__main__":
    run_tests()
