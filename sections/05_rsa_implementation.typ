= Cài đặt RSA bằng Python

Nhóm đã tự triển khai toàn bộ các phép toán nền tảng của RSA trong tệp `rsa.py` bằng ngôn ngữ Python thuần, hoàn toàn không phụ thuộc vào thư viện mật mã học bên ngoài.

== Bảng đặc tả các hàm chính

#align(center)[
  #table(
    columns: (1.2fr, 2fr),
    fill: (x, y) => if y == 0 { rgb("#e0e7ff") } else if calc.even(y) { rgb("#f8fafc") } else { none },
    stroke: 0.5pt + rgb("#cbd5e1"),
    inset: 8pt,
    [*Tên hàm*], [*Mô tả chức năng & Giải thuật*],
    [`extended_gcd(a, b)`], [Cài đặt giải thuật Euclid mở rộng: tìm ước chung lớn nhất và các hệ số $x, y$ thỏa mãn phương trình Bézout $a x + b y = gcd(a, b)$. Dùng để tìm nghịch đảo modulo $d$ sao cho $(d times e) mod phi(n) = 1$.],
    [`generate_rsa_keys(p, q)`], [Giai đoạn sinh khóa: Tính $n = p times q$, $phi = (p-1)(q-1)$, chọn $e = 17$, tính $d$ qua `extended_gcd(e, phi)`, trả về cặp `((e, n), (d, n))`.],
    [`rsa_encrypt(pub_key, M)`], [Giai đoạn mã hóa: Áp dụng công thức $C = M^e mod n$ sử dụng hàm lũy thừa modulo tối ưu `pow(M, e, n)`.],
    [`rsa_decrypt(priv_key, C)`], [Giai đoạn giải mã: Áp dụng công thức $M = C^d mod n$ thông qua `pow(C, d, n)`.]
  )
]

== Mã nguồn then chốt

```python
# Giai đoạn 1: Sinh khóa (generate_rsa_keys)
n = p * q
phi = (p - 1) * (q - 1)
gcd, x, y = extended_gcd(e, phi)
d = (x % phi + phi) % phi

# Giai đoạn 2 & 3: Mã hóa / Giải mã
C = rsa_encrypt(pub_key, M)          # tương đương pow(M, e, n)
M_giai_ma = rsa_decrypt(priv_key, C)  # tương đương pow(C, d, n)
```

#import "../components.typ": info-box
#info-box(title: "Điểm cần nhớ")[
  Cả hai hàm `rsa_encrypt` và `rsa_decrypt` đều thực thi thuật toán tính lũy thừa theo mô-đun (`pow(base, exp, mod)`), chỉ khác nhau ở số mũ: quá trình mã hóa sử dụng số mũ công khai $e$, trong khi quá trình giải mã sử dụng số mũ bí mật $d$.
]
