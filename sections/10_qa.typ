#import "../components.typ": info-box

#let qa-card(q, a) = {
  rect(
    width: 100%,
    fill: rgb("#f8fafc"),
    stroke: 0.5pt + rgb("#cbd5e1"),
    radius: 4pt,
    inset: 10pt,
  )[
    #text(weight: "bold", fill: rgb("#1d4ed8"))[Hỏi: #q] \
    #v(0.3em)
    #text(fill: rgb("#1e293b"))[#a]
  ]
}

= Câu hỏi thảo luận và phản biện (Q&A)

Để chuẩn bị tốt nhất cho buổi bảo vệ tiến độ trước giảng viên hướng dẫn, toàn thể thành viên trong nhóm đã tổng hợp và chuẩn bị kỹ các câu hỏi phản biện cốt lõi:

#qa-card(
  "RSA và AES khác nhau cơ bản ở điểm nào?",
  [
    - *AES:* Hệ mật mã đối xứng, người gửi và người nhận dùng chung một khóa bí mật, thuật toán chủ yếu dựa trên các phép thay thế và hoán vị trên ma trận byte (mạng SPN), tốc độ xử lý phần cứng cực kỳ nhanh.
    - *RSA:* Hệ mật mã bất đối xứng, gồm cặp Public Key và Private Key, hoạt động dựa trên lý thuyết số học modulo và độ khó phân tích số nguyên lớn, chi phí tính toán lớn hơn hàng ngàn lần so với AES.
  ]
)

#qa-card(
  "Khóa công khai dùng để mã hóa khóa phiên thuộc về ai?",
  [
    Khóa công khai đó thuộc về *người nhận (Bob)*. Bất kỳ ai muốn gửi tin nhắn an toàn cho Bob đều dùng Public Key của Bob để mã hóa khóa phiên. Chỉ duy nhất Bob với Private Key tương ứng mới có thể giải mã lấy lại khóa phiên.
  ]
)

#qa-card(
  "Khóa phiên được tạo ra ở đâu và có vai trò gì?",
  [
    Khóa phiên (Session Key) là một khóa đối xứng ngẫu nhiên (độ dài 128 hoặc 256 bit), được sinh ra tại *phía người gửi (Alice)* ngay trước khi thực hiện mã hóa thông điệp, chỉ sử dụng một lần duy nhất cho phiên truyền thông đó.
  ]
)

#qa-card(
  "Cơ chế nào phát hiện bản mã bị kẻ tấn công sửa đổi trên đường truyền?",
  [
    Khi sử dụng chế độ mã hóa xác thực *AES-GCM*, thuật toán tự động sinh ra mã xác thực thông điệp *Authentication Tag* (MAC). Nếu bất kỳ bit nào của bản mã bị thay đổi trên đường truyền, giá trị tag tính toán lại ở phía nhận sẽ không khớp, Bob sẽ lập tức phát hiện và hủy bỏ gói tin.
  ]
)

#qa-card(
  "Vì sao tham số RSA thử nghiệm với p = 61, q = 53 không thể ứng dụng trong thực tế?",
  [
    Vì $n = 3233$ quá nhỏ, bất kỳ máy tính nào cũng có thể phân tích thành $61 times 53$ trong thời gian tính bằng microsecond, từ đó kẻ tấn công dễ dàng tính ra $phi(n) = 3120$ và tìm được khóa bí mật $d$. Trong thực tế, $p, q$ phải có độ dài tối thiểu 1024-bit hoặc 2048-bit trở lên.
  ]
)

#qa-card(
  "Cần bổ sung những gì để đề tài trở thành một hệ thống PGP/OpenPGP hoàn chỉnh?",
  [
    - Bổ sung cơ chế đệm an toàn *OAEP* cho RSA để chống tấn công chọn bản mã;
    - Thêm chức năng nén dữ liệu (ZIP hoặc ZLIB) trước khi mã hóa để giảm kích thước và triệt tiêu tính dư thừa thống kê;
    - Thêm chữ ký số (*Digital Signature*) bằng RSA + SHA-256 để xác thực danh tính người gửi và chống chối bỏ;
    - Quản lý khóa và định dạng gói tin theo chuẩn *RFC 4880* / *RFC 9580*.
  ]
)
