"""Cầu nối chuyển đổi dữ liệu mạng (JSON/Base64) cho mô-đun algorithms/hybrid_pgp.py.

Toàn bộ thuật toán mật mã (Euclid mở rộng, RSA, AES-GCM, đóng/mở gói PGP)
đều được import trực tiếp từ gói `algorithms` của nhóm.
"""

import base64
import hashlib
import json
import os
import sys
from pathlib import Path

# Thêm thư mục gốc dự án vào sys.path để import trực tiếp từ package `algorithms`
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from algorithms.rsa import generate_rsa_keys
from algorithms.hybrid_pgp import alice_encrypt_package, bob_decrypt_package


def create_bob_keypair(private_path: Path, public_path: Path, bits=512):
    """Sinh cặp khóa RSA (e, n) và (d, n) bằng algorithms.rsa; lưu file để tái sử dụng."""
    if private_path.exists():
        data = json.loads(private_path.read_text(encoding="utf-8"))
        pub_key = (int(data["e"]), int(data["n"]))
        priv_key = (int(data["d"]), int(data["n"]))
        print(f"[BOB] Đã nạp cặp khóa RSA ({priv_key[1].bit_length()}-bit) có sẵn.")
    else:
        pub_key, priv_key = generate_rsa_keys(e=65537, bits=bits)
        e, n = pub_key
        d, _ = priv_key
        private_data = {"e": e, "d": d, "n": n}
        private_path.write_text(json.dumps(private_data, indent=2), encoding="utf-8")
        if os.name == "posix":
            os.chmod(private_path, 0o600)
        print(f"[BOB] Đã sinh mới cặp khóa RSA {n.bit_length()}-bit từ algorithms.rsa.")

    public_data = {"e": pub_key[0], "n": pub_key[1]}
    public_path.write_text(json.dumps(public_data, indent=2), encoding="utf-8")
    return pub_key, priv_key


def read_bob_public_key(public_path: Path):
    """Đọc Public Key (e, n) của Bob từ file JSON."""
    data = json.loads(public_path.read_text(encoding="utf-8"))
    return (int(data["e"]), int(data["n"]))


def save_bob_public_key(public_path: Path, pub_key):
    """Lưu Public Key (e, n) của Bob xuống file JSON bên phía Alice."""
    e, n = pub_key
    public_path.write_text(json.dumps({"e": e, "n": n}, indent=2), encoding="utf-8")


def fingerprint(public_key):
    """Tính mã băm SHA-256 của Public Key (e, n) để Alice và Bob đối chiếu."""
    e, n = public_key
    return hashlib.sha256(f"RSA:{e}:{n}".encode("ascii")).hexdigest()


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def _unb64(text: str) -> bytes:
    return base64.b64decode(text, validate=True)


def encrypt_message(message: str, bob_public_key):
    """Gọi trực tiếp `alice_encrypt_package` từ algorithms/hybrid_pgp.py và chuyển sang JSON."""
    package, session_key = alice_encrypt_package(message, bob_public_key)

    envelope = {
        "enc_session_key": hex(package["enc_session_key"]),
        "nonce": _b64(package["nonce"]),
        "ciphertext": _b64(package["ciphertext"]),
        "auth_tag": _b64(package["auth_tag"]),
    }
    return envelope, session_key


def decrypt_message(envelope: dict, bob_private_key):
    """Chuyển dữ liệu JSON về kiểu bytes/int và gọi trực tiếp `bob_decrypt_package`."""
    enc_key_str = str(envelope["enc_session_key"])
    enc_key_int = int(enc_key_str, 16) if enc_key_str.startswith("0x") else int(enc_key_str)

    package = {
        "enc_session_key": enc_key_int,
        "nonce": _unb64(envelope["nonce"]),
        "ciphertext": _unb64(envelope["ciphertext"]),
        "auth_tag": _unb64(envelope["auth_tag"]),
    }
    plaintext = bob_decrypt_package(package, bob_private_key)
    return plaintext
