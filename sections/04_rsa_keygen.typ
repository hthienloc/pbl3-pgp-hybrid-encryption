#import "../styles.typ": report-table

= Cơ sở toán học của thuật toán RSA

Thuật toán RSA @rivest1978 dựa trên tính bất đối xứng tính toán của bài toán phân tích thừa số nguyên tố: việc nhân hai số nguyên tố lớn rất dễ dàng về mặt tính toán, nhưng việc tìm lại hai thừa số đó từ tích của chúng là bài toán khó giải quyết trong thời gian đa thức.

== Mô hình toán học tổng quát (Lý thuyết)

Mô hình hệ mật mã RSA bao gồm 3 giải thuật hình thức:

1. *Sinh cặp khóa (Key Generation):*
  - Chọn ngẫu nhiên hai số nguyên tố lớn phân biệt $p$ và $q$.
  - Tính modulus $n = p times q$. Không gian khóa và bản mã được xác định trên vành số nguyên mô-đun $ZZ_n$.
  - Tính hàm phi Euler: $phi(n) = (p - 1)(q - 1)$.
  - Chọn số mũ công khai $e$ thỏa mãn điều kiện:
    $ 1 < e < phi(n) quad "và" quad gcd(e, phi(n)) = 1 $
  - Tính số mũ bí mật $d$ là phần tử nghịch đảo nhân của $e$ theo mô-đun $phi(n)$:
    $ e times d equiv 1 mod phi(n) $
  - Khóa công khai gồm cặp $(e, n)$, khóa bí mật tương ứng gồm cặp $(d, n)$.

2. *Mã hóa (Encryption):*
  - Bản rõ biểu diễn dưới dạng số nguyên $M in ZZ_n$ ($0 <= M < n$).
  - Bản mã $C$ được tính theo phép lũy thừa mô-đun:
    $ C = M^e mod n $

3. *Giải mã (Decryption):*
  - Từ bản mã $C$, khôi phục lại bản rõ $M'$ bằng khóa bí mật:
    $ M' = C^d mod n $

== Chứng minh tính đúng đắn qua Định lý Euler

Thuật toán giải mã RSA đảm bảo khôi phục chính xác thông điệp gốc dựa trên cơ sở lý thuyết số học sau:
1. *Điều kiện biên không gian bản rõ:* Giá trị số học của thông điệp thỏa mãn $M in ZZ_n$ ($0 <= M < n$).
2. *Quan hệ giữa cặp số mũ:* Do $e d equiv 1 mod phi(n)$, tồn tại số nguyên $k >= 1$ sao cho:
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
