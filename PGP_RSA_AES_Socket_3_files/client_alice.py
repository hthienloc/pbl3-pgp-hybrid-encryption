"""Máy A - Alice (TCP Client):
- Nạp Public Key (e, n) của Bob từ file bob_public.json (hoặc tự động tải từ máy Bob qua TCP).
- Gọi trực tiếp hàm mã hóa từ algorithms/hybrid_pgp.py để đóng gói bản tin gửi qua mạng.
"""

import base64
import json
import socket
import struct
import sys
from pathlib import Path

from pgp_crypto import (
    encrypt_message,
    fingerprint,
    read_bob_public_key,
    save_bob_public_key,
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PORT = 5000
BASE_DIR = Path(__file__).resolve().parent
PUBLIC_KEY_FILE = BASE_DIR / "bob_public.json"


def recv_exact(connection, count):
    chunks = bytearray()
    while len(chunks) < count:
        chunk = connection.recv(min(count - len(chunks), 65536))
        if not chunk:
            raise ConnectionError("Máy Bob đã đóng kết nối trước khi gửi đủ phản hồi.")
        chunks.extend(chunk)
    return bytes(chunks)


def send_json(connection, payload_dict):
    packet = json.dumps(payload_dict, separators=(",", ":")).encode("utf-8")
    if len(packet) > 1_000_000:
        raise ValueError("Thông điệp quá lớn cho giới hạn demo 1 MB.")
    connection.sendall(struct.pack("!I", len(packet)) + packet)
    return len(packet)


def receive_json(connection):
    packet_length = struct.unpack("!I", recv_exact(connection, 4))[0]
    packet = recv_exact(connection, packet_length)
    return json.loads(packet.decode("utf-8"))


def ensure_bob_public_key(bob_ip):
    """Đọc bob_public.json nếu đã có; nếu chưa có thì tự động tải từ máy Bob qua TCP."""
    if PUBLIC_KEY_FILE.exists():
        pub_key = read_bob_public_key(PUBLIC_KEY_FILE)
        print(f"[ALICE] Đã đọc Public Key của Bob từ file {PUBLIC_KEY_FILE.name}.")
        return pub_key

    print(f"[ALICE] Chưa có {PUBLIC_KEY_FILE.name} tại máy Alice. Đang tải Public Key từ máy Bob ({bob_ip}:{PORT})...")
    with socket.create_connection((bob_ip, PORT), timeout=10) as connection:
        send_json(connection, {"action": "GET_PUBLIC_KEY"})
        resp = receive_json(connection)
        pub_key = (int(resp["e"]), int(resp["n"]))
        save_bob_public_key(PUBLIC_KEY_FILE, pub_key)
    print(f"[ALICE] Đã tải và lưu Public Key vào {PUBLIC_KEY_FILE.name}.")
    return pub_key


def tamper_ciphertext(envelope):
    """Đảo bit byte đầu tiên của bản mã ciphertext để mô phỏng tấn công sửa đổi trên mạng."""
    raw = bytearray(base64.b64decode(envelope["ciphertext"]))
    if raw:
        raw[0] ^= 0xFF
    else:
        raw.append(0xFF)
    envelope["ciphertext"] = base64.b64encode(bytes(raw)).decode("ascii")


def tamper_encrypted_key(envelope):
    """Sửa đổi enc_session_key để mô phỏng việc giải mã ra Session Key sai (hoặc sai khóa RSA)."""
    c_key_int = int(envelope["enc_session_key"], 16)
    envelope["enc_session_key"] = hex(c_key_int ^ 0x1)


def main():
    print("=" * 68)
    print("MÁY A (ALICE) - TCP CLIENT MÃ HÓA & GỬI TIN PGP HYBRID (RSA + AES-GCM)")
    print("=" * 68)

    if len(sys.argv) >= 2:
        bob_ip = sys.argv[1].strip()
    else:
        bob_ip = input("[ALICE] Nhập địa chỉ IP của máy Bob (Enter để dùng 127.0.0.1): ").strip()
        if not bob_ip:
            bob_ip = "127.0.0.1"

    bob_public_key = ensure_bob_public_key(bob_ip)
    print(f"[ALICE] SHA-256 Public Key Fingerprint của Bob:\n        {fingerprint(bob_public_key)}")
    print("        (Hãy đối chiếu mã băm này trùng khớp với màn hình máy Bob)")

    while True:
        print("\n" + "-" * 68)
        print("CHỌN CHẾ ĐỘ GỬI TIN QUA MẠNG:")
        print("  [1] Gửi tin nhắn mã hóa chuẩn (Test Case 1: Khôi phục thành công 100%)")
        print("  [2] Giả lập Hacker sửa 1 byte Ciphertext trên mạng (Test Case 2: Phát hiện giả mạo)")
        print("  [3] Giả lập sai lệch khóa phiên RSA enc_session_key (Test Case 3: Sai Session Key)")
        print("  [0] Thoát chương trình")
        choice = input("[ALICE] Lựa chọn của bạn (mặc định 1): ").strip() or "1"

        if choice == "0":
            print("[ALICE] Đã kết thúc phiên làm việc.")
            break
        if choice not in ("1", "2", "3"):
            print("[ALICE] Lựa chọn không hợp lệ, vui lòng chọn 1, 2, 3 hoặc 0.")
            continue

        message = input("[ALICE] Nhập bản rõ M cần gửi cho Bob: ").strip()
        if not message:
            message = "Thông điệp kiểm thử PGP Hybrid Encryption từ máy Alice!"

        envelope, session_key = encrypt_message(message, bob_public_key)
        envelope["action"] = "SEND_MESSAGE"

        if choice == "2":
            tamper_ciphertext(envelope)
            print("[ALICE] [!] Đã đảo bit byte đầu tiên của ciphertext để giả lập tấn công MITM!")
        elif choice == "3":
            tamper_encrypted_key(envelope)
            print("[ALICE] [!] Đã làm lệch giá trị enc_session_key để giả lập giải mã sai Session Key!")

        print(f"[ALICE] [1] Đã sinh Session Key K (16B)  : {session_key.hex()}")
        print(f"[ALICE] [2] enc_session_key (RSA)        : {envelope['enc_session_key'][:44]}...")
        print(f"[ALICE] [3] nonce (AES-GCM 12B)          : {envelope['nonce']}")
        print(f"[ALICE] [4] auth_tag (GHASH 16B)         : {envelope['auth_tag']}")
        print(f"[ALICE] [5] ciphertext (AES)             : {envelope['ciphertext'][:44]}...")

        with socket.create_connection((bob_ip, PORT), timeout=10) as connection:
            sent_bytes = send_json(connection, envelope)
            print(f"[ALICE] >>> Đã truyền {sent_bytes} bytes qua TCP tới {bob_ip}:{PORT}.")
            response = receive_json(connection)
            print(f"[ALICE] <<< Phản hồi từ máy Bob: [{response.get('status')}] {response.get('detail')}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        print("[ALICE] Lỗi kết nối / xử lý:", error)
        sys.exit(1)
