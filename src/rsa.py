"""
Thuật toán RSA cơ bản (Textbook RSA) phục vụ mô phỏng nguyên lý PGP Hybrid Encryption.
Cài đặt bằng Python thuần, không sử dụng thư viện mật mã học bên ngoài.
"""

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

def generate_rsa_keys(p=61, q=53, e=17):
    """
    Giai đoạn 1: Sinh cặp khóa RSA
    - n = p * q (Modulus)
    - phi = (p - 1) * (q - 1) (Euler Totient)
    - e: số mũ công khai (gcd(e, phi) == 1)
    - d: số mũ bí mật (nghịch đảo modulo của e theo phi)
    """
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
