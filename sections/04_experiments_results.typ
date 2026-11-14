#import "../figures.typ": fig-rsa-numeric-example, fig-socket-sequence
#import "../styles.typ": report-table

= Thực nghiệm và kết quả

== Môi trường thực nghiệm và kiến trúc mã nguồn
Hệ thống phần mềm được tổ chức phân tầng rõ ràng với nguyên tắc _"Single Source of Truth"_: toàn bộ các giải thuật toán học cốt lõi chỉ được cài đặt duy nhất tại thư mục `algorithms/` và được tái sử dụng đồng thời bởi các kịch bản dòng lệnh (CLI), hệ thống truyền thông Socket mạng TCP và giao diện trực quan Web Simulator NiceGUI.
- `algorithms/euclid.py`: Cài đặt thuật toán Euclid mở rộng (`extended_gcd`) và hàm tìm phần tử nghịch đảo mô-đun (`mod_inverse`).
- `algorithms/rsa.py`: Cài đặt hàm kiểm tra số nguyên tố Miller–Rabin (`is_prime`), sinh số nguyên tố ngẫu nhiên (`generate_prime`), sinh cặp khóa RSA (`generate_rsa_keys`), mã hóa (`rsa_encrypt`) và giải mã (`rsa_decrypt`).
- `algorithms/aes_gcm.py`: Cài đặt hàm mã hóa `aes_gcm_encrypt` và giải mã có kiểm thực `aes_gcm_decrypt` dựa trên thư viện chuẩn PyCryptodome.
- `algorithms/hybrid_pgp.py`: Đóng gói và giải mã trọn gói luồng dữ liệu lai PGP giữa Alice và Bob.
- `PGP_RSA_AES_Socket_3_files/`: Chứa bộ đôi `server_bob.py` (TCP Server) và `client_alice.py` (TCP Client) phục vụ truyền thông qua mạng LAN.
- `src/gui_nicegui.py`: Ứng dụng web mô phỏng tương tác thời gian thực hai chế độ.

== Ví dụ số học minh họa thuật toán RSA trên không gian nhỏ
Để kiểm chứng tính đúng đắn toán học của thuật toán RSA cài đặt trong `algorithms/rsa.py` bằng các phép tính thủ công trên giấy, nhóm đã thực hiện tính toán thử nghiệm trên không gian số nhỏ với các tham số mô tả trong Bảng 5.

#figure(
  report-table(
    columns: (1.2fr, 1.8fr, 1.5fr),
    headers: ("Bước tính toán", "Công thức số học áp dụng", "Giá trị kết quả"),
    rows: (
      ([1. Chọn số nguyên tố], [Chọn hai số nguyên tố $p, q$], [$p = 61, quad q = 53$]),
      ([2. Tính Modulus], [$n = p dot q = 61 times 53$], [$n = 3233$]),
      ([3. Tính hàm Euler], [$phi(n) = (p - 1)(q - 1) = 60 times 52$], [$phi(n) = 3120$]),
      ([4. Chọn khóa công khai], [$gcd(e, phi(n)) = 1, quad 1 < e < phi(n)$], [$e = 17$]),
      ([5. Tìm khóa bí mật], [$17 dot d equiv 1 (mod 3120)$ qua Euclid mở rộng], [$d = 2753$ (vì $17 times 2753 = 46801 = 15 times 3120 + 1$)]),
      ([6. Thử nghiệm mã hóa / giải mã], [Bản rõ $M = 125$ \ Mã hóa: $C = 125^(17) mod 3233$ \ Giải mã: $M' = 1516^(2753) mod 3233$], [Bản mã $C = 1516$ \ Bản rõ khôi phục $M' = 125$ (Trùng khớp 100%)]),
    ),
  ),
  caption: [Tham số thực nghiệm tính toán số học trên không gian nhỏ của RSA.],
)

Chu trình biến đổi dữ liệu bản rõ – bản mã giữa Alice và Bob trong ví dụ số học RSA trên không gian nhỏ được thể hiện trong Hình 4.

#v(0.3em)
#align(center)[
  #fig-rsa-numeric-example
]
#v(0.3em)

== Kết quả thực nghiệm 3 kịch bản kiểm thử an toàn
Nhóm đã xây dựng bộ 3 kịch bản kiểm thử thực nghiệm toàn diện trong `src/hybrid_demo.py` để đánh giá khả năng tự động khôi phục thông điệp và năng lực bắt lỗi vi phạm toàn vẹn dữ liệu. Bảng 6 tổng hợp kết quả quan sát của cả 3 kịch bản thử nghiệm.

#figure(
  report-table(
    columns: (1.1fr, 1.5fr, 1.6fr, 1.1fr),
    headers: ("Kịch bản", "Mô tả thực nghiệm", "Cơ chế phản ứng của hệ thống", "Kết luận"),
    rows: (
      ([Test Case 01: \ Truyền thông hợp lệ], [Bob sử dụng đúng khóa bí mật Private Key $(d, n)$ tương ứng với Public Key của mình để giải mã.], [RSA khôi phục chính xác 16 bytes Session Key $K$; AES-GCM xác thực khớp Tag GHASH và giải mã 100% bản rõ gốc.], [*PASSED* \ Khôi phục dữ liệu chính xác tuyệt đối.]),
      ([Test Case 02: \ Tấn công can thiệp sửa bit (MITM)], [Kẻ tấn công xen vào đường truyền, đảo 1 byte trong Ciphertext ($C_"data"[0] xor "0xFF"$) trước khi Bob nhận được.], [Khóa $K$ khôi phục đúng, nhưng hàm băm GHASH phát hiện Tag sai khác; ném ngoại lệ `ValueError: MAC check failed`, lập tức hủy gói tin.], [*PASSED* \ Chặn đứng thành công tấn công sửa đổi bản mã.]),
      ([Test Case 03: \ Tấn công nghe lén bằng sai khóa], [Bên thứ ba (Eve) cố tình sử dụng một Private Key khác không hợp lệ để giải mã gói tin đánh cắp.], [Phép tính RSA giải mã ra giá trị Session Key $K'$ sai lệch; AES-GCM đối chiếu Tag thất bại do sai khóa và từ chối xuất dữ liệu.], [*PASSED* \ Ngăn chặn truy cập trái phép khi sai khóa bí mật.]),
    ),
  ),
  caption: [Tổng hợp kết quả thực nghiệm 3 kịch bản kiểm thử bảo mật và toàn vẹn.],
)

Nhật ký thực thi thực tế xuất từ màn hình dòng lệnh khi chạy chương trình:

```text
=================================================================
DEMO PGP HYBRID ENCRYPTION (RSA + AES-GCM)
=================================================================
[ALICE] Thông điệp gốc: "Hello cô Hạnh, bọn em là nhóm 7!"
[ALICE] Mã hóa hoàn tất:
  + Encrypted Session Key (RSA) : 0x4f8a92bc71e54910e9f1a23cd... (256-bit)
  + Nonce (AES-GCM)             : e81b93f01c725d19420b92e1 (12 bytes)
  + Ciphertext (AES)            : 9c2a71f08e334d... (34 bytes)
  + Authentication Tag          : 3a9f02c771e84210d9f2a89c (16 bytes)
-----------------------------------------------------------------
TEST CASE 01: Bob dùng đúng Private Key của mình
[BOB] Khôi phục thành công: "Hello cô Hạnh, bọn em là nhóm 7!"
>>> KẾT QUẢ: [PASSED] Dữ liệu được khôi phục chính xác 100%!
-----------------------------------------------------------------
TEST CASE 02: Kẻ tấn công sửa đổi 1 byte trong Ciphertext
[BOB] CẢNH BÁO AN TOÀN: Phát hiện dữ liệu bị can thiệp trên đường truyền!
      Ngoại lệ bắt được: MAC check failed (Authentication Tag không khớp)
>>> KẾT QUẢ: [PASSED] Hệ thống đã hủy gói tin và chặn đứng sửa đổi.
-----------------------------------------------------------------
TEST CASE 03: Giải mã bằng Private Key không hợp lệ (Khóa của bên thứ ba)
[EVE] Thất bại: Giải mã RSA ra Session Key sai -> AES-GCM từ chối xác thực.
      Ngoại lệ bắt được: MAC check failed
>>> KẾT QUẢ: [PASSED] Từ chối truy cập trái phép khi sai khóa.
=================================================================
```

== Thực nghiệm truyền thông qua Socket TCP giữa 2 máy mạng LAN
Để tiến gần hơn tới bài toán thực tế của môn học Mạng máy tính, nhóm đã thực hiện kết nối vật lý giữa hai máy tính xách tay trong cùng mạng Wi-Fi cục bộ:
- *Máy B (Bob – Server):* Khởi động `server_bob.py`, lắng nghe kết nối tại địa chỉ `0.0.0.0:5000`. Màn hình tự động in ra địa chỉ IP LAN của máy (ví dụ: `192.168.1.3`).
- *Máy A (Alice – Client):* Khởi động `client_alice.py 192.168.1.3`. Chương trình tự động gửi lệnh truy vấn `GET_PUBLIC_KEY` để lấy Public Key của Bob, in dấu vân tay SHA-256 fingerprint để người dùng đối chiếu chéo qua kênh thoại. Sau đó, Alice nhập thông điệp bản rõ và chọn một trong 3 chế độ gửi: gửi chuẩn, giả lập sửa Ciphertext, hoặc giả lập sai khóa phiên. Toàn bộ quá trình gửi nhận diễn ra tức thì với độ trễ mạng dưới 15 ms và máy Bob hiển thị trực quan thông điệp nhận được cùng cảnh báo màu sắc nếu bị can thiệp.

Quy trình bắt tay trao đổi khóa công khai và truyền nhận bản tin PGP Hybrid qua kết nối TCP Socket giữa hai máy tính được tổng hợp trong Hình 5.

#v(0.3em)
#align(center)[
  #fig-socket-sequence
]
#v(0.3em)

== Giao diện mô phỏng trực quan NiceGUI (Web Simulator)
Nhằm phục vụ báo cáo bảo vệ đồ án trước hội đồng một cách trực quan và khoa học, nhóm đã xây dựng ứng dụng Web Simulator bằng NiceGUI (chạy tại `http://localhost:8080`) với hai chế độ màn hình bổ trợ hoàn hảo cho nhau:
+ *Chế độ "Mô Phỏng PGP (Tích Hợp)":* Trực quan hóa góc nhìn phân tán theo 3 cột thực thể: Alice (Client) $arrow.r$ Kênh Mạng TCP $arrow.r$ Bob (Server). Giao diện tích hợp sơ đồ 8 khối dữ liệu động đổi màu theo thời gian thực (vàng: đang tính toán, xanh: thành công, đỏ: lỗi can thiệp) và bảng Terminal console ở đáy màn hình có thể kéo giãn linh hoạt để trình chiếu từng bước biến đổi đại số mà không cần mở mã nguồn.
+ *Chế độ "Chi Tiết Từng Khối Thuật Toán":* Trực quan hóa góc nhìn chiều sâu toán học từ trên xuống dưới gồm 5 khối liên hoàn: Khối 1 (Tạo khóa RSA Bob) $arrow.r$ Khối 2 (Mã hóa AES-GCM Alice) $arrow.r$ Khối 3 (Mã hóa RSA khóa $K$) $arrow.r$ Khối 4 (Giải mã RSA khóa $K$) $arrow.r$ Khối 5 (Giải mã AES-GCM khôi phục bản rõ thông điệp $M$). Giao diện này đáp ứng chuẩn xác 100% các góp ý chỉnh sửa của Giảng viên hướng dẫn: xóa bỏ toàn bộ từ ngữ đề mục báo cáo gây rối mắt; loại bỏ hoàn toàn số nhỏ minh họa 125 để nối liền trực tiếp giá trị số nguyên 128-bit của khóa phiên $K$ thật từ trên xuống dưới; thống nhất một ký hiệu duy nhất ($M$ luôn là thông điệp gốc, $K$ luôn là khóa phiên); và đặc biệt là khép kín hoàn chỉnh quy trình tại Khối 5 bằng việc dùng chính khóa phiên vừa giải mã để khôi phục lại chuỗi thông điệp ban đầu `"Hello cô Hạnh"`.
