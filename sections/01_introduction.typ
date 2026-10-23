#import "@preview/fletcher:0.5.6" as fletcher: diagram, node, edge

= Giới thiệu đề tài

== Bối cảnh và Đặt vấn đề
Trong môi trường truyền thông mạng máy tính hiện đại, việc bảo đảm an toàn dữ liệu khi truyền tải qua các kênh truyền không tin cậy đặt ra ba yêu cầu cốt lõi: *tính bí mật*, *tính toàn vẹn* và *tính xác thực*.

Để giải quyết bài toán này, các hệ thống mật mã học thường dựa trên hai trường phái chính:
- *Mã hóa đối xứng (tiêu biểu là AES):* Đạt tốc độ xử lý phần cứng cực cao, tối ưu cho dữ liệu khối lượng lớn, nhưng vấp phải trở ngại lớn về *bài toán phân phối khóa* (làm sao để chuyển khóa bí mật qua mạng mà không bị kẻ nghe lén đánh cắp).
- *Mã hóa bất đối xứng (tiêu biểu là RSA):* Giải quyết triệt để vấn đề trao đổi khóa thông qua cặp Public Key và Private Key, nhưng chi phí tính toán các phép toán lũy thừa số học mô-đun quá lớn, tạo nên hiện tượng nghẽn cổ chai hiệu năng khi xử lý các tập tin dung lượng lớn.

Chuẩn *PGP* và chuẩn mở *OpenPGP (RFC 4880, RFC 9580)* đã tiên phong giải quyết bài toán dung hòa giữa độ bảo mật và hiệu năng thông qua kiến trúc *Hybrid Encryption*.

#v(0.5em)
#align(center)[
  #figure(
    diagram(
      spacing: (18mm, 10mm),
      node-stroke: 0.8pt + rgb("#3b82f6"),
      node-fill: rgb("#eff6ff"),
      node-corner-radius: 4pt,
      edge-stroke: 0.8pt + rgb("#475569"),

      // Khối dữ liệu đầu vào
      node((0, 0), align(center)[*Thông điệp gốc*\ (Dữ liệu lớn $M$)], name: <msg>, fill: rgb("#f8fafc"), stroke: 0.8pt + rgb("#94a3b8")),
      node((0, 1.8), align(center)[*Session Key ($K$)*\ (Sinh ngẫu nhiên)], name: <key>, fill: rgb("#fef3c7"), stroke: 0.8pt + rgb("#f59e0b")),

      // Khối thuật toán mã hóa
      node((1.5, 0), align(center)[*Mã hóa đối xứng*\ *AES*], name: <aes>, fill: rgb("#dbeafe"), stroke: 1pt + rgb("#2563eb")),
      node((1.5, 1.8), align(center)[*Mã hóa bất đối xứng*\ *RSA*], name: <rsa>, fill: rgb("#ede9fe"), stroke: 1pt + rgb("#7c3aed")),

      // Khóa công khai của Bob
      node((1.5, 2.9), align(center)[*Public Key (Bob)*\ (Khóa công khai)], name: <pub>, fill: rgb("#f1f5f9"), stroke: 0.8pt + rgb("#94a3b8")),

      // Kết quả đóng gói
      node((3, 0), align(center)[*Bản mã thông điệp*\ ($C_("data")$)], name: <cdata>, fill: rgb("#dcfce7"), stroke: 0.8pt + rgb("#16a34a")),
      node((3, 1.8), align(center)[*Khóa phiên mã hóa*\ ($C_("key")$)], name: <ckey>, fill: rgb("#dcfce7"), stroke: 0.8pt + rgb("#16a34a")),

      // Các mũi tên luồng xử lý
      edge(<msg>, <aes>, "-|>"),
      edge(<key>, (0.9, 1.8), (0.9, 0.4), <aes>, "-|>", [Dùng $K$], label-pos: 0.7, label-side: right),
      edge(<key>, <rsa>, "-|>", [Bảo vệ $K$], label-pos: 0.5, label-side: right),
      edge(<pub>, <rsa>, "-|>"),
      edge(<aes>, <cdata>, "-|>"),
      edge(<rsa>, <ckey>, "-|>"),
    ),
    caption: [Sơ đồ nguyên lý mã hóa lai RSA – AES trong mô hình PGP],
  )
]
#v(0.5em)

== Mục tiêu đề tài
Chuẩn PGP/OpenPGP trên thực tế là một hệ thống mật mã học vô cùng rộng lớn và phức tạp, bao gồm rất nhiều phân hệ: định dạng gói tin nhị phân đa tầng (RFC 4880, RFC 9580), nén dữ liệu (ZIP/ZLIB), mô hình tín nhiệm mạng lưới (Web of Trust), hệ thống quản lý khóa công khai/khóa bí mật và cơ chế chứng thực khóa.

Nhận thức được quy mô đồ sộ đó, trong khuôn khổ học phần *PBL3: Mạng máy tính*, nhóm không đặt mục tiêu xây dựng lại toàn bộ một phần mềm PGP hoàn chỉnh mà chỉ tập trung đi sâu vào nghiên cứu và hiện thực hóa *trái tim kiến trúc cốt lõi* của PGP: *cơ chế mã hóa lai (Hybrid Encryption) giữa RSA và AES*.

Mục tiêu cụ thể của nhóm bao gồm:
+ *Nắm vững nền tảng lý thuyết:* Phân tích toán học số học mô-đun của RSA (định lý Euler, hàm Euler Phi, thuật toán Euclid mở rộng) và nguyên lý bảo mật của mã hóa đối xứng AES.
+ *Lập trình tự cài đặt (From Scratch):* Tự tay xây dựng thuật toán RSA bằng ngôn ngữ Python thuần túy mà không phụ thuộc vào các thư viện mật mã có sẵn nhằm hiểu sâu bản chất từng phép tính.
+ *Mô phỏng mô hình mã hóa lai:* Kết hợp thuật toán RSA tự viết với AES để đóng gói và bảo vệ khóa phiên (*Session Key*), tái hiện quy trình truyền tin an toàn giữa Alice và Bob.
+ *Thực nghiệm và đánh giá:* Xây dựng các ca kiểm thử điển hình để kiểm tra tính đúng đắn khi giải mã và khả năng phát hiện can thiệp bản mã.

== Phạm vi đề tài
Từ mục tiêu đã xác định, nhóm giới hạn phạm vi nghiên cứu và triển khai của đề tài như sau:
- *Phạm vi thuật toán:*
  - Cài đặt thuật toán RSA cơ bản (Textbook RSA) trên tập số học Python phục vụ mục đích minh họa nguyên lý sinh khóa, mã hóa và giải mã số học.
  - Sử dụng thuật toán AES để mã hóa khối dữ liệu thông điệp thông qua khóa phiên ngẫu nhiên.
- *Phạm vi chương trình:* Xây dựng ứng dụng mô phỏng quy trình gửi - nhận dữ liệu giữa hai đối tượng Alice và Bob trên cùng môi trường thực thi thử nghiệm.
- *Giới hạn ngoài phạm vi:*
  - Đề tài chưa triển khai định dạng gói dữ liệu đầy đủ theo chuẩn RFC 4880 (gói PKESK, SEIPD nhị phân).
  - Chưa tích hợp cơ chế nén dữ liệu trước mã hóa và hệ thống quản lý vòng đời chứng thư số (Web of Trust).
  - Mô-đun RSA tự viết nhằm phục vụ mục đích học tập giải thuật, chưa bổ sung cơ chế đệm an toàn ngẫu nhiên (OAEP padding) dùng trong các sản phẩm thương mại thực tế.
