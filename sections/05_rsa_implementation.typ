= Cài đặt RSA bằng Python

Thuật toán RSA được tổ chức thành các mô-đun độc lập trong thư mục `algorithms/` nhằm phục vụ việc kiểm thử từng thành phần:

== Bảng đặc tả các hàm chính

#align(center)[
  #table(
    columns: (1.2fr, 2fr),
    fill: (x, y) => if y == 0 { rgb("#e0e7ff") } else if calc.even(y) { rgb("#f8fafc") } else { none },
    stroke: 0.5pt + rgb("#cbd5e1"),
    inset: 8pt,
    [*Tên hàm*], [*Mô tả chức năng & Giải thuật*],
    [`extended_gcd(a, b)`], [Cài đặt giải thuật Euclid mở rộng: đệ quy tìm ước chung lớn nhất và các hệ số Bézout $x, y$ sao cho $a x + b y = gcd(a, b)$. Dùng để tính số mũ bí mật $d$.],
    [`generate_rsa_keys(p, q)`], [Giai đoạn sinh khóa: Tính $n = p times q$, $phi = (p-1)(q-1)$, chọn $e = 17$, tính $d$ qua `mod_inverse(e, phi)`, trả về cặp `((e, n), (d, n))`.],
    [`rsa_encrypt(pub_key, M)`], [Giai đoạn mã hóa: Áp dụng công thức $C = M^e mod n$ sử dụng hàm lũy thừa modulo tối ưu `pow(M, e, n)`.],
    [`rsa_decrypt(priv_key, C)`], [Giai đoạn giải mã: Áp dụng công thức $M = C^d mod n$ thông qua `pow(C, d, n)`.]
  )
]

== Mã nguồn giải thuật Euclid mở rộng (`algorithms/euclid.py`)

#raw(read("../algorithms/euclid.py"), lang: "python")

== Mã nguồn thuật toán RSA (`algorithms/rsa.py`)

#raw(read("../algorithms/rsa.py"), lang: "python")

== Kết quả thực thi (`algorithms/rsa.py`)

Kết quả xuất ra khi chạy `python3 -m algorithms.rsa`:

```text
Public Key (e, n): (17, 3233)
Private Key (d, n): (2753, 3233)
Bản rõ: 125 -> Bản mã: 1516 -> Khôi phục: 125
Khôi phục thành công.
```

#import "../components.typ": info-box
#info-box(title: "Điểm cần nhớ")[
  Cả hai hàm `rsa_encrypt` và `rsa_decrypt` đều thực thi thuật toán tính lũy thừa theo mô-đun (`pow(base, exp, mod)`), chỉ khác nhau ở số mũ: quá trình mã hóa sử dụng số mũ công khai $e$, trong khi quá trình giải mã sử dụng số mũ bí mật $d$.
]
