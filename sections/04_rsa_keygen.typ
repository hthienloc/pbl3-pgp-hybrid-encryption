= Thuật toán RSA – Quá trình tạo khóa

Thuật toán RSA @rivest1978 dựa trên tính bất đối xứng tính toán của bài toán phân tích thừa số nguyên tố. Dưới đây là các bước sinh khóa với hai số nguyên tố nhỏ $p=61, q=53$:

#align(center)[
  #table(
    columns: (auto, 1.6fr, 1fr),
    fill: (x, y) => if y == 0 { rgb("#e0e7ff") } else if calc.even(y) { rgb("#f8fafc") } else { none },
    stroke: 0.5pt + rgb("#cbd5e1"),
    inset: 8pt,
    [*Bước*], [*Phép tính toán học*], [*Kết quả minh họa*],
    [1. Số nguyên tố], [Chọn ngẫu nhiên $p, q$ ($p eq.not q$)], [$p = 61, q = 53$],
    [2. Modulus], [$n = p times q = 61 times 53$], [$n = 3233$],
    [3. Hàm Euler Phi], [$phi(n) = (p - 1)(q - 1) = 60 times 52$], [$phi(n) = 3120$],
    [4. Khóa công khai $e$], [Chọn $1 < e < phi(n)$ sao cho $gcd(e, phi(n)) = 1$], [$e = 17$],
    [5. Khóa bí mật $d$], [$e times d equiv 1 mod phi(n)$ (Nghịch đảo modulo)], [$d = 2753$]
  )
]

== Cơ chế giải thuật Euclid mở rộng tìm $d$
Phương trình đồng dư $17 d equiv 1 mod 3120$ tương đương phương trình Bézout:
$ 17 d + 3120 y = 1 $
Thực hiện chia Euclid:
1. $3120 = 183 times 17 + 9$
2. $17 = 1 times 9 + 8$
3. $9 = 1 times 8 + 1$

Biểu diễn ngược số dư $1$:
$ 1 = 9 - (17 - 9) = 2 times (3120 - 183 times 17) - 17 = 2 times 3120 - 367 times 17 $
Hệ số của $17$ là $x = -367$. Lấy modulo theo $phi(n) = 3120$:
$ d = -367 mod 3120 = 3120 - 367 = 2753 $

*Cặp khóa thu được:* Public Key $(e=17, n=3233)$ và Private Key $(d=2753, n=3233)$.

== Chứng minh tính đúng đắn của RSA qua Định lý Euler

Thuật toán giải mã RSA khôi phục chính xác thông điệp gốc dựa trên cơ sở lý thuyết số học sau:
1. *Điều kiện biên không gian bản rõ:* Giá trị số học của thông điệp phải thỏa mãn $M in ZZ_n$ ($0 <= M < n$).
2. *Quan hệ giữa cặp khóa:* Do $e d equiv 1 mod phi(n)$, tồn tại số nguyên $k >= 1$ sao cho:
$ e d = 1 + k phi(n) = 1 + k (p - 1)(q - 1) $
3. *Áp dụng Định lý Euler:* Với mọi $M$ nguyên tố cùng nhau với $n$ ($gcd(M, n) = 1$):
$ M^(phi(n)) equiv 1 mod n $
4. *Biến đổi giải mã:*
$ M' = C^d mod n = (M^e)^d mod n = M^(e d) mod n = M^(1 + k phi(n)) mod n $
$ M' = M times (M^(phi(n)))^k mod n equiv M times 1^k mod n equiv M mod n $
Do $0 <= M < n$, giá trị thu được sau giải mã $M'$ đồng nhất hoàn toàn với bản rõ ban đầu $M$.

#import "../components.typ": info-box
#info-box(title: "Khuyến nghị tiêu chuẩn")[
  Mô hình trên là Textbook RSA. Tiêu chuẩn RFC 8017 @rfc8017 yêu cầu kích thước khóa tối thiểu 2048-bit và bắt buộc kết hợp cơ chế đệm an toàn (RSA-OAEP) để chống các kỹ thuật tấn công chọn bản mã.
]
