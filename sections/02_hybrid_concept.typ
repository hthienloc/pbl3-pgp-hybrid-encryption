= Vì sao PGP sử dụng mã hóa lai?

Mô hình *Hybrid Encryption* kết hợp hài hòa ưu điểm của cả hai trường phái: mã hóa đối xứng và mã hóa bất đối xứng trong cùng một chu trình xử lý an toàn.

#align(center)[
  #table(
    columns: (1fr, 1fr),
    fill: (x, y) => if y == 0 { rgb("#e0e7ff") } else if calc.even(y) { rgb("#f8fafc") } else { none },
    stroke: 0.5pt + rgb("#cbd5e1"),
    inset: 9pt,
    [*AES – Mã hóa đối xứng*], [*RSA – Mã hóa bất đối xứng*],
    [Sử dụng khóa phiên (Session Key).], [Sử dụng cặp Public Key và Private Key.],
    [Tốc độ mã hóa cực nhanh, tối ưu cho dữ liệu có kích thước lớn.], [Chi phí tính toán cao, xử lý dữ liệu chậm hơn nhiều so với AES.],
    [Khó khăn: Cần một cơ chế an toàn để phân phối khóa phiên đến người nhận.], [Giải pháp: Dùng Public Key của người nhận để mã hóa và bảo vệ khóa phiên an toàn khi truyền tải.],
    [Không hỗ trợ trao đổi khóa trực tiếp trên kênh mở.], [Không phù hợp để mã hóa trực tiếp toàn bộ khối dữ liệu lớn.]
  )
]

== Lý do kết hợp trong PGP
- *AES* có hiệu năng vượt trội, phù hợp mã hóa khối lượng dữ liệu thực tế lớn từ người dùng, nhưng yêu cầu hai phía phải đồng thuận khóa bí mật trước khi liên lạc.
- *RSA* giải quyết triệt để bài toán phân phối khóa trên môi trường mạng công cộng mà không cần chia sẻ trước khóa bí mật, tuy nhiên lại tiêu tốn tài nguyên xử lý lớn đối với dữ liệu dài.
- *Kết hợp:* PGP khai thác thế mạnh của từng thuật toán:
  - Sử dụng *AES* để mã hóa nội dung thông điệp bằng một khóa phiên ngẫu nhiên.
  - Sử dụng *RSA* để mã hóa khóa phiên này bằng Public Key của người nhận.

*Kết luận then chốt:*
$ "Bản mã PGP" = { "RSA"_(E_("Bob"))("Session Key"), "AES"_("Session Key")("Plaintext") } $
*AES mã hóa thông điệp; RSA mã hóa khóa phiên.*
