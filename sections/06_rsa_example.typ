= Ví dụ RSA – Mã hóa và giải mã

Để kiểm chứng tính đúng đắn của giải thuật toán học đã lập trình, nhóm thực hiện chạy thử nghiệm quy trình với bộ tham số:
- Cặp khóa công khai / bí mật: $e = 17$, $d = 2753$, $n = 3233$.
- Thông điệp dạng số cần mã hóa: $M = 125$.

#align(center)[
  #table(
    columns: (1fr, 1.8fr, 1fr),
    fill: (x, y) => if y == 0 { rgb("#e0e7ff") } else if calc.even(y) { rgb("#f8fafc") } else { none },
    stroke: 0.5pt + rgb("#cbd5e1"),
    inset: 9pt,
    [*Giai đoạn*], [*Công thức toán học*], [*Kết quả*],
    [Thông điệp gốc], [Giá trị ban đầu $M$], [$125$],
    [Mã hóa bằng Public Key], [$C = M^e mod n = 125^(17) mod 3233$], [$1516$],
    [Giải mã bằng Private Key], [$M_("giải mã") = C^d mod n = 1516^(2753) mod 3233$], [$125$]
  )
]

== Chuỗi chuyển đổi dữ liệu
$ M = 125 quad -->^("Mã hóa với " e=17) quad C = 1516 quad -->^("Giải mã với " d=2753) quad M_("khôi phục") = 125 $

Trong chương trình Python, điều kiện xác nhận:
```python
if M == M_giai_ma:
    print("Dữ liệu được khôi phục chính xác 100%!")
```
Kết quả thực nghiệm chứng minh thuật toán RSA tự cài đặt tái hiện chính xác nguyên lý toán học của hệ mật mã hóa khóa công khai.
