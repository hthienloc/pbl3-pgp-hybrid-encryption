#import "../components.typ": info-box

#info-box(title: "Tóm tắt")[
  Khi truyền dữ liệu qua mạng không tin cậy, mật mã đối xứng AES (Advanced Encryption Standard) đạt tốc độ xử lý cao với dữ liệu lớn nhưng gặp khó khăn trong việc phân phối khóa bí mật. Ngược lại, mật mã bất đối xứng RSA (Rivest–Shamir–Adleman) khắc phục được vấn đề trao đổi khóa bằng cặp khóa công khai và khóa bí mật, nhưng chi phí lũy thừa mô-đun lớn nên không phù hợp để mã hóa trực tiếp thông điệp dài.

  Báo cáo trình bày mô hình mã hóa lai (Hybrid Encryption) theo nguyên lý PGP/OpenPGP (RFC 4880, RFC 9580): dùng AES-128-GCM mã hóa dữ liệu kèm xác thực toàn vẹn GHASH, và dùng RSA số học (modulus 256-bit, sinh nguyên tố Miller–Rabin) để bảo vệ khóa phiên dùng một lần (Session Key). Hệ thống được triển khai qua Socket TCP giữa Client (Alice) và Server (Bob) với cơ chế đóng khung chống phân mảnh luồng byte, đi kèm ứng dụng mô phỏng tương tác NiceGUI. Kết quả chạy thử trên 3 kịch bản kiểm thử cho thấy hệ thống khôi phục đúng dữ liệu gốc và phát hiện, từ chối xử lý khi có hành vi sửa đổi bit trên đường truyền.
]

#v(0.8em)

*Từ khóa:* PGP, OpenPGP, RSA, AES-GCM, Mã hóa lai (Hybrid Encryption), Socket TCP, Xác thực toàn vẹn, GHASH, Miller–Rabin, Euclid mở rộng.
