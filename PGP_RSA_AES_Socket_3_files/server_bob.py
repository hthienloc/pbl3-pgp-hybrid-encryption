"""Máy B - Bob (TCP Server):
- Sinh cặp khóa RSA (e, n) và (d, n) từ mô-đun algorithms/rsa.py.
- Lắng nghe gói tin PGP Hybrid và giải mã trực tiếp qua algorithms/hybrid_pgp.py.
"""

import json
import os
import socket
import struct
import sys
from pathlib import Path

from pgp_crypto import create_bob_keypair, decrypt_message, fingerprint

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HOST = "0.0.0.0"        # Lắng nghe từ mọi máy trong mạng LAN
PORT = 5000
MAX_PACKET = 1_000_000  # Giới hạn kích thước gói tin JSON (1 MB)
BASE_DIR = Path(__file__).resolve().parent
PRIVATE_KEY_FILE = BASE_DIR / "bob_private.json"
PUBLIC_KEY_FILE = BASE_DIR / "bob_public.json"


def get_lan_ip():
    """Tự động lấy địa chỉ IPv4 LAN của máy Bob để nhập vào máy Alice."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"


def recv_exact(connection, count):
    """TCP là luồng byte; đảm bảo đọc đủ count byte trước khi phân tích."""
    chunks = bytearray()
    while len(chunks) < count:
        chunk = connection.recv(min(count - len(chunks), 65536))
        if not chunk:
            raise ConnectionError("Bên gửi đã đóng kết nối trước khi gửi đủ dữ liệu.")
        chunks.extend(chunk)
    return bytes(chunks)


def send_json(connection, payload_dict):
    """Đóng gói 4 byte độ dài (Big-Endian) + chuỗi JSON gửi qua TCP."""
    data = json.dumps(payload_dict, separators=(",", ":")).encode("utf-8")
    connection.sendall(struct.pack("!I", len(data)) + data)


def receive_json(connection):
    """Nhận 4 byte độ dài đầu tiên, sau đó đọc chính xác gói JSON."""
    packet_length = struct.unpack("!I", recv_exact(connection, 4))[0]
    if not 0 < packet_length <= MAX_PACKET:
        raise ValueError("Kích thước gói tin không hợp lệ.")
    packet = recv_exact(connection, packet_length)
    envelope = json.loads(packet.decode("utf-8"))
    if not isinstance(envelope, dict):
        raise ValueError("Gói tin phải là một JSON object.")
    return envelope


def main():
    print("=" * 68)
    print("MÁY B (BOB) - TCP SERVER NHẬN & GIẢI MÃ PGP HYBRID (RSA + AES-GCM)")
    print("=" * 68)

    pub_key, priv_key = create_bob_keypair(PRIVATE_KEY_FILE, PUBLIC_KEY_FILE, bits=512)
    lan_ip = get_lan_ip()

    print(f"[BOB] File Public Key  : {PUBLIC_KEY_FILE.name}")
    print(f"[BOB] File Private Key : {PRIVATE_KEY_FILE.name} (BÍ MẬT - chỉ lưu tại máy Bob)")
    print(f"[BOB] SHA-256 Public Key Fingerprint:\n      {fingerprint(pub_key)}")
    print("-" * 68)
    print(f"[BOB] ĐỊA CHỈ IP LAN CỦA MÁY BOB: {lan_ip}")
    print(f"      -> Trên máy Alice, hãy chạy: python client_alice.py {lan_ip}")
    print("-" * 68)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        if os.name == "posix":
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        elif hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            server.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        server.bind((HOST, PORT))
        server.listen(5)
        print(f"[BOB] Đang lắng nghe TCP tại {HOST}:{PORT} ... (Nhấn Ctrl+C để dừng)", flush=True)

        try:
            while True:
                connection, address = server.accept()
                with connection:
                    connection.settimeout(15)
                    print(f"\n[BOB] >>> Kết nối mới từ {address[0]}:{address[1]}", flush=True)
                    try:
                        request = receive_json(connection)
                        action = request.get("action", "SEND_MESSAGE")

                        # Hỗ trợ Alice lấy Public Key tự động qua mạng nếu chưa copy file
                        if action == "GET_PUBLIC_KEY":
                            send_json(connection, {"e": pub_key[0], "n": pub_key[1]})
                            print("[BOB] Đã gửi Public Key (e, n) cho máy Alice.", flush=True)
                            continue

                        # Xử lý gói tin mã hóa PGP Hybrid
                        print("[BOB] Đã nhận gói tin PGP gồm 4 thành phần:")
                        print(f"      + enc_session_key (RSA) : {str(request.get('enc_session_key', ''))[:44]}...")
                        print(f"      + nonce (AES-GCM 12B)   : {request.get('nonce')}")
                        print(f"      + auth_tag (GHASH 16B)  : {request.get('auth_tag')}")
                        print(f"      + ciphertext (AES)      : {str(request.get('ciphertext', ''))[:44]}...")

                        plaintext = decrypt_message(request, priv_key)
                        print("[BOB] Đã giải mã RSA & xác thực toàn vẹn AES-GCM thành công!")
                        print(f'[BOB] >>> BẢN RÕ NHẬN ĐƯỢC: "{plaintext}"', flush=True)
                        send_json(connection, {"status": "OK", "detail": "Bob da giai ma va xac thuc thanh cong!"})

                    except ValueError as error:
                        print("[BOB] [!] CẢNH BÁO AN TOÀN MẬT MÃ:")
                        print(f"      Phát hiện gói tin bị can thiệp hoặc sai khóa! Chi tiết: {error}")
                        print("      -> Bản tin đã bị hủy bỏ theo cơ chế toàn vẹn AES-GCM.", flush=True)
                        try:
                            send_json(connection, {"status": "ERROR", "detail": f"Tu choi goi tin: {error}"})
                        except OSError:
                            pass
                    except Exception as error:
                        print("[BOB] Lỗi nhận/giải mã:", error, flush=True)
        except KeyboardInterrupt:
            print("\n[BOB] Đã dừng TCP Server.", flush=True)


if __name__ == "__main__":
    main()
