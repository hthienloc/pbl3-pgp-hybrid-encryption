#import "../styles.typ": report-table

= Danh mục thuật ngữ và viết tắt

Để văn phong báo cáo cô đọng, trong toàn bộ tài liệu các thuật ngữ mật mã học và mạng máy tính được phân loại và chuẩn hóa theo danh mục dưới đây:

#align(center)[
  #report-table(
    columns: (1fr, 1.2fr, 1.4fr, 2.2fr),
    headers: ("Ký hiệu / Thuật ngữ", "Phân loại", "Tên tiếng Anh", "Ý nghĩa chuyên môn"),
    rows: (
      ([*PGP*], [Tiêu chuẩn], [Pretty Good Privacy], [Giao thức mã hóa bảo vệ quyền riêng tư qua kênh mạng mở.]),
      ([*RSA*], [Bất đối xứng], [Rivest – Shamir – Adleman], [Hệ mật mã khóa công khai dựa trên độ khó bài toán phân tích số nguyên lớn.]),
      ([*AES*], [Đối xứng], [Advanced Encryption Standard], [Chuẩn mã hóa đối xứng khối tốc độ cao, dùng ma trận thay thế hoán vị SPN.]),
      ([*Hybrid Encryption*], [Kiến trúc], [Mã hóa lai], [Mô hình kết hợp AES (mã hóa dữ liệu) và RSA (bảo vệ khóa phiên).]),
      ([*Session Key*], [Khóa], [Khóa phiên], [Khóa đối xứng ngẫu nhiên chỉ có giá trị cho một phiên truyền thông duy nhất.]),
      ([*Public / Private Key*], [Khóa], [Khóa công khai / Bí mật], [Cặp khóa bất đối xứng: chia sẻ công khai để mã hóa / giữ bí mật để giải mã.]),
      ([*PKESK*], [Gói tin PGP], [Public-Key Encrypted Session Key], [Gói tin chứa Session Key đã được mã hóa bằng khóa công khai người nhận.]),
      ([*SEIPD*], [Gói tin PGP], [Symmetrically Encrypted Integrity Protected Data], [Gói tin chứa dữ liệu đã được mã hóa đối xứng kèm cơ chế kiểm tra toàn vẹn.]),
      ([*AES-GCM*], [Chế độ AES], [Galois/Counter Mode], [Chế độ mã hóa xác thực (AEAD) cung cấp đồng thời tính bí mật và toàn vẹn.]),
      ([*IV / Nonce*], [Tham số AES], [Initialization Vector / Number Used Once], [Vector khởi tạo ngẫu nhiên (12 bytes) giúp triệt tiêu hiện tượng trùng lặp bản mã khi mã hóa cùng dữ liệu.]),
      ([*Authentication Tag*], [Toàn vẹn], [Message Authentication Code (MAC)], [Mã kiểm thực (16 bytes) giúp phía nhận phát hiện mọi hành vi can thiệp hay sửa đổi bản mã trên mạng.]),
      ([*OAEP*], [Cơ chế đệm], [Optimal Asymmetric Encryption Padding], [Cơ chế đệm ngẫu nhiên an toàn chống tấn công chọn bản mã cho RSA.]),
      ([*Miller–Rabin*], [Số học], [Miller–Rabin Primality Test], [Thuật toán kiểm tra số nguyên tố xác suất, được dùng để sinh $p, q$ động trong quá trình tạo khóa RSA.]),
      ([*TCP*], [Giao thức mạng], [Transmission Control Protocol], [Giao thức truyền luồng tin cậy, có thứ tự, bảo đảm dữ liệu đến đủ và đúng thứ tự.]),
      ([*Socket*], [Lập trình mạng], [Berkeley Sockets API], [Điểm cuối giao tiếp giữa hai tiến trình qua mạng, định danh bởi cặp địa chỉ IP và cổng.]),
      ([*Length-prefixed Framing*], [Kỹ thuật], [Đóng khung tiền tố độ dài], [Kỹ thuật ghi 4 byte độ dài gói trước dữ liệu để bộ nhận xác định đúng ranh giới thông điệp trên luồng TCP.]),
      ([*Fingerprint*], [Xác thực khóa], [SHA-256 Fingerprint], [Mã băm SHA-256 của Public Key, dùng đối chiếu ngoài kênh nhằm phát hiện khóa bị thay thế.]),
    )
  )
]
