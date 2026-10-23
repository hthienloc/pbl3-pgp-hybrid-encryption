= Thuật toán RSA – Quá trình tạo khóa

RSA là một hệ mật mã hóa bất đối xứng dựa trên độ khó tính toán của bài toán phân tích các số nguyên rất lớn thành tích các thừa số nguyên tố. Dưới đây là các bước tạo khóa cùng ví dụ số học minh họa với hai số nguyên tố nhỏ nhằm quan sát chi tiết từng phép tính.

#align(center)[
  #table(
    columns: (auto, 1.5fr, 1fr),
    fill: (x, y) => if y == 0 { rgb("#e0e7ff") } else if calc.even(y) { rgb("#f8fafc") } else { none },
    stroke: 0.5pt + rgb("#cbd5e1"),
    inset: 8pt,
    [*Bước*], [*Phép tính toán học*], [*Kết quả minh họa*],
    [1. Chọn số nguyên tố], [Chọn ngẫu nhiên 2 số nguyên tố lớn $p, q$ ($p eq.not q$)], [$p = 61, q = 53$],
    [2. Tính Modulus], [$n = p times q = 61 times 53$], [$n = 3233$],
    [3. Hàm Euler Phi], [$phi(n) = (p - 1)(q - 1) = 60 times 52$], [$phi(n) = 3120$],
    [4. Chọn số mũ công khai $e$], [$1 < e < phi(n)$ sao cho $gcd(e, phi(n)) = 1$], [$e = 17$],
    [5. Tìm số mũ bí mật $d$], [$e times d equiv 1 mod phi(n)$ (Nghịch đảo modulo)], [$d = 2753$]
  )
]

== Cặp khóa thu được
- *Public Key (Khóa công khai):* $(e, n) = (17, 3233)$ — công khai cho toàn mạng.
- *Private Key (Khóa bí mật):* $(d, n) = (2753, 3233)$ — giữ bí mật tuyệt đối tại phía nhận.

#import "../components.typ": info-box
#info-box(title: "Lưu ý an toàn mật mã học")[
  Mô hình trên là _Textbook RSA_ không sử dụng cơ chế đệm an toàn (OAEP padding), đồng thời chọn số nguyên tố cực nhỏ để minh họa trực quan. Trong môi trường bảo mật thực tế, kích thước của số nguyên tố $p, q$ tối thiểu phải đạt độ dài từ 1024-bit đến 2048-bit trở lên để chống lại các thuật toán phân tích số nguyên lớn (như General Number Field Sieve).
]
