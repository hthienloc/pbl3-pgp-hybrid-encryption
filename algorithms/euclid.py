"""
Mô-đun giải thuật Euclid mở rộng và tính nghịch đảo modulo.
Cung cấp nền tảng toán học để tìm khóa bí mật d trong RSA: e * d ≡ 1 (mod phi).
"""

def extended_gcd(a, b):
    """
    Giải thuật Euclid mở rộng tìm ước chung lớn nhất gcd(a, b)
    và các hệ số Bézout x, y sao cho: a*x + b*y = gcd(a, b).
    """
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def mod_inverse(e, phi):
    """
    Tìm phần tử nghịch đảo modulo d = e^(-1) mod phi.
    Ném lỗi ValueError nếu e và phi không nguyên tố cùng nhau.
    """
    gcd, x, _ = extended_gcd(e, phi)
    if gcd != 1:
        raise ValueError(f"Không tồn tại nghịch đảo modulo: gcd({e}, {phi}) = {gcd} != 1")
    return (x % phi + phi) % phi

if __name__ == "__main__":
    e = 17
    phi = 3120
    d = mod_inverse(e, phi)
    print(f"Kiểm thử Euclid mở rộng:")
    print(f"e = {e}, phi(n) = {phi}")
    print(f"Khóa bí mật d = {d}")
    print(f"Kiểm tra: ({e} * {d}) mod {phi} = {(e * d) % phi}")
