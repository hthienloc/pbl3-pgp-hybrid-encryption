= Cài đặt RSA bằng Python

Nhóm đã tự triển khai toàn bộ các phép toán nền tảng của RSA trong tệp `src/rsa.py` bằng ngôn ngữ Python thuần, hoàn toàn không phụ thuộc vào thư viện mật mã học bên ngoài.

== Bảng đặc tả các hàm chính

#align(center)[
  #table(
    columns: (1.2fr, 2fr),
    fill: (x, y) => if y == 0 { rgb("#e0e7ff") } else if calc.even(y) { rgb("#f8fafc") } else { none },
    stroke: 0.5pt + rgb("#cbd5e1"),
    inset: 8pt,
    [*Tên hàm*], [*Mô tả chức năng & Giải thuật*],
    [`extended_gcd(a, b)`], [Cài đặt giải thuật Euclid mở rộng: đệ quy tìm ước chung lớn nhất và các hệ số Bézout $x, y$ sao cho $a x + b y = gcd(a, b)$. Dùng để tính số mũ bí mật $d$.],
    [`generate_rsa_keys(p, q)`], [Giai đoạn sinh khóa: Tính $n = p times q$, $phi = (p-1)(q-1)$, chọn $e = 17$, tính $d$ qua `extended_gcd(e, phi)`, trả về cặp `((e, n), (d, n))`.],
    [`rsa_encrypt(pub_key, M)`], [Giai đoạn mã hóa: Áp dụng công thức $C = M^e mod n$ sử dụng hàm lũy thừa modulo tối ưu `pow(M, e, n)`.],
    [`rsa_decrypt(priv_key, C)`], [Giai đoạn giải mã: Áp dụng công thức $M = C^d mod n$ thông qua `pow(C, d, n)`.]
  )
]

== Mã nguồn cài đặt giải thuật Euclid mở rộng và RSA

```python
def extended_gcd(a, b):
    """Giải thuật Euclid mở rộng tìm gcd(a, b) và x, y thỏa mãn a*x + b*y = gcd"""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def generate_rsa_keys(p=61, q=53, e=17):
    """Sinh cặp khóa Public Key (e, n) và Private Key (d, n)"""
    n = p * q
    phi = (p - 1) * (q - 1)
    gcd, x, _ = extended_gcd(e, phi)
    d = (x % phi + phi) % phi  # Đảm bảo d > 0
    return (e, n), (d, n)

def rsa_encrypt(public_key, plaintext_num):
    e, n = public_key
    return pow(plaintext_num, e, n)

def rsa_decrypt(private_key, ciphertext_num):
    d, n = private_key
    return pow(ciphertext_num, d, n)
```

#import "../components.typ": info-box
#info-box(title: "Điểm cần nhớ")[
  Cả hai hàm `rsa_encrypt` và `rsa_decrypt` đều thực thi thuật toán tính lũy thừa theo mô-đun (`pow(base, exp, mod)`), chỉ khác nhau ở số mũ: quá trình mã hóa sử dụng số mũ công khai $e$, trong khi quá trình giải mã sử dụng số mũ bí mật $d$.
]
