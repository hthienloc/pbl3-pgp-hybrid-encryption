"""
Thuật toán RSA cơ bản (Textbook RSA) phục vụ mô phỏng nguyên lý PGP Hybrid Encryption.
Cài đặt bằng Python thuần, không sử dụng thư viện mật mã học bên ngoài.
"""

import random


def extended_gcd(a, b):
    """
    Thuật toán Euclid mở rộng:
    Tìm gcd(a, b) và các hệ số x, y sao cho: a*x + b*y = gcd(a, b)
    Dùng để tính nghịch đảo modulo d sao cho: (d * e) % phi == 1
    """
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y


def is_prime(n, k=20):
    """Kiểm tra số nguyên tố bằng thuật toán xác suất Miller-Rabin."""
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
    """Sinh số nguyên tố ngẫu nhiên có độ dài bit chỉ định."""
    rng = random.SystemRandom()
    while True:
        candidate = rng.getrandbits(bits) | (1 << (bits - 1)) | 1
        if is_prime(candidate):
            return candidate


def generate_rsa_keys(p=None, q=None, e=65537, bits=256):
    """
    Giai đoạn 1: Sinh cặp khóa RSA
    - n = p * q (Modulus)
    - phi = (p - 1) * (q - 1) (Euler Totient)
    - e: số mũ công khai (gcd(e, phi) == 1)
    - d: số mũ bí mật (nghịch đảo modulo của e theo phi)
    """
    if p is None or q is None:
        prime_bits = max(bits // 2, 72)
        while True:
            p = generate_prime(prime_bits)
            q = generate_prime(prime_bits)
            if p != q and extended_gcd(e, (p - 1) * (q - 1))[0] == 1:
                break

    n = p * q
    phi = (p - 1) * (q - 1)
    gcd, x, _ = extended_gcd(e, phi)
    if gcd != 1:
        raise ValueError("e và phi(n) không nguyên tố cùng nhau.")
    d = (x % phi + phi) % phi
    return (e, n), (d, n)


def rsa_encrypt(public_key, plaintext_num):
    """
    Giai đoạn 2: Mã hóa dữ liệu số bằng Public Key (e, n)
    Công thức: C = (M ^ e) mod n
    """
    e, n = public_key
    if plaintext_num >= n:
        raise ValueError("Dữ liệu cần mã hóa phải nhỏ hơn modulus n.")
    return pow(plaintext_num, e, n)


def rsa_decrypt(private_key, ciphertext_num):
    """
    Giai đoạn 3: Giải mã dữ liệu số bằng Private Key (d, n)
    Công thức: M = (C ^ d) mod n
    """
    d, n = private_key
    return pow(ciphertext_num, d, n)


if __name__ == "__main__":
    p, q = 61, 53
    pub_key, priv_key = generate_rsa_keys(p, q, e=17)
    print(f"Public Key (e, n): {pub_key}")
    print(f"Private Key (d, n): {priv_key}")

    M = 125
    C = rsa_encrypt(pub_key, M)
    M_decrypted = rsa_decrypt(priv_key, C)

    print(f"Thông điệp gốc: {M}")
    print(f"Bản mã sau khi mã hóa: {C}")
    print(f"Bản rõ sau khi giải mã: {M_decrypted}")
    assert M == M_decrypted, "Giải mã thất bại!"
    print("Kiểm thử thành công: Dữ liệu được khôi phục chính xác 100%!")
