= Vì sao PGP sử dụng mã hóa lai?

Mã hóa lai giải quyết bài toán dung hòa giữa tốc độ xử lý và khả năng phân phối khóa an toàn:

#align(center)[
  #table(
    columns: (1fr, 1fr),
    fill: (x, y) => if y == 0 { rgb("#e0e7ff") } else if calc.even(y) { rgb("#f8fafc") } else { none },
    stroke: 0.5pt + rgb("#cbd5e1"),
    inset: 8pt,
    [*AES – Mã hóa đối xứng @nist_fips197*], [*RSA – Mã hóa bất đối xứng @rivest1978*],
    [Dùng chung một Session Key bí mật.], [Dùng cặp Public Key và Private Key.],
    [Tốc độ phần cứng cực nhanh, tối ưu cho dữ liệu lớn.], [Tốc độ chậm do tính lũy thừa mô-đun trên số nguyên lớn.],
    [Cần kênh an toàn để trao đổi khóa phiên.], [Cho phép gửi khóa an toàn qua kênh công khai.],
    [Không mã hóa được nếu chưa có khóa chung.], [Không tối ưu để mã hóa trực tiếp khối dữ liệu dài.]
  )
]

== Nguyên lý kết hợp
- AES chịu trách nhiệm mã hóa toàn bộ dữ liệu người dùng bằng khóa ngẫu nhiên $K$.
- RSA chịu trách nhiệm mã hóa duy nhất khóa $K$ bằng Public Key của Bob ($E_B$).

Công thức đóng gói dữ liệu của PGP:
$ "Gói tin PGP" = { "RSA"_(E_B)(K), quad "AES"_K ("Plaintext") } $

*Kết luận:* AES bảo vệ dữ liệu, RSA bảo vệ khóa phiên.
