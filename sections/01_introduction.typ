#import "@preview/fletcher:0.5.6" as fletcher: diagram, node, edge

= Giới thiệu đề tài

== Bối cảnh kỹ thuật
Truyền thông an toàn trên mạng đòi hỏi đảm bảo đồng thời ba thuộc tính: tính bí mật, toàn vẹn và xác thực @stallings2017:
- *Mã hóa đối xứng (AES):* Xử lý nhanh, hiệu quả với dữ liệu lớn nhưng phụ thuộc vào bài toán thỏa thuận khóa bí mật qua kênh truyền @nist_sp800_38d.
- *Mã hóa bất đối xứng (RSA):* Giải quyết việc trao đổi khóa bằng cặp Public/Private Key, nhưng tốc độ xử lý chậm do chi phí tính lũy thừa mô-đun lớn @rfc8017.

Chuẩn OpenPGP @rfc4880 @rfc9580 giải quyết sự đánh đổi này bằng kiến trúc *Hybrid Encryption*: dùng AES mã hóa dữ liệu và dùng RSA bảo vệ khóa phiên.

#v(0.3em)
#align(center)[
  #figure(
    diagram(
      spacing: (18mm, 9mm),
      node-stroke: 0.8pt + black,
      node-fill: none,
      node-corner-radius: 4pt,
      edge-stroke: 0.8pt + black,

      // Dữ liệu đầu vào: Nét mảnh 0.8pt, nền trắng
      node((0, 0), align(center)[*Thông điệp gốc*\ ($M$)], name: <msg>, stroke: 0.8pt + black),
      // Khóa bí mật/phiên: Nét đứt (dashed), thể hiện tính tạm thời / phiên
      node((0, 1.8), align(center)[*Session Key*\ ($K$ ngẫu nhiên)], name: <key>, stroke: (paint: black, thickness: 0.8pt, dash: "dashed")),

      // Khối xử lý mã hóa: Nét liền đậm (1.2pt)
      node((1.5, 0), align(center)[*Mã hóa đối xứng*\ *AES*], name: <aes>, stroke: 1.2pt + black),
      node((1.5, 1.8), align(center)[*Mã hóa bất đối xứng*\ *RSA*], name: <rsa>, stroke: 1.2pt + black),

      // Khóa công khai: Nét chấm gạch (dash-dotted)
      node((1.5, 2.9), align(center)[*Public Key Bob*\ ($E_B, n$)], name: <pub>, stroke: (paint: black, thickness: 0.8pt, dash: "dash-dotted")),

      // Kết quả đầu ra (Bản mã): Nét đôi (double) / viền kép đậm 1.4pt, thể hiện thành phần đóng gói gửi đi
      node((3, 0), align(center)[*Bản mã dữ liệu*\ ($C_("data")$)], name: <cdata>, stroke: 1.4pt + black),
      node((3, 1.8), align(center)[*Khóa phiên mã hóa*\ ($C_("key")$)], name: <ckey>, stroke: 1.4pt + black),

      edge(<msg>, <aes>, "-|>"),
      edge(<key>, (0.7, 1.8), (0.7, 0.4), <aes>, "-|>", [Dùng $K$], label-pos: 0.5, label-side: left),
      edge(<key>, <rsa>, "-|>", [Bảo vệ $K$], label-pos: 0.5, label-side: right),
      edge(<pub>, <rsa>, "-|>"),
      edge(<aes>, <cdata>, "-|>"),
      edge(<rsa>, <ckey>, "-|>"),
    ),
    caption: [Sơ đồ nguyên lý mã hóa lai RSA – AES trong mô hình PGP],
  )
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
