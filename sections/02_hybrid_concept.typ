#import "../styles.typ": report-table

= Vì sao PGP sử dụng mã hóa lai?

Mã hóa lai giải quyết bài toán dung hòa giữa tốc độ xử lý và khả năng phân phối khóa an toàn:

#align(center)[
  #report-table(
    columns: (1fr, 1fr),
    headers: ("AES – Mã hóa đối xứng", "RSA – Mã hóa bất đối xứng"),
    rows: (
      ([Dùng chung một Session Key bí mật.], [Dùng cặp Public Key và Private Key.]),
      ([Tốc độ phần cứng cực nhanh, tối ưu cho dữ liệu lớn.], [Tốc độ chậm do tính lũy thừa mô-đun trên số nguyên lớn.]),
      ([Cần kênh an toàn để trao đổi khóa phiên.], [Cho phép gửi khóa an toàn qua kênh công khai.]),
      ([Không mã hóa được nếu chưa có khóa chung.], [Không tối ưu để mã hóa trực tiếp khối dữ liệu dài.]),
    )
  )
]

== Nguyên lý kết hợp
Trong kịch bản truyền thông giữa Alice (người gửi) và Bob (người nhận):
- AES chịu trách nhiệm mã hóa toàn bộ dữ liệu người dùng bằng khóa ngẫu nhiên $K$ do Alice sinh ra.
- RSA chịu trách nhiệm mã hóa duy nhất khóa $K$ bằng Public Key của Bob ($e_B$). Chỉ có Bob sở hữu Private Key ($d_B$) tương ứng mới có thể giải mã lấy lại $K$.

Công thức đóng gói dữ liệu của PGP:
$ "PGP Packet" = { "RSA"_(e_B)(K), quad "AES"_K (M) } $

*Kết luận:* AES bảo vệ dữ liệu, RSA bảo vệ khóa phiên.
