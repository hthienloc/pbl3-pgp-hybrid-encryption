= Câu hỏi thảo luận và phản biện (Q&A)

Để chuẩn bị tốt nhất cho buổi bảo vệ tiến độ trước giảng viên hướng dẫn, toàn thể thành viên trong nhóm đã tổng hợp và chuẩn bị kỹ các câu hỏi phản biện cốt lõi:

+ *RSA và AES khác nhau cơ bản ở điểm nào?*
  - _AES:_ Hệ mật mã đối xứng, người gửi và người nhận dùng chung một khóa bí mật, thuật toán chủ yếu dựa trên các phép thay thế và hoán vị trên ma trận byte (mạng SPN), tốc độ xử lý phần cứng cực kỳ nhanh.
  - _RSA:_ Hệ mật mã bất đối xứng, gồm cặp Public Key và Private Key, hoạt động dựa trên lý thuyết số học modulo và độ khó phân tích số nguyên lớn, chi phí tính toán lớn hơn hàng ngàn lần so với AES.

+ *Khóa công khai dùng để mã hóa khóa phiên thuộc về ai?*
  - Khóa công khai đó thuộc về *người nhận (Bob)*. Bất kỳ ai muốn gửi tin nhắn an toàn cho Bob đều dùng khóa công khai của Bob để mã hóa khóa phiên. Chỉ Bob với Private Key duy nhất mới giải mã được.

+ *Khóa phiên (Session Key) là gì và được tạo ra ở đâu?*
  - Khóa phiên là một khóa đối xứng ngẫu nhiên (thường có độ dài 128 hoặc 256 bit), được sinh ra ngẫu nhiên tại *phía người gửi (Alice)* trước khi thực hiện mã hóa thông điệp, chỉ dùng một lần duy nhất cho một phiên truyền thông.

+ *Cơ chế nào phát hiện bản mã bị kẻ tấn công sửa đổi?*
  - Khi sử dụng chế độ mã hóa xác thực *AES-GCM*, thuật toán tự động sinh ra giá trị *Authentication Tag*. Nếu bất kỳ bit nào của bản mã bị thay đổi trên đường truyền, giá trị tag tính toán lại ở phía nhận sẽ không khớp, Bob sẽ lập tức bác bỏ gói tin.

+ *Vì sao mã RSA tự viết với $p = 61, q = 53$ không thể ứng dụng trong bảo mật thực tế?*
  - Vì $n = 3233$ quá nhỏ, bất kỳ máy tính nào cũng có thể phân tích thành $61 times 53$ trong thời gian tính bằng microsecond, từ đó kẻ tấn công dễ dàng tính ra $phi(n) = 3120$ và tìm được khóa bí mật $d$. Trong thực tế, $p, q$ phải có độ dài tối thiểu 1024-bit hoặc 2048-bit trở lên.

+ *Cần bổ sung những gì để đề tài trở thành một hệ thống PGP/OpenPGP hoàn chỉnh?*
  - Bổ sung cơ chế đệm an toàn *OAEP* cho RSA;
  - Thêm chức năng nén dữ liệu (ZIP hoặc ZLIB) trước khi mã hóa;
  - Thêm chữ ký số (Digital Signature) để xác thực danh tính người gửi;
  - Quản lý khóa và định dạng gói tin theo chuẩn *RFC 4880* / *RFC 9580*.
