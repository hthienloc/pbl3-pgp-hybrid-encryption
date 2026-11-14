#pagebreak()

#heading(numbering: none, outlined: true)[PHỤ LỤC]

#heading(level: 2, numbering: none, outlined: true)[Phụ lục A: Cấu trúc mã nguồn và hướng dẫn chạy chương trình]

Hệ thống phần mềm được tổ chức phân tầng với lõi thuật toán đặt tại thư mục `algorithms/` và tái sử dụng cho ứng dụng web NiceGUI, kịch bản kiểm thử CLI và mô hình Socket LAN:
- `algorithms/euclid.py`: Cài đặt giải thuật Euclid mở rộng (`extended_gcd`) và tìm nghịch đảo mô-đun (`mod_inverse`).
- `algorithms/rsa.py`: Cài đặt kiểm tra nguyên tố Miller–Rabin (`is_prime`, mặc định `k = 20`), sinh số nguyên tố (`generate_prime`), sinh cặp khóa (`generate_rsa_keys`), mã hóa (`rsa_encrypt`) và giải mã (`rsa_decrypt`).
- `algorithms/aes_gcm.py`: Cài đặt mã hóa (`aes_gcm_encrypt`) và giải mã có kiểm thực (`aes_gcm_decrypt`) dựa trên PyCryptodome.
- `algorithms/hybrid_pgp.py`: Đóng gói (`alice_encrypt_package`) và giải mã (`bob_decrypt_package`) luồng dữ liệu lai.
- `PGP_RSA_AES_Socket_3_files/`: Gồm `pgp_crypto.py`, `server_bob.py` (TCP Server, khóa RSA 512-bit) và `client_alice.py` (TCP Client).
- `src/hybrid_demo.py`: Kịch bản dòng lệnh chạy 3 kịch bản kiểm thử an toàn.
- `src/gui_nicegui.py`: Ứng dụng web mô phỏng tương tác trên nền NiceGUI (chạy tại cổng `8080`).

Hướng dẫn cài đặt thư viện và chạy thử nghiệm từ thư mục gốc dự án:

```bash
pip install -r requirements.txt
python3 src/hybrid_demo.py          # Chạy 3 kịch bản kiểm thử CLI
python3 src/gui_nicegui.py          # Khởi động Web Simulator tại http://localhost:8080
python3 PGP_RSA_AES_Socket_3_files/server_bob.py        # Chạy trên máy nhận (Bob)
python3 PGP_RSA_AES_Socket_3_files/client_alice.py <IP> # Chạy trên máy gửi (Alice)
```

#heading(level: 2, numbering: none, outlined: true)[Phụ lục B: Cài đặt giải thuật Euclid mở rộng và RSA số học]

Mã nguồn mô-đun `algorithms/euclid.py`:

```python
def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def mod_inverse(e, phi):
    gcd, x, _ = extended_gcd(e, phi)
    if gcd != 1:
        raise ValueError(f"Không tồn tại nghịch đảo modulo: gcd({e}, {phi}) = {gcd} != 1")
    return (x % phi + phi) % phi
```

Mã nguồn mô-đun `algorithms/rsa.py`:

```python
import random
from .euclid import extended_gcd, mod_inverse

def is_prime(n, k=20):
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False

    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    rng = random.SystemRandom()
    for _ in range(k):
        a = rng.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_prime(bits=128):
    rng = random.SystemRandom()
    while True:
        candidate = rng.getrandbits(bits) | (1 << (bits - 1)) | 1
        if is_prime(candidate):
            return candidate

def generate_rsa_keys(p=None, q=None, e=65537, bits=256):
    if p is None and q is None:
        prime_bits = max(bits // 2, 72)
        while True:
            p = generate_prime(prime_bits)
            q = generate_prime(prime_bits)
            if p != q and extended_gcd(e, (p - 1) * (q - 1))[0] == 1:
                break
    elif p is None or q is None:
        raise ValueError("Phải cung cấp đồng thời cả p và q, hoặc để trống cả hai để sinh ngẫu nhiên.")
    else:
        if p == q or not is_prime(p) or not is_prime(q):
            raise ValueError("p và q phải là hai số nguyên tố phân biệt.")
        if extended_gcd(e, (p - 1) * (q - 1))[0] != 1:
            raise ValueError("e và phi(n) phải nguyên tố cùng nhau.")

    n = p * q
    phi = (p - 1) * (q - 1)
    d = mod_inverse(e, phi)
    return (e, n), (d, n)

def rsa_encrypt(public_key, plaintext_num):
    e, n = public_key
    if not (0 <= plaintext_num < n):
        raise ValueError(f"Dữ liệu ({plaintext_num}) phải nằm trong khoảng [0, {n - 1}]")
    return pow(plaintext_num, e, n)

def rsa_decrypt(private_key, ciphertext_num):
    d, n = private_key
    if not (0 <= ciphertext_num < n):
        raise ValueError(f"Bản mã ({ciphertext_num}) phải nằm trong khoảng [0, {n - 1}]")
    return pow(ciphertext_num, d, n)
```

#heading(level: 2, numbering: none, outlined: true)[Phụ lục C: Cài đặt AES-GCM và bộ đóng gói mã hóa lai]

Mã nguồn mô-đun `algorithms/aes_gcm.py` và `algorithms/hybrid_pgp.py`:

```python
import os
from Cryptodome.Cipher import AES
from .rsa import rsa_encrypt, rsa_decrypt

def aes_gcm_encrypt(session_key, plaintext_bytes):
    nonce = os.urandom(12)
    cipher = AES.new(session_key, AES.MODE_GCM, nonce=nonce)
    ciphertext, auth_tag = cipher.encrypt_and_digest(plaintext_bytes)
    return ciphertext, nonce, auth_tag

def aes_gcm_decrypt(session_key, nonce_bytes, ciphertext_bytes, auth_tag_bytes):
    if len(nonce_bytes) != 12:
        raise ValueError(f"Nonce AES-GCM chuẩn phải dài 12 bytes (nhận được {len(nonce_bytes)} bytes).")
    cipher = AES.new(session_key, AES.MODE_GCM, nonce=nonce_bytes)
    return cipher.decrypt_and_verify(ciphertext_bytes, auth_tag_bytes)

# --- Đóng gói PGP Hybrid ---
def alice_encrypt_package(plaintext_str, bob_pub_key):
    session_key = os.urandom(16)  # Khóa phiên AES-128 (16 bytes = 128 bits)
    ciphertext, nonce, auth_tag = aes_gcm_encrypt(session_key, plaintext_str.encode("utf-8"))
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
    recovered_key_int = rsa_decrypt(bob_priv_key, package["enc_session_key"])
    try:
        recovered_session_key = recovered_key_int.to_bytes(16, byteorder="big")
    except OverflowError as exc:
        raise ValueError("Khóa phiên giải mã từ RSA vượt quá 128-bit (sai khóa hoặc C_key bị can thiệp).") from exc
    plaintext_bytes = aes_gcm_decrypt(
        session_key=recovered_session_key,
        nonce_bytes=package["nonce"],
        ciphertext_bytes=package["ciphertext"],
        auth_tag_bytes=package["auth_tag"],
    )
    return plaintext_bytes.decode("utf-8")
```

#heading(level: 2, numbering: none, outlined: true)[Phụ lục D: Cài đặt truyền thông Socket TCP giữa 2 máy mạng LAN]

Cơ chế đóng khung 4 byte độ dài giải quyết phân mảnh byte stream trong `PGP_RSA_AES_Socket_3_files/server_bob.py`:

```python
import struct, json

MAX_PACKET = 4 * 1024 * 1024

def recv_exact(connection, count):
    chunks = bytearray()
    while len(chunks) < count:
        chunk = connection.recv(min(count - len(chunks), 65536))
        if not chunk:
            raise ConnectionError("Bên gửi đã đóng kết nối trước khi gửi đủ dữ liệu.")
        chunks.extend(chunk)
    return bytes(chunks)

def send_json(connection, payload_dict):
    data = json.dumps(payload_dict, separators=(",", ":")).encode("utf-8")
    connection.sendall(struct.pack("!I", len(data)) + data)

def receive_json(connection):
    packet_length = struct.unpack("!I", recv_exact(connection, 4))[0]
    if not 0 < packet_length <= MAX_PACKET:
        raise ValueError("Kích thước gói tin không hợp lệ.")
    packet = recv_exact(connection, packet_length)
    envelope = json.loads(packet.decode("utf-8"))
    if not isinstance(envelope, dict):
        raise ValueError("Gói tin phải là một JSON object.")
    return envelope
```
