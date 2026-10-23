= Danh mục thuật ngữ và viết tắt

Để văn phong báo cáo cô đọng, trong toàn bộ tài liệu các thuật ngữ mật mã học và mạng máy tính được phân loại và chuẩn hóa theo danh mục dưới đây:

#align(center)[
  #table(
    columns: (1fr, 1.2fr, 1.4fr, 2.2fr),
    fill: (x, y) => if y == 0 { rgb("#e0e7ff") } else if calc.even(y) { rgb("#f8fafc") } else { none },
    stroke: 0.5pt + rgb("#cbd5e1"),
    inset: 7pt,
    [*Ký hiệu / Thuật ngữ*], [*Phân loại*], [*Tên tiếng Anh*], [*Ý nghĩa chuyên môn*],
    [*PGP*], [Tiêu chuẩn], [Pretty Good Privacy], [Giao thức mã hóa bảo vệ quyền riêng tư qua kênh mạng mở.],
    [*RSA*], [Bất đối xứng], [Rivest – Shamir – Adleman], [Hệ mật mã khóa công khai dựa trên độ khó bài toán phân tích số nguyên lớn.],
    [*AES*], [Đối xứng], [Advanced Encryption Standard], [Chuẩn mã hóa đối xứng khối tốc độ cao, dùng ma trận thay thế hoán vị SPN.],
    [*Hybrid Encryption*], [Kiến trúc], [Mã hóa lai], [Mô hình kết hợp AES (mã hóa dữ liệu) và RSA (bảo vệ khóa phiên).],
    [*Session Key*], [Khóa], [Khóa phiên], [Khóa đối xứng ngẫu nhiên chỉ có giá trị cho một phiên truyền thông duy nhất.],
    [*Public / Private Key*], [Khóa], [Khóa công khai / Bí mật], [Cặp khóa bất đối xứng: chia sẻ công khai để mã hóa / giữ bí mật để giải mã.],
    [*PKESK*], [Gói tin PGP], [Public-Key Encrypted Session Key], [Gói tin chứa Session Key đã được mã hóa bằng khóa công khai người nhận.],
    [*SEIPD*], [Gói tin PGP], [Symmetrically Encrypted Integrity Protected Data], [Gói tin chứa dữ liệu đã được mã hóa đối xứng kèm cơ chế kiểm tra toàn vẹn.],
    [*AES-GCM*], [Chế độ AES], [Galois/Counter Mode], [Chế độ mã hóa xác thực (AEAD) cung cấp đồng thời tính bí mật và toàn vẹn.],
    [*Authentication Tag*], [Toàn vẹn], [Mã kiểm thực MAC], [Giá trị kiểm tra giúp phía nhận phát hiện mọi hành vi can thiệp hay sửa đổi bản mã.],
    [*OAEP*], [Cơ chế đệm], [Optimal Asymmetric Encryption Padding], [Cơ chế đệm ngẫu nhiên an toàn chống tấn công chọn bản mã cho RSA.]
  )
]
