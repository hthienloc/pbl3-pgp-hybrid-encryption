#import "../figures.typ": fig-rsa-numeric-example, fig-socket-sequence
#import "../styles.typ": report-table

= Thực nghiệm và kết quả

== Ví dụ số học minh họa thuật toán RSA trên không gian nhỏ
Để kiểm chứng tính đúng đắn của thuật toán RSA tự cài đặt bằng phép tính thủ công, nhóm thực hiện thử nghiệm trên không gian số nhỏ với các tham số tổng hợp trong @tbl-rsa-example và chu trình xử lý minh họa tại @fig-rsa-numeric-example.

#figure(
  report-table(
    columns: (1.2fr, 1.8fr, 1.5fr),
    headers: ("Bước tính toán", "Công thức số học áp dụng", "Giá trị kết quả"),
    rows: (
      ([1. Chọn số nguyên tố], [Chọn hai số nguyên tố $p, q$], [$p = 61, quad q = 53$]),
      ([2. Tính modulus], [$n = p dot q = 61 times 53$], [$n = 3233$]),
      ([3. Tính hàm Euler], [$phi(n) = (p - 1)(q - 1) = 60 times 52$], [$phi(n) = 3120$]),
      ([4. Chọn khóa công khai], [$gcd(e, phi(n)) = 1, quad 1 < e < phi(n)$], [$e = 17$]),
      ([5. Tìm khóa bí mật], [$17 dot d equiv 1 (mod 3120)$ qua Euclid mở rộng], [$d = 2753$ (vì $17 times 2753 = 46801 = 15 times 3120 + 1$)]),
      ([6. Mã hóa và giải mã], [Bản rõ $M = 125$ \ Mã hóa: $C = 125^(17) mod 3233$ \ Giải mã: $M' = 1516^(2753) mod 3233$], [Bản mã $C = 1516$ \ Bản rõ khôi phục $M' = 125$ (trùng khớp)]),
    ),
  ),
  caption: [Tham số thực nghiệm tính toán số học trên không gian nhỏ của RSA],
) <tbl-rsa-example>

#v(0.3em)
#align(center)[
  #fig-rsa-numeric-example <fig-rsa-numeric-example>
]
#v(0.3em)

== Kết quả kiểm thử ba kịch bản an toàn
Nhóm triển khai chương trình thử nghiệm trên ngôn ngữ Python kết hợp thư viện mật mã PyCryptodome với khóa RSA 512-bit (hai số nguyên tố 256-bit) và khóa phiên AES 128-bit để đánh giá ba kịch bản: truyền thông hợp lệ, tấn công sửa đổi bản mã trên đường truyền và tấn công giải mã bằng khóa bí mật sai. Kết quả tóm tắt được trình bày trong @tbl-test-cases.

#figure(
  report-table(
    columns: (1.3fr, 2.5fr, 0.9fr),
    headers: ("Kịch bản", "Mô tả ngắn gọn", "Kết quả"),
    rows: (
      ([Kịch bản 1: Truyền thông hợp lệ], [Bên nhận dùng đúng khóa bí mật của mình để giải mã gói tin từ bên gửi.], [Đạt (PASSED)]),
      ([Kịch bản 2: Sửa bit bản mã], [Kẻ tấn công đảo 1 byte đầu tiên của bản mã dữ liệu trước khi gói tin tới bên nhận.], [Đạt (PASSED)]),
      ([Kịch bản 3: Dùng sai khóa bí mật], [Bên thứ ba dùng một khóa bí mật khác để giải mã gói tin đánh cắp.], [Đạt (PASSED)]),
    ),
  ),
  caption: [Tóm tắt kết quả thực nghiệm ba kịch bản kiểm thử],
) <tbl-test-cases>

Dưới đây là nhật ký chạy thực tế của từng kịch bản để kiểm chứng kết quả đạt yêu cầu:

- *Kịch bản 1 (Truyền thông hợp lệ):* Gói tin gồm khóa phiên mã hóa 512-bit, vector khởi tạo 12 byte, bản mã dữ liệu 81 byte và thẻ xác thực 16 byte được bên nhận giải mã chính xác 100%.

```text
[ALICE] Thông điệp gốc: "Báo cáo tiến độ Nhóm 7: PGP Hybrid Encryption hoạt động chính xác!"
[ALICE] Mã hóa hoàn tất:
  + Khóa phiên mã hóa (RSA)     : 0x21fe7b44d00027e78b0d491225917c9d11...
  + Vector khởi tạo (AES-GCM)   : cf143dfebc01f7d3288721c5 (12 bytes)
  + Bản mã dữ liệu (AES)        : 4fc7c13e891897cd657a30a80a80068912... (81 bytes)
  + Thẻ xác thực (Tag)          : 0cb440f3f4fd0e69f548cf1841f6e89b (16 bytes)

TEST CASE 01: Bob dùng đúng Private Key của mình
[BOB] Giải mã thành công: "Báo cáo tiến độ Nhóm 7: PGP Hybrid Encryption hoạt động chính xác!"
>>> KẾT QUẢ: [PASSED] Khôi phục chính xác 100% dữ liệu.
```

- *Kịch bản 2 (Tấn công sửa bit bản mã):* Khi 1 byte của bản mã dữ liệu bị đảo bit trên đường truyền, giá trị băm GHASH tính lại không khớp với thẻ xác thực nên bên nhận hủy gói tin.

```text
TEST CASE 02: Kẻ tấn công sửa đổi 1 byte trong Ciphertext
[BOB] CẢNH BÁO AN TOÀN: Phát hiện dữ liệu bị can thiệp!
      Chi tiết lỗi: Kiểm tra thẻ xác thực thất bại (Tag không khớp)
>>> KẾT QUẢ: [PASSED] Chặn thành công tấn công sửa đổi bản mã.
```

- *Kịch bản 3 (Dùng sai khóa bí mật):* Dùng khóa bí mật khác để giải mã khiến khóa phiên khôi phục vượt quá 128 bit hoặc sai lệch, bị hệ thống từ chối ngay lập tức.

```text
TEST CASE 03: Giải mã bằng Private Key không hợp lệ (Khóa của Eve)
[EVE] Thất bại: Giải mã RSA ra Session Key sai -> Từ chối xác thực.
      Chi tiết lỗi: Khóa phiên giải mã vượt quá 128-bit (sai khóa hoặc bị can thiệp)
>>> KẾT QUẢ: [PASSED] Từ chối truy cập trái phép khi sai khóa.
```

== Thực nghiệm truyền thông Socket TCP giữa hai máy mạng LAN
Để kiểm chứng hoạt động trên môi trường mạng thực tế, nhóm triển khai thử nghiệm giữa hai máy tính kết nối trong cùng mạng Wi-Fi cục bộ theo mô hình Khách – Chủ (Client–Server) qua giao thức TCP ở cổng 5000, như minh họa trong @fig-socket-sequence.

Tại máy nhận (đóng vai trò Server), chương trình tự động sinh cặp khóa RSA 512-bit (từ hai số nguyên tố 256-bit), hiển thị địa chỉ IP cục bộ cùng dấu vân tay SHA-256 của khóa công khai và mở cổng lắng nghe kết nối. Tại máy gửi (đóng vai trò Client), người dùng nhập địa chỉ IP của máy nhận để kết nối, tự động tải về khóa công khai và đối chiếu dấu vân tay SHA-256 nhằm xác nhận đúng người nhận. Sau khi người gửi nhập thông điệp và chọn chế độ truyền (gửi hợp lệ, giả lập sửa bản mã hoặc giả lập sai khóa), gói tin được đóng khung kèm tiền tố 4 byte độ dài và truyền qua mạng LAN. Quá trình truyền nhận và giải mã hoàn tất với độ trễ dưới 15 ms; các gói tin bị sửa đổi đều bị máy nhận phát hiện và từ chối xử lý.

#v(0.3em)
#align(center)[
  #fig-socket-sequence <fig-socket-sequence>
]
#v(0.3em)

== Giao diện mô phỏng trực quan trên nền web
Nhằm hỗ trợ quan sát trực tiếp quá trình mã hóa và giải mã, nhóm xây dựng ứng dụng mô phỏng tương tác trên nền web (sử dụng thư viện NiceGUI) gồm hai chế độ màn hình:
+ *Chế độ mô phỏng luồng tích hợp:* Trình bày bố cục ba cột gồm bên gửi (Alice), kênh truyền mạng và bên nhận (Bob). Người dùng có thể thực hiện từng bước hoặc chạy tuần tự toàn bộ quy trình, theo dõi sơ đồ trạng thái đổi màu theo thời gian thực và kích hoạt giả lập sửa bit trực tiếp trên gói tin trước khi bên nhận giải mã.
+ *Chế độ chi tiết từng khối thuật toán:* Hiển thị năm khối tính toán liên hoàn từ trên xuống dưới gồm sinh khóa RSA, mã hóa dữ liệu AES-GCM, mã hóa khóa phiên bằng RSA, giải mã khóa phiên bằng RSA và giải mã AES-GCM khôi phục bản rõ. Khóa phiên 128-bit thực tế được truyền xuyên suốt qua các khối giúp người học kiểm tra sự nhất quán giữa lý thuyết số học và dữ liệu chạy thật.
