#import "../figures.typ": fig-hybrid-overview
#import "../styles.typ": report-table

= Giới thiệu

== Bối cảnh kỹ thuật
Theo tài liệu an toàn mạng @stallings2017, một hệ thống truyền thông tin cậy cần bốn tính chất: tính bí mật (Confidentiality) nhằm ngăn bên không có thẩm quyền đọc nội dung; tính toàn vẹn (Integrity) để bảo đảm dữ liệu không bị sửa đổi, chèn hoặc xóa trên đường truyền; tính xác thực (Authentication) giúp xác minh danh tính bên gửi; và tính chống chối bỏ (Non-repudiation) để bên gửi không thể phủ nhận thông điệp đã tạo.

Hai hướng mật mã chính đáp ứng các yêu cầu này là mật mã đối xứng và bất đối xứng. AES (Advanced Encryption Standard) @nist_fips197 cho tốc độ mã hóa/giải mã cao nhờ cấu trúc mạng hoán vị - thay thế (SPN) tối ưu phần cứng, nhưng khó khăn khi phải phân phối khóa bí mật qua mạng công khai. Ngược lại, RSA (Rivest, Shamir, Adleman, 1978) @rivest1978 xử lý được vấn đề trao đổi khóa bằng cặp khóa công khai và bí mật, nhưng phép lũy thừa mô-đun trên số nguyên lớn khiến RSA chậm hơn AES từ 100 đến 1000 lần, không phù hợp để mã hóa trực tiếp thông điệp dài.

Chuẩn PGP và OpenPGP (RFC 4880 @rfc4880, RFC 9580 @rfc9580) kết hợp hai phương pháp này theo mô hình mã hóa lai (Hybrid Encryption): dùng AES mã hóa bản rõ bằng khóa phiên dùng một lần (Session Key), sau đó dùng RSA mã hóa khóa phiên đó bằng khóa công khai của người nhận. Quy trình giữa Alice (gửi) và Bob (nhận) được minh họa trong @fig-hybrid-overview: bản rõ $M$ được mã hóa đối xứng bằng khóa phiên $K$ thành $C_"data"$ (kèm Nonce và Authentication Tag), khóa $K$ được mã hóa bất đối xứng bằng khóa công khai $(e_B, n)$ thành $C_"key"$; phía Bob dùng khóa bí mật $(d_B, n)$ giải mã lấy lại $K$ để khôi phục bản rõ $M' = M$.

#v(0.3em)
#align(center)[
  #fig-hybrid-overview <fig-hybrid-overview>
]
#v(0.3em)

== Mục tiêu đề tài
Đề tài PBL3: Mạng máy tính (Khoa Điện tử và Trí tuệ Nhân tạo, Trường Đại học Bách Khoa - ĐHĐN) tập trung vào các mục tiêu cụ thể sau:
+ Tìm hiểu cơ sở số học của RSA (thuật toán Euclid mở rộng, định lý Euler, kiểm tra nguyên tố Miller-Rabin) và cơ chế mã hóa xác thực AES-GCM (Galois/Counter Mode).
+ Tự cài đặt thuật toán RSA bằng Python thuần, không phụ thuộc thư viện đóng gói sẵn, nhằm minh họa rõ quá trình sinh khóa và lũy thừa mô-đun.
+ Tích hợp module RSA với AES-GCM theo luồng mã hóa lai PGP, từ bước bảo vệ khóa phiên, đóng gói khung tin đến giải mã và kiểm tra toàn vẹn.
+ Xây dựng hệ thống truyền thông Client-Server qua TCP Socket có đóng khung tiền tố độ dài (Length-Prefixed Framing) để tránh phân mảnh luồng byte khi truyền giữa 2 máy trong mạng LAN.
+ Phát triển giao diện web NiceGUI gồm hai chế độ (mô phỏng luồng truyền thông tích hợp và chi tiết từng khối thuật toán), kèm các kịch bản kiểm thử tấn công sửa bit.

== Phạm vi đề tài
Trong khuôn khổ đồ án, nhóm cài đặt Textbook RSA dạng số học (modulus 256-bit ở phần minh họa thuật toán và 512-bit khi truyền qua Socket, đủ chứa khóa AES 128-bit); sử dụng thư viện chuẩn cho AES-GCM với Nonce 12 bytes và Tag 16 bytes; đóng gói dữ liệu dạng JSON Envelope truyền qua TCP Socket cổng 5000; đối chiếu SHA-256 fingerprint của khóa công khai và xây dựng giao diện mô phỏng bằng NiceGUI. Hệ thống đáp ứng được tính bí mật, tính toàn vẹn và hỗ trợ xác thực thủ công khóa công khai thông qua SHA-256 fingerprint.

Một số phần nâng cao chưa được triển khai trong phiên bản này gồm: kỹ thuật đệm RSA-OAEP theo RFC 8017 @rfc8017 (để chống tấn công Coppersmith @coppersmith1997), chữ ký số (Digital Signature) cho tính xác thực người gửi và chống chối bỏ, cũng như mô hình Web of Trust hay cấu trúc gói tin nhị phân đa tầng đầy đủ theo RFC 4880 @rfc4880.

== Phân công nhiệm vụ và đóng góp của các thành viên
Phân công công việc của 3 thành viên được tổng hợp trong @tbl-task-allocation.

#figure(
  report-table(
    columns: (1.2fr, 3.0fr, 0.9fr),
    headers: ("Tên thành viên", "Nhiệm vụ", "Phần trăm đóng góp"),
    rows: (
      (
        [Vũ Duy Dương \ (`106230007`)],
        [Trưởng nhóm; thiết kế kiến trúc Hybrid Encryption; cài đặt RSA thuần (Miller–Rabin, Euclid mở rộng); phát triển Web Simulator NiceGUI; tổng hợp báo cáo.],
        align(center)[34%],
      ),
      (
        [Huỳnh Thiện Lộc \ (`106230052`)],
        [Nghiên cứu AES-GCM (NIST SP 800-38D) và hàm băm GHASH trên $"GF"(2^(128))$; thiết kế và thực thi 3 kịch bản kiểm thử bảo mật và toàn vẹn.],
        align(center)[33%],
      ),
      (
        [Phan Vĩnh Sơn \ (`106230059`)],
        [Nghiên cứu TCP Socket; lập trình Client–Server (Alice/Bob) qua mạng LAN; cài đặt đóng khung tiền tố độ dài chống phân mảnh và đối chiếu SHA-256 fingerprint.],
        align(center)[33%],
      ),
    ),
  ),
  caption: [Phân công nhiệm vụ của nhóm],
) <tbl-task-allocation>
