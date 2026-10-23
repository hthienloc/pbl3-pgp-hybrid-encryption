= Tích hợp RSA và AES trong Hybrid Encryption

Trong mô hình mã hóa lai hoàn chỉnh, RSA tuyệt đối không tham gia trực tiếp vào việc mã hóa khối dữ liệu thông điệp dài mà đóng vai trò là "két sắt" bảo vệ khóa đối xứng (Session Key). AES đảm nhận toàn bộ việc mã hóa dữ liệu tốc độ cao.

#align(center)[
  #table(
    columns: (1fr, 1fr),
    fill: (x, y) => if y == 0 { rgb("#e0e7ff") } else { none },
    stroke: 0.5pt + rgb("#cbd5e1"),
    inset: 9pt,
    [*Phía Alice (Mã hóa)*], [*Phía Bob (Giải mã)*],
    [
      - Sinh khóa phiên $K_("session")$ ngẫu nhiên (128-bit / 256-bit).
      - Dùng AES mã hóa thông điệp bằng $K_("session")$.
      - Dùng Public Key RSA của Bob để mã hóa $K_("session")$.
      - Đóng gói và gửi các thành phần cần thiết (bản mã AES, khóa phiên mã hóa, IV/Nonce, Tag).
    ],
    [
      - Tiếp nhận toàn bộ gói dữ liệu đã mã hóa từ Alice.
      - Dùng Private Key RSA của Bob để khôi phục $K_("session")$.
      - Dùng $K_("session")$ giải mã dữ liệu thông điệp bằng AES.
      - Kiểm tra xác thực/toàn vẹn dữ liệu nếu chế độ mã hóa có hỗ trợ (Authentication Tag).
    ]
  )
]

#import "../components.typ": info-box
#info-box(title: "Gợi ý trình bày & Lưu ý kỹ thuật")[
  - *Code minh chứng:* Mở trực tiếp tệp mã hóa lai thực tế của nhóm để chỉ rõ dòng sinh khóa phiên, vị trí AES dùng khóa phiên để mã hóa thông điệp, hàm RSA đóng gói khóa phiên, và chiều giải mã đối xứng của Bob.
  - *Chế độ mã hóa AES:* Nếu chương trình sử dụng *AES-GCM*, cần giải thích rõ vai trò của *Nonce* (tránh trùng lặp khối mã) và *Tag* (kiểm tra tính toàn vẹn và xác thực thông điệp).
  - *Tính minh bạch:* Cần nêu rõ ranh giới phần code: nhóm tự triển khai giải thuật RSA toán học để tìm hiểu nguyên lý, còn AES và cơ chế đệm an toàn được tích hợp từ thư viện chuẩn (Cryptodome/Cryptography) theo đúng tiêu chuẩn công nghiệp.
]
