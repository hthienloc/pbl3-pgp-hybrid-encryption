#import "../figures.typ": fig-hybrid-overview
#import "../styles.typ": report-table

= Giới thiệu

== Bối cảnh kỹ thuật
Trong kỷ nguyên số hóa và mạng thông tin toàn cầu, việc truyền tải dữ liệu giữa các thực thể phân tán đòi hỏi các giải pháp an toàn thông tin mạnh mẽ. Theo các lý thuyết an toàn mạng chuẩn mực @stallings2017, một hệ thống truyền thông tin cậy bắt buộc phải thỏa mãn đồng thời bốn yêu cầu cốt lõi: (1) *Tính bí mật (Confidentiality)* – ngăn chặn các bên không có thẩm quyền đọc hiểu nội dung; (2) *Tính toàn vẹn (Integrity)* – bảo đảm dữ liệu không bị sửa đổi, chèn ép hoặc xóa bớt trên đường truyền; (3) *Tính xác thực (Authentication)* – chứng minh danh tính thực sự của bên gửi tin; và (4) *Tính chống chối bỏ (Non-repudiation)* – bên gửi không thể phủ nhận thông điệp do chính mình khởi tạo.

Để đáp ứng các yêu cầu trên, các kỹ thuật mật mã học đã phát triển hai trường phái chính: mật mã khóa đối xứng và mật mã khóa công khai bất đối xứng. Tiêu chuẩn mã hóa nâng cao AES (Advanced Encryption Standard) @nist_fips197 là đại diện tiêu biểu của mật mã đối xứng, cho phép mã hóa và giải mã với tốc độ cực cao nhờ cấu trúc mạng hoán vị – thay thế (SPN) tối ưu hóa trên phần cứng. Tuy nhiên, điểm yếu cố hữu của AES là bài toán thỏa thuận và phân phối khóa bí mật: làm thế nào để hai bên chưa từng gặp nhau có thể chia sẻ chung một khóa bí mật qua một môi trường mạng công khai đầy rẫy kẻ nghe lén? Mặt khác, hệ mật mã bất đối xứng RSA do Ron Rivest, Adi Shamir và Leonard Adleman công bố năm 1978 @rivest1978 đã giải quyết trọn vẹn bài toán trao đổi khóa nhờ nguyên lý cặp khóa bất đối xứng: khóa công khai (Public Key) dùng để mã hóa và khóa bí mật (Private Key) dùng để giải mã. Thế nhưng, chi phí tính toán lũy thừa mô-đun trên các số nguyên lớn khiến tốc độ của RSA chậm hơn AES từ 100 đến 1000 lần, biến việc mã hóa trực tiếp các bức thư hay tệp tin dung lượng lớn bằng RSA thành một giải pháp bất khả thi về mặt hiệu năng.

Mô hình mã hóa và giải mã lai kinh điển kết hợp giữa RSA và AES theo chuẩn OpenPGP được nhóm nghiên cứu và trực quan hóa chi tiết trong Hình 1 @zhou2011. Hình 1 mô tả toàn bộ chu trình xử lý dữ liệu và khóa giữa hai thực thể truyền thông Alice (phía gửi) và Bob (phía nhận). Tại phía Alice, bản rõ gốc $M$ được mã hóa đối xứng bằng khóa phiên ngẫu nhiên $K$ theo chuẩn AES để tạo ra bản mã dữ liệu $C_"data"$. Khóa phiên $K$ được mã hóa bất đối xứng bằng Public Key $(e_B, n)$ của Bob qua thuật toán RSA để tạo ra bản mã khóa $C_"key"$. Cả hai bản mã được truyền an toàn qua kênh mạng công cộng. Tại phía Bob, Private Key $(d_B, n)$ được dùng để giải mã RSA khôi phục chính xác khóa phiên $K$, từ đó tiến hành giải mã AES để lấy lại trọn vẹn bản rõ ban đầu $M' = M$.

#v(0.3em)
#align(center)[
  #fig-hybrid-overview
]
#v(0.3em)

Nhận thấy ưu thế và khuyết điểm bù trừ lẫn nhau giữa hai trường phái, chuẩn PGP (Pretty Good Privacy) do Phil Zimmermann phát minh và sau này được IETF chuẩn hóa thành OpenPGP (RFC 4880 @rfc4880, RFC 9580 @rfc9580) đã kết hợp chúng trong mô hình *Mã hóa lai (Hybrid Encryption)*. Mô hình này sử dụng hệ mật đối xứng AES để mã hóa nhanh khối dữ liệu bản rõ bằng một khóa phiên tạm thời dùng một lần (Session Key), sau đó dùng RSA để mã hóa an toàn khóa phiên đó với khóa công khai của người nhận.

== Mục tiêu đề tài
Trong khuôn khổ học phần PBL3: Mạng máy tính tại Khoa Điện tử và Trí tuệ Nhân tạo, Trường Đại học Bách Khoa – Đại học Đà Nẵng, đề tài tập trung vào các mục tiêu học thuật và thực nghiệm sau:
+ *Làm chủ cơ sở lý thuyết số học và thuật toán mật mã:* Nắm vững nguyên lý số học của hệ mật RSA (thuật toán Euclid mở rộng, định lý số học Euler, kiểm tra nguyên tố xác suất Miller–Rabin) và cơ chế mã hóa có xác thực AES-GCM (Galois/Counter Mode).
+ *Tự lập trình giải thuật số học thuần:* Cài đặt thuật toán RSA hoàn toàn bằng Python không phụ thuộc vào thư viện đen (black-box), qua đó trực quan hóa tường minh các bước biến đổi lũy thừa mô-đun và sinh khóa.
+ *Xây dựng luồng tích hợp lai PGP hoàn chỉnh:* Ghép nối module RSA với AES-GCM để tạo nên đường ống xử lý dữ liệu khép kín từ mã hóa khóa phiên, đóng gói khung tin đến giải mã và kiểm thực tại bên nhận.
+ *Hiện thực hóa truyền thông mạng thực tế:* Xây dựng hệ thống Client–Server hoàn chỉnh qua giao thức TCP Socket có đóng khung độ dài (Length-Prefixed Framing) chống phân mảnh luồng dữ liệu byte giữa 2 máy tính trong mạng LAN.
+ *Phát triển giao diện trực quan và bộ kịch bản kiểm thử:* Xây dựng ứng dụng web mô phỏng trực quan bằng NiceGUI hỗ trợ hai chế độ (Tích hợp luồng truyền thông và Chi tiết từng khối thuật toán), đồng thời thử nghiệm các kịch bản tấn công can thiệp sửa đổi bit để kiểm chứng tính toàn vẹn của hệ thống.

== Phạm vi đề tài
- *Phạm vi thực hiện:* Cài đặt Textbook RSA dạng số học tự sinh khóa ngẫu nhiên 256-bit (đủ chứa khóa AES 128-bit); kết hợp thư viện chuẩn AES-GCM với vector khởi tạo Nonce 12 bytes và mã xác thực Tag 16 bytes; đóng gói JSON Envelope và truyền nhận qua TCP Socket cổng 5000; đối chiếu mã băm SHA-256 fingerprint của Public Key; phát triển giao diện Web Simulator trực quan.
- *Phạm vi chưa thực hiện:* Chưa triển khai cơ chế đệm an toàn ngẫu nhiên tối ưu RSA-OAEP theo RFC 8017 @rfc8017 (vốn bắt buộc cho các hệ thống thương mại nhằm chống tấn công Coppersmith @coppersmith1997); chưa xây dựng mạng lưới tín nhiệm Web of Trust đầy đủ và chưa hỗ trợ cấu trúc gói tin nhị phân đa tầng phức tạp theo chuẩn RFC 4880 @rfc4880.

== Phân công nhiệm vụ và đóng góp của các thành viên
Để bảo đảm tiến độ và chất lượng chuyên môn của đề tài, nhóm sinh viên gồm 3 thành viên đã phân chia rõ ràng các mảng nghiên cứu lý thuyết, phát triển mã nguồn thuật toán, lập trình socket mạng và kiểm thử giao diện. Chi tiết công việc và mức độ đóng góp của từng thành viên được tổng hợp đầy đủ trong Bảng 1.

#figure(
  report-table(
    columns: (1.2fr, 3.2fr, 0.7fr),
    headers: ("Tên thành viên", "Nhiệm vụ phụ trách", "Đóng góp"),
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
)
