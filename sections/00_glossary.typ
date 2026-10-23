= Danh mục thuật ngữ và viết tắt

Để văn phong báo cáo cô đọng, trong toàn bộ tài liệu các thuật ngữ mật mã học và mạng máy tính được chuẩn hóa theo danh mục dưới đây:

#align(center)[
  #table(
    columns: (1fr, 1.6fr, 2.2fr),
    fill: (x, y) => if y == 0 { rgb("#e0e7ff") } else if calc.even(y) { rgb("#f8fafc") } else { none },
    stroke: 0.5pt + rgb("#cbd5e1"),
    inset: 8pt,
    [*Ký hiệu / Thuật ngữ*], [*Tên tiếng Anh đầy đủ*], [*Định nghĩa và ý nghĩa chuyên môn*],
    [*PGP*], [Pretty Good Privacy], [Tiêu chuẩn mã hóa dữ liệu truyền thông và bảo vệ quyền riêng tư qua kênh mạng.],
    [*RSA*], [Rivest – Shamir – Adleman], [Hệ mật mã khóa công khai dựa trên độ khó bài toán phân tích số nguyên lớn.],
    [*AES*], [Advanced Encryption Standard], [Chuẩn mã hóa đối xứng khối tốc độ cao, sử dụng ma trận trạng thái thay thế và hoán vị.],
    [*Hybrid Encryption*], [Mã hóa lai], [Mô hình kết hợp mã hóa đối xứng (mã hóa dữ liệu) và bất đối xứng (bảo vệ khóa phiên).],
    [*Session Key*], [Khóa phiên], [Khóa đối xứng ngẫu nhiên chỉ có giá trị cho một phiên truyền thông duy nhất.],
    [*Public Key*], [Khóa công khai], [Thành phần khóa trong hệ mật bất đối xứng được chia sẻ công khai để mã hóa.],
    [*Private Key*], [Khóa bí mật], [Thành phần khóa chỉ do chủ sở hữu nắm giữ để giải mã dữ liệu.],
    [*Plaintext / Ciphertext*], [Bản rõ / Bản mã], [Dữ liệu ban đầu chưa mã hóa / Dữ liệu đã được chuyển đổi sang dạng bí mật.],
    [*PKESK*], [Public-Key Encrypted Session Key], [Gói tin chứa khóa phiên đã được mã hóa bằng khóa công khai của người nhận.],
    [*SEIPD*], [Symmetrically Encrypted Integrity Protected Data], [Gói tin chứa dữ liệu đã được mã hóa đối xứng kèm mã phát hiện sửa đổi.],
    [*GCM*], [Galois/Counter Mode], [Chế độ mã hóa xác thực cung cấp đồng thời tính bảo mật và tính toàn vẹn dữ liệu.],
    [*Authentication Tag*], [Mã kiểm thực toàn vẹn (MAC)], [Giá trị đính kèm giúp phía nhận phát hiện mọi hành vi can thiệp hay sửa đổi bản mã.],
    [*OAEP*], [Optimal Asymmetric Encryption Padding], [Cơ chế đệm ngẫu nhiên bảo đảm an toàn chống lại các tấn công chọn bản mã cho RSA.]
  )
]
