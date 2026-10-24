#import "../figures.typ": fig-hybrid-overview

= Giới thiệu đề tài

== Bối cảnh kỹ thuật
Truyền thông an toàn trên mạng đòi hỏi đảm bảo đồng thời ba thuộc tính: tính bí mật, toàn vẹn và xác thực @stallings2017:
- *Mã hóa đối xứng (AES):* Xử lý nhanh, hiệu quả với dữ liệu lớn nhưng phụ thuộc vào bài toán thỏa thuận khóa bí mật qua kênh truyền @nist_sp800_38d.
- *Mã hóa bất đối xứng (RSA):* Giải quyết việc trao đổi khóa bằng cặp Public/Private Key, nhưng tốc độ xử lý chậm do chi phí tính lũy thừa mô-đun lớn @rfc8017.

Chuẩn OpenPGP @rfc4880 @rfc9580 giải quyết sự đánh đổi này bằng kiến trúc *Hybrid Encryption*: dùng AES mã hóa dữ liệu và dùng RSA bảo vệ khóa phiên. Trong mô hình truyền thông mật mã học chuẩn mực, hai thực thể trao đổi tin được quy ước định danh là *Alice (phía gửi tin)* và *Bob (phía nhận tin)*. Bob công khai Public Key $(e_B, n)$ để mọi người gửi thông điệp mã hóa cho mình, trong khi giữ bí mật Private Key $(d_B, n)$ để giải mã.

#v(0.3em)
#align(center)[
  #fig-hybrid-overview
]
#v(0.3em)

== Mục tiêu
Chuẩn OpenPGP hoàn chỉnh chứa nhiều cơ chế phức hợp (hệ thống gói tin đa tầng, chứng thực Web of Trust, nén dữ liệu). Trong phạm vi đề tài môn học, nhóm tập trung thực nghiệm mô hình cốt lõi:
+ Nắm vững cơ sở số học của RSA (thuật toán Euclid mở rộng, định lý Euler).
+ Cài đặt thuật toán RSA bằng Python thuần để quan sát quá trình tính toán.
+ Tích hợp module RSA với AES-GCM tạo thành luồng mã hóa lai.
+ Thiết kế các kịch bản kiểm thử nhằm đánh giá tính đúng đắn và khả năng bắt lỗi toàn vẹn.

== Phạm vi
- *Thực hiện:* Cài đặt Textbook RSA dạng số học, kết hợp thư viện chuẩn AES-GCM để gửi và nhận thông điệp có kiểm thực tag.
- *Chưa thực hiện:* Chưa áp dụng cơ chế đệm an toàn RSA-OAEP @rfc8017, chưa xây dựng mạng lưới tín nhiệm Web of Trust và cấu trúc nhị phân RFC 4880.
