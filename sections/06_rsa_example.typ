#import "../styles.typ": report-table
#import "../figures.typ": fig-rsa-numeric-example

= Ví dụ số học RSA – Tạo khóa, mã hóa và giải mã

Để minh họa nguyên lý toán học của hệ mật mã RSA, phần này thực nghiệm tính toán trên không gian số nhỏ có thể kiểm tra từng bước bằng tay.

== Khởi tạo hệ thống và tính toán khóa

1. *Chọn hai số nguyên tố nhỏ:*
   $ p = 61, quad q = 53 $
2. *Tính Modulus hệ thống $n$:*
   $ n = p times q = 61 times 53 = 3233 $
3. *Tính giá trị hàm Euler $phi(n)$:*
   $ phi(n) = (p - 1)(q - 1) = 60 times 52 = 3120 $
4. *Chọn số mũ công khai $e$:*
   Chọn $e = 17$ thỏa mãn $1 < e < 3120$ và $gcd(17, 3120) = 1$.
5. *Tính số mũ bí mật $d$ bằng thuật toán Euclid mở rộng:*
   Tìm $d$ sao cho $17 times d equiv 1 mod 3120$:
   $ 17 times 2753 = 46801 = 15 times 3120 + 1 => d = 2753 $

#align(center)[
  #report-table(
    columns: (1.2fr, 1.2fr, 2fr),
    headers: ("Loại khóa", "Thành phần", "Giá trị số học"),
    rows: (
      ([Public Key], [$(e, n)$], [$(17, 3233)$]),
      ([Private Key], [$(d, n)$], [$(2753, 3233)$]),
    )
  )
]

== Thực nghiệm mã hóa và giải mã

Giả sử Alice muốn truyền thông điệp số $M = 125$ ($M < n$) cho Bob:
- *Mã hóa (Alice thực hiện):*
  $ C = M^e mod n = 125^17 mod 3233 = 1516 $
- *Giải mã (Bob thực hiện):*
  $ M' = C^d mod n = 1516^2753 mod 3233 = 125 $

#align(center)[
  #report-table(
    columns: (1fr, 1.2fr, 1.8fr),
    headers: ("Giai đoạn", "Công thức", "Kết quả tính toán"),
    rows: (
      ([Bản rõ gốc], [$M$], [$125$]),
      ([Bản mã], [$C = M^e mod n$], [$1516$]),
      ([Bản giải mã], [$M' = C^d mod n$], [$125$ ($= M$)]),
    )
  )
]

== Chuỗi chuyển đổi dữ liệu và khóa

#v(0.3em)
#align(center)[
  #fig-rsa-numeric-example
]
#v(0.3em)

Quá trình giải mã cho kết quả $M' = 125$, trùng khớp hoàn toàn với giá trị gốc $M$, xác nhận tính toàn vẹn của cặp phép biến đổi $M^e mod n$ và $C^d mod n$.
