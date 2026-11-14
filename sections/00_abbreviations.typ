#import "../styles.typ": report-table

#heading(numbering: none, outlined: true)[DANH MỤC TỪ VIẾT TẮT VÀ THUẬT NGỮ]

#show figure.where(kind: table): set block(breakable: true)
#figure(
  report-table(
    columns: (0.9fr, 1.8fr, 2.2fr),
    headers: ("Từ viết tắt", "Tên tiếng Anh đầy đủ", "Giải nghĩa tiếng Việt"),
    rows: (
      ([AEAD], [Authenticated Encryption with Associated Data], [Mã hóa xác thực có dữ liệu bổ sung]),
      ([AES], [Advanced Encryption Standard], [Tiêu chuẩn mã hóa nâng cao]),
      ([CA], [Certificate Authority], [Cơ quan cấp phát chứng chỉ số]),
      ([CBC], [Cipher Block Chaining], [Chế độ nối khối bản mã]),
      ([CRT], [Chinese Remainder Theorem], [Định lý số dư Trung Hoa]),
      ([CSPRNG], [Cryptographically Secure Pseudorandom Number Generator], [Bộ sinh số giả ngẫu nhiên an toàn mật mã]),
      ([CTR], [Counter Mode], [Chế độ bộ đếm]),
      ([ECB], [Electronic Codebook], [Chế độ sổ mã điện tử]),
      ([GCM], [Galois/Counter Mode], [Chế độ Galois kết hợp bộ đếm]),
      ([GF], [Galois Field], [Trường hữu hạn Galois]),
      ([GHASH], [Galois Hash Function], [Hàm băm đại số trên trường hữu hạn]),
      ([IV / Nonce], [Initialization Vector / Number Used Once], [Vector khởi tạo / Giá trị dùng một lần]),
      ([JSON], [JavaScript Object Notation], [Định dạng trao đổi dữ liệu văn bản có cấu trúc]),
      ([LAN], [Local Area Network], [Mạng cục bộ]),
      ([MAC], [Message Authentication Code], [Mã xác thực thông điệp]),
      ([MITM], [Man-in-the-Middle], [Tấn công kẻ đứng giữa]),
      ([NIST], [National Institute of Standards and Technology], [Viện Tiêu chuẩn và Công nghệ Quốc gia Hoa Kỳ]),
      ([OAEP], [Optimal Asymmetric Encryption Padding], [Cơ chế đệm mã hóa bất đối xứng tối ưu]),
      ([OpenPGP], [Open Pretty Good Privacy], [Chuẩn giao thức mã hóa thư tín mở của IETF]),
      ([PGP], [Pretty Good Privacy], [Phần mềm và mô hình mã hóa lai do Phil Zimmermann phát triển]),
      ([RFC], [Request for Comments], [Tài liệu đặc tả kỹ thuật của IETF]),
      ([RSA], [Rivest–Shamir–Adleman], [Hệ mật mã khóa công khai bất đối xứng RSA]),
      ([SHA-256], [Secure Hash Algorithm 256-bit], [Hàm băm an toàn tạo chuỗi băm 256-bit]),
      ([SPN], [Substitution–Permutation Network], [Mạng thay thế – hoán vị]),
      ([TCP], [Transmission Control Protocol], [Giao thức điều khiển truyền vận]),
      ([XOR], [Exclusive OR], [Phép toán cộng loại trừ theo từng bit]),
    ),
  ),
  caption: [Danh mục các từ viết tắt và thuật ngữ sử dụng trong báo cáo],
) <tbl-abbreviations>

#pagebreak()
