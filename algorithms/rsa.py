"""
Mô-đun thuật toán RSA số học.
Cài đặt quá trình sinh khóa, mã hóa và giải mã số học.
"""

from .euclid import mod_inverse

def generate_rsa_keys(p=61, q=53, e=17):
    """
    Sinh cặp khóa Public Key (e, n) và Private Key (d, n).
    """
    n = p * q
    phi = (p - 1) * (q - 1)
    d = mod_inverse(e, phi)
    return (e, n), (d, n)

def rsa_encrypt(public_key, plaintext_num):
    """
    Mã hóa số học RSA: C = M^e mod n.
    """
    e, n = public_key
    if plaintext_num >= n:
        raise ValueError(f"Dữ liệu ({plaintext_num}) phải nhỏ hơn modulus n ({n})")
    return pow(plaintext_num, e, n)

def rsa_decrypt(private_key, ciphertext_num):
    """
    Giải mã số học RSA: M = C^d mod n.
    """
    d, n = private_key
    return pow(ciphertext_num, d, n)

if __name__ == "__main__":
    pub_key, priv_key = generate_rsa_keys(p=61, q=53, e=17)
    M = 125
    C = rsa_encrypt(pub_key, M)
    M_prime = rsa_decrypt(priv_key, C)
    print("Kiểm thử module RSA:")
    print(f"Public Key (e, n): {pub_key}")
    print(f"Private Key (d, n): {priv_key}")
    print(f"Bản rõ: {M} -> Bản mã: {C} -> Khôi phục: {M_prime}")
    assert M == M_prime, "Lỗi giải mã!"
    print("Khôi phục thành công.")
