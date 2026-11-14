#import "../figures.typ": fig-hybrid-overview
#import "../styles.typ": report-table

= Giới thiệu

== Bối cảnh và phân biệt PGP với OpenPGP
Theo tài liệu an toàn mạng @stallings2017, truyền thông tin cậy cần bảo đảm bốn tính chất: bí mật, toàn vẹn, xác thực và chống chối bỏ. Để đáp ứng đồng thời hiệu năng và an toàn trao đổi khóa, các hệ thống thực tế kết hợp hai nhánh mật mã: dùng mã hóa đối xứng AES (*Advanced Encryption Standard*, tiêu chuẩn mã hóa nâng cao) @nist_fips197 cho phần dữ liệu và dùng mã hóa bất đối xứng RSA (*Rivest–Shamir–Adleman*) @rivest1978 để bảo vệ khóa trao đổi qua kênh công khai.

Trong thực tế, hai khái niệm PGP (*Pretty Good Privacy*) và OpenPGP thường bị gọi chung nhưng có bản chất khác nhau: PGP là phần mềm bảo mật thư điện tử do Phil Zimmermann phát triển năm 1991, còn OpenPGP là bộ chuẩn giao thức mở do IETF (*Internet Engineering Task Force*) ban hành dựa trên PGP qua các đặc tả RFC 4880 @rfc4880 và RFC 9580 @rfc9580. Đề tài này *mô phỏng kiến trúc mã hóa lai theo nguyên lý của chuẩn OpenPGP*: mã hóa thông điệp bằng khóa phiên AES dùng một lần, rồi mã hóa khóa phiên đó bằng khóa công khai RSA của người nhận như trong @fig-hybrid-overview.

#v(0.3em)
#align(center)[
  #fig-hybrid-overview <fig-hybrid-overview>
]
#v(0.3em)

== Mục tiêu và phạm vi đề tài
Đề tài hướng tới các mục tiêu chính trong học phần PBL3: Mạng máy tính:
+ Nắm vững cơ sở toán học của RSA (Euclid mở rộng, định lý Euler, kiểm tra nguyên tố Miller–Rabin) và chế độ xác thực AES-GCM (*Galois/Counter Mode*).
+ Tự cài đặt RSA bằng Python thuần để quan sát rõ từng bước sinh khóa và tính toán số học.
+ Kết nối RSA với AES-GCM thành luồng mã hóa lai hoàn chỉnh: sinh khóa phiên, đóng gói bản tin, giải mã và kiểm tra toàn vẹn.
+ Xây dựng mô hình Client–Server qua Socket TCP (*Transmission Control Protocol*) có đóng khung độ dài để truyền nhận ổn định trong mạng cục bộ (LAN).
+ Phát triển giao diện mô phỏng trực quan và kiểm thử các kịch bản tấn công sửa đổi dữ liệu hoặc dùng sai khóa.

Về phạm vi, hệ thống tập trung bảo đảm tính bí mật, tính toàn vẹn dữ liệu và xác thực thủ công khóa công khai qua dấu vân tay SHA-256. Nhóm dùng cấu hình RSA-256 cho bản demo thuật toán để dễ quan sát số học và RSA-512 cho mô hình Socket LAN nhằm tăng biên độ an toàn mà vẫn sinh khóa nhanh (chi tiết kích thước khóa trình bày ở Mục 3.2). Các thành phần mở rộng của OpenPGP như đệm RSA-OAEP @rfc8017 (chống tấn công Coppersmith @coppersmith1997), chữ ký số, Web of Trust và gói tin nhị phân đa tầng chưa nằm trong phạm vi phiên bản này.

== Phân công nhiệm vụ của các thành viên
Công việc nghiên cứu lý thuyết, cài đặt thuật toán, lập trình mạng và kiểm thử được phân chia cho ba thành viên như trong @tbl-task-allocation.

#figure(
  report-table(
    columns: (1.2fr, 3.0fr, 0.9fr),
    headers: ("Tên thành viên", "Nhiệm vụ", "Phần trăm đóng góp"),
    rows: (
      (
        [Vũ Duy Dương \ (`106230007`)],
        [Trưởng nhóm; thiết kế kiến trúc mã hóa lai; cài đặt RSA số học thuần (Miller–Rabin, Euclid mở rộng); phát triển giao diện mô phỏng trực quan; tổng hợp báo cáo.],
        align(center)[34%],
      ),
      (
        [Huỳnh Thiện Lộc \ (`106230052`)],
        [Nghiên cứu cơ chế mã hóa xác thực AES-GCM và hàm băm GHASH trên trường hữu hạn Galois; thiết kế và thực thi các kịch bản kiểm thử toàn vẹn.],
        align(center)[33%],
      ),
      (
        [Phan Vĩnh Sơn \ (`106230059`)],
        [Nghiên cứu giao thức Socket TCP; xây dựng mô hình Client–Server truyền nhận qua mạng LAN; cài đặt đóng khung tiền tố độ dài và đối chiếu dấu vân tay SHA-256.],
        align(center)[33%],
      ),
    ),
  ),
  caption: [Phân công nhiệm vụ của nhóm],
) <tbl-task-allocation>
