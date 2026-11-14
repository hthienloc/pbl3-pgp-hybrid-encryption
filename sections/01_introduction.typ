#import "../figures.typ": fig-hybrid-overview
#import "../styles.typ": report-table

= Giới thiệu

== Bối cảnh kỹ thuật
Trong kỷ nguyên số hóa và mạng thông tin toàn cầu, việc truyền tải dữ liệu giữa các thực thể phân tán đòi hỏi các giải pháp an toàn thông tin mạnh mẽ. Theo các lý thuyết an toàn mạng chuẩn mực @stallings2017, một hệ thống truyền thông tin cậy hướng tới bốn yêu cầu cốt lõi: (1) *Tính bí mật (Confidentiality)* – ngăn chặn các bên không có thẩm quyền đọc hiểu nội dung; (2) *Tính toàn vẹn (Integrity)* – bảo đảm dữ liệu không bị sửa đổi, chèn ép hoặc xóa bớt trên đường truyền; (3) *Tính xác thực (Authentication)* – chứng minh danh tính thực sự của bên gửi tin; và (4) *Tính chống chối bỏ (Non-repudiation)* – bên gửi không thể phủ nhận thông điệp do chính mình khởi tạo.

Để đáp ứng các yêu cầu trên, các kỹ thuật mật mã học đã phát triển hai trường phái chính: mật mã khóa đối xứng và mật mã khóa công khai bất đối xứng. Tiêu chuẩn mã hóa nâng cao AES (Advanced Encryption Standard) @nist_fips197 là đại diện tiêu biểu của mật mã đối xứng, cho phép mã hóa và giải mã với tốc độ cực cao nhờ cấu trúc mạng hoán vị – thay thế (SPN) tối ưu hóa trên phần cứng. Tuy nhiên, điểm yếu cố hữu của AES là bài toán thỏa thuận và phân phối khóa bí mật qua môi trường mạng công khai. Mặt khác, hệ mật mã bất đối xứng RSA do Ron Rivest, Adi Shamir và Leonard Adleman công bố năm 1978 @rivest1978 đã giải quyết bài toán trao đổi khóa nhờ cặp khóa công khai (Public Key) dùng để mã hóa và khóa bí mật (Private Key) dùng để giải mã. Thế nhưng, chi phí tính toán lũy thừa mô-đun trên các số nguyên lớn khiến tốc độ của RSA chậm hơn AES từ 100 đến 1000 lần, biến việc mã hóa trực tiếp thông điệp dài bằng RSA thành giải pháp bất khả thi về mặt hiệu năng.

Chuẩn PGP (Pretty Good Privacy) và chuẩn mở OpenPGP (RFC 4880 @rfc4880, RFC 9580 @rfc9580) giải quyết sự đánh đổi này bằng kiến trúc *Mã hóa lai (Hybrid Encryption)*: dùng AES để mã hóa dữ liệu bản rõ bằng một khóa phiên dùng một lần (Session Key), sau đó dùng RSA để bảo vệ khóa phiên đó với khóa công khai của người nhận. Toàn bộ chu trình xử lý dữ liệu và khóa giữa hai thực thể Alice (phía gửi) và Bob (phía nhận) được minh họa trong @fig-hybrid-overview: bản rõ $M$ được mã hóa đối xứng bằng khóa phiên $K$ thành $C_"data"$ (kèm Nonce và Authentication Tag), khóa phiên $K$ được mã hóa bất đối xứng bằng Public Key $(e_B, n)$ thành $C_"key"$; tại phía Bob, Private Key $(d_B, n)$ giải mã lấy lại $K$ để khôi phục trọn vẹn bản rõ $M' = M$.

#v(0.3em)
#align(center)[
  #fig-hybrid-overview <fig-hybrid-overview>
]
#v(0.3em)

== Mục tiêu đề tài
Trong khuôn khổ học phần PBL3: Mạng máy tính tại Khoa Điện tử và Trí tuệ Nhân tạo, Trường Đại học Bách Khoa – Đại học Đà Nẵng, đề tài tập trung vào các mục tiêu học thuật và thực nghiệm sau:
+ *Làm chủ cơ sở lý thuyết số học và thuật toán mật mã:* Nắm vững nguyên lý số học của hệ mật RSA (thuật toán Euclid mở rộng, định lý số học Euler, kiểm tra nguyên tố xác suất Miller–Rabin) và cơ chế mã hóa có xác thực AES-GCM (Galois/Counter Mode).
+ *Tự lập trình giải thuật số học thuần:* Cài đặt thuật toán RSA hoàn toàn bằng Python không phụ thuộc vào thư viện đen (black-box), qua đó trực quan hóa tường minh các bước biến đổi lũy thừa mô-đun và sinh khóa.
+ *Xây dựng luồng tích hợp lai PGP hoàn chỉnh:* Ghép nối module RSA với AES-GCM để tạo nên đường ống xử lý dữ liệu khép kín từ mã hóa khóa phiên, đóng gói khung tin đến giải mã và kiểm thực tại bên nhận.
+ *Hiện thực hóa truyền thông mạng thực tế:* Xây dựng hệ thống Client–Server hoàn chỉnh qua giao thức TCP Socket có đóng khung độ dài (Length-Prefixed Framing) chống phân mảnh luồng dữ liệu byte giữa 2 máy tính trong mạng LAN.
+ *Phát triển giao diện trực quan và bộ kịch bản kiểm thử:* Xây dựng ứng dụng web mô phỏng trực quan bằng NiceGUI hỗ trợ hai chế độ (Tích hợp luồng truyền thông và Chi tiết từng khối thuật toán), đồng thời thử nghiệm các kịch bản tấn công can thiệp sửa đổi bit để kiểm chứng tính toàn vẹn của hệ thống.

== Phạm vi đề tài
- *Phạm vi thực hiện:* Cài đặt Textbook RSA dạng số học (modulus 256-bit ở demo thuật toán và 512-bit ở truyền thông Socket, đủ chứa khóa AES 128-bit); kết hợp thư viện chuẩn AES-GCM với vector khởi tạo Nonce 12 bytes và mã xác thực Tag 16 bytes; đóng gói JSON Envelope và truyền nhận qua TCP Socket cổng 5000; đối chiếu mã băm SHA-256 fingerprint của Public Key; phát triển giao diện Web Simulator trực quan. Trong phạm vi hiện tại, hệ thống bảo đảm hai thuộc tính cốt lõi là *Tính bí mật* và *Tính toàn vẹn* của thông điệp (cùng xác thực thủ công khóa công khai qua SHA-256 fingerprint).
- *Phạm vi chưa thực hiện:* Chưa triển khai cơ chế đệm an toàn ngẫu nhiên tối ưu RSA-OAEP theo RFC 8017 @rfc8017 (nhằm chống tấn công Coppersmith @coppersmith1997); chưa tích hợp Chữ ký số (Digital Signature) để bảo đảm tính xác thực người gửi và chống chối bỏ; chưa xây dựng mạng lưới tín nhiệm Web of Trust đầy đủ và chưa hỗ trợ cấu trúc gói tin nhị phân đa tầng phức tạp theo chuẩn RFC 4880 @rfc4880.

== Phân công nhiệm vụ và đóng góp của các thành viên
Để bảo đảm tiến độ và chất lượng chuyên môn của đề tài, nhóm sinh viên gồm 3 thành viên đã phân chia rõ ràng các mảng nghiên cứu lý thuyết, phát triển mã nguồn thuật toán, lập trình socket mạng và kiểm thử giao diện. Chi tiết công việc và mức độ hoàn thành của từng thành viên được tổng hợp đầy đủ trong @tbl-task-allocation.

#figure(
  report-table(
    columns: (1.2fr, 3.1fr, 0.8fr),
    headers: ("Tên thành viên", "Nhiệm vụ phụ trách", "Hoàn thành"),
    rows: (
      (
        [Vũ Duy Dương \ (`106230007`)],
        [Trưởng nhóm; thiết kế kiến trúc hệ thống Hybrid Encryption; tự lập trình thuật toán RSA số học thuần (sinh nguyên tố Miller–Rabin, Euclid mở rộng); phát triển ứng dụng Web Simulator tương tác thời gian thực bằng NiceGUI; tổng hợp và viết báo cáo.],
        align(center)[100%],
      ),
      (
        [Huỳnh Thiện Lộc \ (`106230052`)],
        [Nghiên cứu cơ chế mã hóa đối xứng xác thực AES-GCM (NIST SP 800-38D); phân tích cơ sở toán học của hàm băm GHASH trên trường Galois $"GF"(2^(128))$; thiết kế và thực thi 3 kịch bản kiểm thử bảo mật và bắt lỗi toàn vẹn.],
        align(center)[100%],
      ),
      (
        [Phan Vĩnh Sơn \ (`106230059`)],
        [Nghiên cứu giao thức truyền thông mạng TCP Socket; lập trình bộ máy Client–Server (Alice/Bob) qua mạng LAN; xây dựng cơ chế đóng khung tiền tố độ dài chống phân mảnh byte stream; cài đặt thuật toán băm đối chiếu SHA-256 fingerprint.],
        align(center)[100%],
      ),
    ),
  ),
  caption: [Phân công nhiệm vụ của nhóm.],
) <tbl-task-allocation>
