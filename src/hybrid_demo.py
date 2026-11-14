"""
Chương trình mô phỏng hoàn chỉnh PGP Hybrid Encryption:
- Kết hợp thuật toán RSA tự viết để mã hóa / giải mã trọn vẹn Session Key 128-bit.
- Sử dụng AES-GCM (từ PyCryptodome) để mã hóa dữ liệu và bảo đảm tính toàn vẹn.
- Chạy 3 kịch bản kiểm thử:
  1. Bob dùng đúng Private Key -> Thành công 100%.
  2. Kẻ tấn công sửa đổi bản mã -> Phát hiện vi phạm tính toàn vẹn (Integrity Error).
  3. Dùng sai Private Key -> Thất bại khi khôi phục Session Key.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from algorithms.rsa import generate_rsa_keys
from algorithms.hybrid_pgp import alice_encrypt_package, bob_decrypt_package


def run_tests():
    print("=" * 65)
    print("DEMO PGP HYBRID ENCRYPTION (RSA + AES-GCM)")
    print("=" * 65)

    # Khởi tạo cặp khóa RSA 256-bit cho Bob và Eve (đủ chứa trọn khóa AES 128-bit)
    bob_pub_key, bob_priv_key = generate_rsa_keys(bits=256)
    _, eve_priv_key = generate_rsa_keys(bits=256)

    message = "Báo cáo tiến độ Nhóm 7: PGP Hybrid Encryption hoạt động chính xác!"
    print(f'\n[ALICE] Thông điệp gốc: "{message}"')

    # Đóng gói mã hóa lai
    package, _ = alice_encrypt_package(message, bob_pub_key)
    print("[ALICE] Mã hóa hoàn tất:")
    print(f"  + Encrypted Session Key (RSA) : {hex(package['enc_session_key'])[:36]}...")
    print(f"  + Nonce (AES-GCM)             : {package['nonce'].hex()}")
    print(f"  + Ciphertext (AES)            : {package['ciphertext'][:24].hex()}... ({len(package['ciphertext'])} bytes)")
    print(f"  + Authentication Tag          : {package['auth_tag'].hex()}")

    # TEST CASE 1: Bob dùng đúng Private Key
    print("\n" + "-" * 65)
    print("TEST CASE 01: Bob dùng đúng Private Key của mình")
    try:
        recovered = bob_decrypt_package(package, bob_priv_key)
        print(f'[BOB] Giải mã thành công: "{recovered}"')
        assert recovered == message
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
        recovered = bob_decrypt_package(tampered_package, bob_priv_key)
        print(f"[BOB] Giải mã: {recovered}")
    except ValueError as e:
        print("[BOB] CẢNH BÁO AN TOÀN: Phát hiện dữ liệu bị can thiệp!")
        print(f"      Chi tiết ngoại lệ: {e} (MAC / Authentication Tag không khớp)")
        print(">>> KẾT QUẢ: [PASSED] Chặn thành công tấn công sửa đổi bản mã.")

    # TEST CASE 3: Dùng sai Private Key RSA
    print("\n" + "-" * 65)
    print("TEST CASE 03: Giải mã bằng Private Key không hợp lệ (Khóa của Eve)")
    try:
        bob_decrypt_package(package, eve_priv_key)
    except ValueError as e:
        print("[EVE] Thất bại: Giải mã RSA ra Session Key sai -> AES-GCM từ chối xác thực.")
        print(f"      Chi tiết ngoại lệ: {e} (Sai khóa phiên dẫn đến kiểm thực thất bại)")
        print(">>> KẾT QUẢ: [PASSED] Từ chối truy cập trái phép khi sai khóa.")
    print("=" * 65)


if __name__ == "__main__":
    run_tests()
