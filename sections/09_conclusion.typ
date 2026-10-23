= Kết quả đạt được và hướng phát triển

Dưới đây là tổng hợp tiến độ nghiên cứu của nhóm cùng lộ trình hoàn thiện cho đồ án trong giai đoạn tiếp theo:

== Tổng kết khối lượng công việc

#align(center)[
  #table(
    columns: (1fr, 1fr),
    fill: (x, y) => if y == 0 { rgb("#dcfce7") } else { none },
    stroke: 0.5pt + rgb("#bbf7d0"),
    inset: 9pt,
    [*Đã thực hiện*], [*Hướng phát triển tiếp theo*],
    [
      - Nắm vững cơ sở lý thuyết về mô hình Hybrid Encryption và cấu trúc chuẩn PGP/OpenPGP.
      - Tự lập trình giải thuật RSA toán học bằng Python (Euclid mở rộng, tính modulo).
      - Minh họa thành công chu trình mã hóa và giải mã số học RSA.
      - Xây dựng chương trình Hybrid tích hợp RSA – AES và hoàn thành bộ 3 kiểm thử cơ bản.
    ],
    [
      - Rà soát, làm sạch và tối ưu hóa mã nguồn toàn bộ hệ thống tích hợp.
      - Mở rộng chức năng tạo chữ ký số (Digital Signature) bằng RSA và hàm băm SHA-256 để đảm bảo tính chống chối bỏ.
      - Kiểm thử hệ thống với dữ liệu thực tế lớn (tệp tin văn bản, ảnh, nhị phân).
      - Đo đạc thời gian thực thi (độ trễ và thông lượng) giữa mã hóa thuần RSA so với Hybrid Encryption.
    ]
  )
]

== Lộ trình kế hoạch triển khai giai đoạn tới (Roadmap)

#align(center)[
  #table(
    columns: (auto, 1.2fr, 2fr),
    fill: (x, y) => if y == 0 { rgb("#e0e7ff") } else if calc.even(y) { rgb("#f8fafc") } else { none },
    stroke: 0.5pt + rgb("#cbd5e1"),
    inset: 8pt,
    [*Thời gian*], [*Nhiệm vụ trọng tâm*], [*Kết quả dự kiến đầu ra*],
    [Tuần 1], [Hoàn thiện module Chữ ký số], [Tích hợp RSA + SHA-256 để ký và xác thực chữ ký điện tử.],
    [Tuần 2], [Thực nghiệm tệp tin dung lượng lớn], [Xử lý mã hóa/giải mã các file nhị phân, hình ảnh, tài liệu PDF.],
    [Tuần 3], [Đo đạc Benchmark & Hiệu năng], [Biểu đồ so sánh thời gian thực thi giữa RSA thuần và Hybrid Encryption.],
    [Tuần 4], [Hoàn thiện báo cáo & Slide bảo vệ], [Đóng gói mã nguồn hoàn chỉnh và tài liệu báo cáo nghiệm thu.]
  )
]

#import "../components.typ": info-box
#info-box(title: "Định vị phạm vi đề tài")[
  *Phạm vi hiện tại:* Chương trình là bản mô phỏng trực quan cơ chế mã hóa lai RSA – AES phục vụ mục tiêu học tập và nghiên cứu cấu trúc PGP. Nhóm chưa đồng nhất bản demo này với một phần mềm OpenPGP hoàn chỉnh (như GnuPG), vốn đòi hỏi định dạng gói dữ liệu RFC 4880, hệ thống chứng thực Web of Trust và cơ chế quản lý khóa an toàn trên đĩa cứng.
]
