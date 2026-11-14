= Kết luận và hướng phát triển

Đề tài đã hoàn thành việc nghiên cứu và mô phỏng cơ chế mã hóa lai kết hợp RSA và AES-128-GCM theo mô hình OpenPGP. Về thuật toán, nhóm nắm vững cấu trúc mạng thay thế – hoán vị của AES, cơ chế xác thực GHASH trên trường $"GF"(2^(128))$ và tự cài đặt trọn vẹn RSA số học thuần bằng Python (Miller–Rabin, Euclid mở rộng).

Về triển khai thực tế, hệ thống đã giải quyết được bài toán phân mảnh luồng byte TCP bằng khung tiền tố độ dài và đối chiếu dấu vân tay khóa công khai qua SHA-256 trên mạng cục bộ. Kết quả kiểm thử ba kịch bản và giao diện mô phỏng xác nhận dữ liệu hợp lệ được khôi phục chính xác, còn các gói tin bị sửa bit hoặc giải mã sai khóa đều bị phát hiện và loại bỏ.

Trong thời gian tới, hệ thống có thể mở rộng theo ba hướng chính:
- *Bổ sung chữ ký số:* Kết hợp SHA-256 và khóa bí mật của bên gửi để bảo đảm thêm tính xác thực nguồn gốc và chống chối bỏ.
- *Nâng cấp chuẩn an toàn RSA:* Tăng độ dài khóa lên tối thiểu 2048 bit kèm cơ chế đệm ngẫu nhiên RSA-OAEP theo RFC 8017.
- *Đo đạc hiệu năng với dữ liệu lớn:* Thử nghiệm truyền tệp đa phương tiện dung lượng lớn qua Socket TCP để đánh giá định lượng tốc độ giữa mã hóa lai và mã hóa thuần bất đối xứng.
