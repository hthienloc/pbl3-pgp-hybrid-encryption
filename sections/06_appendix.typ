#pagebreak()

#heading(numbering: none, outlined: true)[PHỤ LỤC]

#heading(level: 2, numbering: none, outlined: true)[Phụ lục A: Cài đặt giải thuật Euclid mở rộng và RSA số học]

Mã nguồn mô-đun `algorithms/euclid.py`:

```python
def extended_gcd(a, b):
    if b == 0:
        return a, 1, 0
    gcd, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return gcd, x, y

def mod_inverse(e, phi):
    gcd, x, _ = extended_gcd(e, phi)
    if gcd != 1:
        raise ValueError(f'Nghich dao modulo khong ton tai vi gcd({e}, {phi}) = {gcd}')
    return (x % phi + phi) % phi
```

Mã nguồn mô-đun `algorithms/rsa.py`:

```python
import random
from .euclid import extended_gcd, mod_inverse

def is_prime(n, k=40):
    if n < 2: return False
    if n in (2, 3): return True
    if n % 2 == 0: return False
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    rng = random.SystemRandom()
    for _ in range(k):
        a = rng.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1: continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1: break
        else: return False
    return True

def generate_prime(bits=128):
    rng = random.SystemRandom()
    while True:
        cand = rng.getrandbits(bits) | (1 << (bits - 1)) | 1
        if is_prime(cand):
            return cand

def generate_rsa_keys(p=None, q=None, e=65537, bits=256):
    if p is None or q is None:
        prime_bits = max(bits // 2, 72)
        while True:
            p = generate_prime(prime_bits)
            q = generate_prime(prime_bits)
            if p != q and extended_gcd(e, (p - 1) * (q - 1))[0] == 1:
                break
    n = p * q
    phi = (p - 1) * (q - 1)
    d = mod_inverse(e, phi)
    return (e, n), (d, n)

def rsa_encrypt(public_key, plaintext_num):
    e, n = public_key
    if plaintext_num >= n:
        raise ValueError('Du lieu phai nho hon modulus n')
    return pow(plaintext_num, e, n)

def rsa_decrypt(private_key, ciphertext_num):
    d, n = private_key
    return pow(ciphertext_num, d, n)
```

#heading(level: 2, numbering: none, outlined: true)[Phụ lục B: Cài đặt AES-GCM và bộ đóng gói PGP Hybrid]

Mã nguồn mô-đun `algorithms/aes_gcm.py` và `algorithms/hybrid_pgp.py`:

```python
import os
from Cryptodome.Cipher import AES

def aes_gcm_encrypt(session_key, plaintext_bytes):
    nonce = os.urandom(12)
    cipher = AES.new(session_key, AES.MODE_GCM, nonce=nonce)
    ciphertext, auth_tag = cipher.encrypt_and_digest(plaintext_bytes)
    return ciphertext, nonce, auth_tag

def aes_gcm_decrypt(session_key, nonce_bytes, ciphertext_bytes, auth_tag_bytes):
    cipher = AES.new(session_key, AES.MODE_GCM, nonce=nonce_bytes)
    return cipher.decrypt_and_verify(ciphertext_bytes, auth_tag_bytes)

# --- Dong goi PGP Hybrid ---
def alice_encrypt_package(plaintext_str, bob_pub_key):
    session_key = os.urandom(16) # 128-bit key
    c_data, nonce, tag = aes_gcm_encrypt(session_key, plaintext_str.encode('utf-8'))
    k_int = int.from_bytes(session_key, byteorder='big')
    enc_session_key = rsa_encrypt(bob_pub_key, k_int)
    return {'enc_session_key': enc_session_key, 'nonce': nonce, 'ciphertext': c_data, 'auth_tag': tag}

def bob_decrypt_package(package, bob_priv_key):
    recovered_int = rsa_decrypt(bob_priv_key, package['enc_session_key'])
    recovered_key = (recovered_int & ((1 << 128) - 1)).to_bytes(16, byteorder='big')
    pt_bytes = aes_gcm_decrypt(recovered_key, package['nonce'], package['ciphertext'], package['auth_tag'])
    return pt_bytes.decode('utf-8')
```

#heading(level: 2, numbering: none, outlined: true)[Phụ lục C: Cài đặt truyền thông Socket TCP giữa 2 máy mạng LAN]

Cơ chế đóng khung 4 byte độ dài giải quyết phân mảnh byte stream:

```python
import struct, json

def recv_exact(sock, count):
    chunks = bytearray()
    while len(chunks) < count:
        chunk = sock.recv(min(count - len(chunks), 65536))
        if not chunk:
            raise ConnectionError('Ket noi bi ngat truoc khi nhan du du lieu.')
        chunks.extend(chunk)
    return bytes(chunks)

def send_json(sock, payload_dict):
    data = json.dumps(payload_dict, separators=(',', ':')).encode('utf-8')
    sock.sendall(struct.pack('!I', len(data)) + data)

def receive_json(sock):
    packet_length = struct.unpack('!I', recv_exact(sock, 4))[0]
    packet_data = recv_exact(sock, packet_length)
    return json.loads(packet_data.decode('utf-8'))
```
