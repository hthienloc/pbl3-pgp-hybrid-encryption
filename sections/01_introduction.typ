#import "../figures.typ": fig-hybrid-overview
#import "../styles.typ": report-table

= Giới thiệu

== Bối cảnh kỹ thuật
Theo lý thuyết an toàn mạng @stallings2017, một hệ thống truyền thông tin cậy cần bốn thuộc tính: (1) *Tính bí mật (Confidentiality)* – ngăn bên không có thẩm quyền đọc nội dung; (2) *Tính toàn vẹn (Integrity)* – bảo đảm dữ liệu không bị sửa đổi, chèn hoặc xóa trên đường truyền; (3) *Tính xác thực (Authentication)* – xác minh danh tính bên gửi; và (4) *Tính chống chối bỏ (Non-repudiation)* – bên gửi không thể phủ nhận thông điệp đã tạo.

Hai trường phái mật mã chính giải quyết các yêu cầu này là mật mã đối xứng và bất đối xứng. AES (Advanced Encryption Standard) @nist_fips197 cho tốc độ mã hóa/giải mã cao nhờ mạng hoán vị – thay thế (SPN) tối ưu phần cứng, nhưng gặp khó khăn trong việc phân phối khóa bí mật qua mạng công khai. Ngược lại, RSA (Rivest, Shamir, Adleman, 1978) @rivest1978 giải quyết bài toán trao đổi khóa bằng cặp khóa công khai / bí mật, nhưng phép lũy thừa mô-đun trên số nguyên lớn khiến RSA chậm hơn AES từ 100 đến 1000 lần, không phù hợp để mã hóa trực tiếp thông điệp dài.

Chuẩn PGP và OpenPGP (RFC 4880 @rfc4880, RFC 9580 @rfc9580) kết hợp hai phương pháp qua kiến trúc *Mã hóa lai (Hybrid Encryption)*: dùng AES mã hóa bản rõ bằng khóa phiên dùng một lần (Session Key), rồi dùng RSA mã hóa khóa phiên đó bằng khóa công khai người nhận. Quy trình giữa Alice (gửi) và Bob (nhận) được minh họa trong @fig-hybrid-overview: bản rõ $M$ được mã hóa đối xứng bằng khóa phiên $K$ thành $C_"data"$ (kèm Nonce và Authentication Tag), khóa $K$ được mã hóa bất đối xứng bằng Public Key $(e_B, n)$ thành $C_"key"$; phía Bob dùng Private Key $(d_B, n)$ giải mã lấy lại $K$ để khôi phục bản rõ $M' = M$.

#v(0.3em)
#align(center)[
  #fig-hybrid-overview <fig-hybrid-overview>
]
#v(0.3em)

== Mục tiêu đề tài
Đề tài PBL3: Mạng máy tính (Khoa Điện tử và Trí tuệ Nhân tạo, Trường Đại học Bách Khoa – ĐHĐN) hướng tới các mục tiêu sau:
+ *Cơ sở số học và mật mã:* Nắm vững lý thuyết RSA (Euclid mở rộng, định lý Euler, kiểm tra nguyên tố Miller–Rabin) và mã hóa xác thực AES-GCM (Galois/Counter Mode).
+ *Cài đặt RSA thuần Python:* Tự lập trình giải thuật RSA không dùng thư viện đen (black-box) để minh họa trực tiếp sinh khóa và lũy thừa mô-đun.
+ *Tích hợp luồng lai PGP:* Kết nối module RSA với AES-GCM từ khâu mã hóa khóa phiên, đóng gói khung tin đến giải mã và kiểm thực.
+ *Truyền thông Socket TCP:* Xây dựng hệ thống Client–Server qua TCP Socket có đóng khung độ dài (Length-Prefixed Framing) chống phân mảnh luồng byte giữa 2 máy mạng LAN.
+ *Mô phỏng và kiểm thử:* Phát triển giao diện web NiceGUI gồm hai chế độ (Tích hợp luồng truyền thông và Chi tiết từng khối thuật toán), kèm bộ kịch bản kiểm thử tấn công sửa bit.

== Phạm vi đề tài
- *Phạm vi thực hiện:* Cài đặt Textbook RSA dạng số học (modulus 256-bit ở demo thuật toán, 512-bit ở truyền thông Socket, đủ chứa khóa AES 128-bit); dùng thư viện chuẩn AES-GCM với Nonce 12 bytes và Tag 16 bytes; đóng gói JSON Envelope truyền qua TCP Socket cổng 5000; đối chiếu SHA-256 fingerprint của Public Key; xây dựng Web Simulator NiceGUI. Hệ thống bảo đảm *Tính bí mật*, *Tính toàn vẹn* và xác thực thủ công khóa công khai qua SHA-256 fingerprint.
- *Phạm vi chưa thực hiện:* Chưa triển khai đệm RSA-OAEP theo RFC 8017 @rfc8017 (chống tấn công Coppersmith @coppersmith1997); chưa tích hợp Chữ ký số (Digital Signature) cho tính xác thực người gửi và chống chối bỏ; chưa xây dựng Web of Trust và gói tin nhị phân đa tầng đầy đủ theo RFC 4880 @rfc4880.

== Phân công nhiệm vụ và đóng góp của các thành viên
Phân công công việc của 3 thành viên được tổng hợp trong @tbl-task-allocation.

#figure(
  report-table(
    columns: (1.2fr, 3.1fr, 0.8fr),
    headers: ("Tên thành viên", "Nhiệm vụ phụ trách", "Hoàn thành"),
    rows: (
      (
        [Vũ Duy Dương \ (`106230007`)],
        [Trưởng nhóm; thiết kế kiến trúc Hybrid Encryption; cài đặt RSA thuần (Miller–Rabin, Euclid mở rộng); phát triển Web Simulator NiceGUI; tổng hợp báo cáo.],
        align(center)[100%],
      ),
      (
        [Huỳnh Thiện Lộc \ (`106230052`)],
        [Nghiên cứu AES-GCM (NIST SP 800-38D) và hàm băm GHASH trên $"GF"(2^(128))$; thiết kế và thực thi 3 kịch bản kiểm thử bảo mật và toàn vẹn.],
        align(center)[100%],
      ),
      (
        [Phan Vĩnh Sơn \ (`106230059`)],
        [Nghiên cứu TCP Socket; lập trình Client–Server (Alice/Bob) qua mạng LAN; cài đặt đóng khung tiền tố độ dài chống phân mảnh và đối chiếu SHA-256 fingerprint.],
        align(center)[100%],
      ),
    ),
  ),
  caption: [Phân công nhiệm vụ của nhóm.],
) <tbl-task-allocation>
