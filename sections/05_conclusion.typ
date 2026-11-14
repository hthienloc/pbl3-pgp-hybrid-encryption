#import "../styles.typ": report-table

= Kết luận

== Đánh giá kết quả đạt được
Qua quá trình nghiên cứu lý thuyết, lập trình cài đặt và thực nghiệm kiểm thử, nhóm đã hoàn thành toàn diện các mục tiêu đề ra của đề tài môn học PBL3:
- *Về mặt học thuật:* Nhóm đã nắm vững bản chất toán học của hệ mật mã bất đối xứng RSA và hệ mật mã đối xứng xác thực AES-GCM; chứng minh được tính đúng đắn số học của quá trình giải mã dựa trên Định lý Euler (kèm Định lý Số dư Trung Hoa cho trường hợp tổng quát) và nguyên lý khuếch tán kiểm thực của hàm băm GHASH trên trường Galois $"GF"(2^(128))$.
- *Về mặt kỹ thuật:* Tự cài đặt thành công thuật toán RSA thuần Python (Miller–Rabin, Euclid mở rộng) không phụ thuộc thư viện đen; tích hợp luồng mã hóa lai PGP hoàn chỉnh giải quyết sự đánh đổi giữa hiệu năng và phân phối khóa; xử lý thành công giao thức đóng khung độ dài (Length-Prefixed Framing) chống phân mảnh byte stream trên kết nối mạng TCP Socket thực tế giữa 2 máy tính LAN.
- *Về mặt ứng dụng:* Xây dựng thành công ứng dụng mô phỏng trực quan tương tác hai chế độ trên nền web NiceGUI, hỗ trợ chạy tự động tuần tự và giả lập tấn công sửa bit thời gian thực, phục vụ hiệu quả cho việc kiểm chứng và trình diễn cơ chế mã hóa lai.

== Hạn chế và hướng phát triển tiếp theo
Mặc dù đã hoàn thành tốt các yêu cầu trọng tâm của học phần, đề tài vẫn còn một số điểm giới hạn cần được nghiên cứu và mở rộng trong tương lai. Kế hoạch và lộ trình phát triển chi tiết được tóm tắt trong @tbl-roadmap.

#figure(
  report-table(
    columns: (0.8fr, 1.7fr, 2.2fr),
    headers: ("Giai đoạn", "Mục tiêu & Hạng mục kỹ thuật", "Kết quả dự kiến đạt được"),
    rows: (
      ([Giai đoạn 1], [Tích hợp tính năng Chữ ký số điện tử (Digital Signature)], [Kết hợp thuật toán RSA với hàm băm SHA-256 để ký bản rõ tại Alice và kiểm chứng tại Bob, đảm bảo tính xác thực người gửi và tính chống chối bỏ.]),
      ([Giai đoạn 2], [Nâng cấp bảo mật RSA theo chuẩn RFC 8017 @rfc8017], [Nâng độ dài khóa lên 2048-bit và áp dụng cơ chế đệm an toàn ngẫu nhiên RSA-OAEP nhằm loại bỏ hoàn toàn các điểm yếu của Textbook RSA trước tấn công Coppersmith @coppersmith1997.]),
      ([Giai đoạn 3], [Mở rộng kiểm thử tệp tin thực tế dung lượng lớn], [Thực nghiệm mã hóa và truyền nhận các tệp tin đa phương tiện thực tế: tài liệu PDF, hình ảnh chất lượng cao và tệp nén nhị phân dung lượng từ vài chục MB đến hàng GB.]),
      ([Giai đoạn 4], [Đo đạc Benchmark và phân tích định lượng hiệu năng], [Xây dựng biểu đồ so sánh chi tiết thời gian thực thi, mức tiêu thụ CPU/RAM giữa phương pháp mã hóa thuần RSA so với giải pháp Mã hóa lai Hybrid Encryption.]),
    ),
  ),
  caption: [Kế hoạch hoàn thiện và mở rộng đề tài.],
) <tbl-roadmap>
