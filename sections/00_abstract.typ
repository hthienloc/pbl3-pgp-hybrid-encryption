#import "../components.typ": info-box
#import "../theme.typ": color-primary, color-text-muted

#align(center)[
  #set par(justify: false, leading: 0.5em)
  #text(size: 20pt, weight: "bold", fill: color-primary)[
    NGHIÊN CỨU VÀ MÔ PHỎNG CƠ CHẾ MÃ HÓA LAI (HYBRID ENCRYPTION) KẾT HỢP RSA VÀ AES-GCM THEO CHUẨN PGP/OPENPGP
  ]
  #v(0.6em)
  #text(size: 13pt, weight: "bold")[
    #box[Vũ Duy Dương (106230007)], #box[Huỳnh Thiện Lộc (106230052)], #box[Phan Vĩnh Sơn (106230059)]
  ] \
  #text(size: 12pt, style: "italic", fill: color-text-muted)[
    duong22012005\@gmail.com, locht.bk\@gmail.com, sonpv.bk\@gmail.com
  ] \
  #text(size: 12pt)[
    Khoa Điện tử và Trí tuệ Nhân tạo – Trường Đại học Bách Khoa, Đại học Đà Nẵng
  ]
]

#v(0.8em)

#info-box(title: "Tóm tắt")[
  #set text(size: 13pt)
  Trong bối cảnh truyền thông mạng mở, việc bảo đảm đồng thời tính bí mật, tính toàn vẹn và tính xác thực dữ liệu đặt ra nhiều yêu cầu kỹ thuật. Mật mã đối xứng AES xử lý nhanh các khối dữ liệu lớn nhưng gặp khó khăn khi phân phối khóa bí mật qua kênh không an toàn. Ngược lại, hệ mật bất đối xứng RSA hỗ trợ trao đổi khóa qua cặp khóa công khai và bí mật nhưng có chi phí lũy thừa mô-đun lớn, không phù hợp để mã hóa trực tiếp thông điệp dài.

  Báo cáo trình bày việc nghiên cứu và cài đặt kiến trúc Mã hóa lai (Hybrid Encryption) theo chuẩn PGP/OpenPGP (RFC 4880, RFC 9580). Hệ thống dùng AES-128-GCM để mã hóa dữ liệu và kiểm tra toàn vẹn bằng hàm băm GHASH, kết hợp RSA số học (modulus 512-bit, kiểm tra nguyên tố Miller–Rabin) để bảo vệ khóa phiên dùng một lần (Session Key). Nhóm đã xây dựng mô hình truyền thông Socket TCP giữa Client (Alice) và Server (Bob) có đóng khung chống phân mảnh luồng byte, cùng ứng dụng mô phỏng tương tác trên NiceGUI. Kết quả qua 3 kịch bản kiểm thử cho thấy hệ thống khôi phục chính xác dữ liệu gốc và phát hiện, từ chối các gói tin bị sửa bit trên đường truyền.
]

#v(0.5em)

#text(size: 13pt)[
  *Từ khóa:* PGP, OpenPGP, RSA, AES-GCM, Mã hóa lai (Hybrid Encryption), Socket TCP, Xác thực toàn vẹn, GHASH, Miller–Rabin, Euclid mở rộng.
]
