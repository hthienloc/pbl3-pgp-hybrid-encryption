#import "../styles.typ": report-table

= Kết luận

== Đánh giá kết quả đạt được
Qua quá trình thực hiện đồ án, nhóm đã nắm được cơ sở toán học của RSA và AES-GCM, đồng thời chứng minh được tính đúng đắn của phép giải mã RSA thông qua Định lý Euler (kèm CRT) cũng như cơ chế kiểm tra toàn vẹn của GHASH trên trường $"GF"(2^(128))$.

Về mặt triển khai, nhóm đã tự cài đặt thuật toán RSA thuần Python (gồm Miller-Rabin và Euclid mở rộng), kết hợp với AES-GCM thành luồng mã hóa lai PGP hoàn chỉnh và xử lý được vấn đề phân mảnh byte stream trên TCP Socket bằng cơ chế đóng khung độ dài (Length-Prefixed Framing) giữa 2 máy LAN. Bên cạnh đó, ứng dụng Web Simulator bằng NiceGUI với hai chế độ chạy tuần tự và giả lập tấn công sửa bit giúp trực quan hóa dữ liệu ở từng khâu và kiểm chứng hoạt động của hệ thống.

== Hạn chế và hướng phát triển tiếp theo
Các hạn chế hiện tại và lộ trình mở rộng được tóm tắt trong @tbl-roadmap.

#figure(
  report-table(
    columns: (0.8fr, 1.7fr, 2.2fr),
    headers: ("Giai đoạn", "Mục tiêu & Hạng mục kỹ thuật", "Kết quả dự kiến đạt được"),
    rows: (
      ([Giai đoạn 1], [Tích hợp Chữ ký số điện tử (Digital Signature)], [Kết hợp RSA với SHA-256 để ký bản rõ tại Alice và kiểm chứng tại Bob, bảo đảm xác thực người gửi và chống chối bỏ.]),
      ([Giai đoạn 2], [Nâng cấp bảo mật RSA theo chuẩn RFC 8017 @rfc8017], [Nâng khóa lên 2048-bit và áp dụng đệm RSA-OAEP nhằm khắc phục điểm yếu của Textbook RSA trước tấn công Coppersmith @coppersmith1997.]),
      ([Giai đoạn 3], [Mở rộng kiểm thử tệp tin dung lượng lớn], [Thử nghiệm mã hóa và truyền nhận tệp PDF, hình ảnh, tệp nhị phân dung lượng từ vài chục MB đến hàng GB.]),
      ([Giai đoạn 4], [Đo đạc Benchmark hiệu năng], [So sánh thời gian thực thi và mức tiêu thụ CPU/RAM giữa mã hóa thuần RSA với mã hóa lai.]),
    ),
  ),
  caption: [Kế hoạch hoàn thiện và mở rộng đề tài.],
) <tbl-roadmap>
