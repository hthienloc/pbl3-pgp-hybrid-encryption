#import "../figures.typ": fig-rsa-numeric-example, fig-socket-sequence
#import "../styles.typ": report-table

= Thực nghiệm và kết quả

== Môi trường thực nghiệm và kiến trúc mã nguồn
Hệ thống phần mềm được tổ chức phân tầng rõ ràng với lõi thuật toán mật mã đặt tại thư mục `algorithms/` và được dùng chung bởi giao diện mô phỏng trực quan NiceGUI, bên cạnh các kịch bản kiểm thử CLI và Socket TCP:
- `algorithms/euclid.py`: Cài đặt thuật toán Euclid mở rộng (`extended_gcd`) và hàm tìm phần tử nghịch đảo mô-đun (`mod_inverse`).
- `algorithms/rsa.py`: Cài đặt hàm kiểm tra số nguyên tố Miller–Rabin (`is_prime` với $k = 20$), sinh số nguyên tố ngẫu nhiên (`generate_prime`), sinh cặp khóa RSA (`generate_rsa_keys`), mã hóa (`rsa_encrypt`) và giải mã (`rsa_decrypt`).
- `algorithms/aes_gcm.py`: Cài đặt hàm mã hóa `aes_gcm_encrypt` và giải mã có kiểm thực `aes_gcm_decrypt` dựa trên thư viện PyCryptodome.
- `algorithms/hybrid_pgp.py`: Đóng gói và giải mã trọn gói luồng dữ liệu lai PGP giữa Alice và Bob (`alice_encrypt_package`, `bob_decrypt_package`).
- `PGP_RSA_AES_Socket_3_files/`: Chứa `pgp_crypto.py`, `server_bob.py` (TCP Server, khóa RSA 512-bit) và `client_alice.py` (TCP Client) phục vụ truyền thông qua mạng LAN.
- `src/hybrid_demo.py`: Kịch bản dòng lệnh (CLI) độc lập chạy 3 kịch bản kiểm thử bảo mật (kết hợp `src/rsa.py`).
- `src/gui_nicegui.py`: Ứng dụng web mô phỏng tương tác thời gian thực hai chế độ.

== Ví dụ số học minh họa thuật toán RSA trên không gian nhỏ
Để kiểm chứng tính đúng đắn toán học của thuật toán RSA cài đặt trong `algorithms/rsa.py` bằng các phép tính thủ công trên giấy, nhóm đã thực hiện tính toán thử nghiệm trên không gian số nhỏ với các tham số mô tả trong @tbl-rsa-example.

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
) <tbl-rsa-example>

Chu trình biến đổi dữ liệu bản rõ – bản mã giữa Alice và Bob trong ví dụ số học RSA trên không gian nhỏ được thể hiện trong @fig-rsa-numeric-example.

#v(0.3em)
#align(center)[
  #fig-rsa-numeric-example <fig-rsa-numeric-example>
]
#v(0.3em)

== Kết quả thực nghiệm 3 kịch bản kiểm thử an toàn
Nhóm đã xây dựng bộ 3 kịch bản kiểm thử thực nghiệm trong `src/hybrid_demo.py` để đánh giá khả năng tự động khôi phục thông điệp và năng lực bắt lỗi vi phạm toàn vẹn dữ liệu. @tbl-test-cases tổng hợp kết quả quan sát của cả 3 kịch bản thử nghiệm.

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
) <tbl-test-cases>

Nhật ký thực thi thực tế xuất từ màn hình dòng lệnh khi chạy `python3 src/hybrid_demo.py`:

```text
=================================================================
DEMO PGP HYBRID ENCRYPTION (RSA + AES-GCM)
=================================================================

[ALICE] Thông điệp gốc: "Báo cáo tiến độ Nhóm 7: PGP Hybrid Encryption hoạt động chính xác!"
[ALICE] Mã hóa hoàn tất:
  + Encrypted Session Key (RSA) : 0x8c47f6f87ccc179734ec19b039d026691e...
  + Nonce (AES-GCM)             : 87e86fc1f28aaaa24fc05fff66b1185e
  + Ciphertext (AES)            : 721796208643fdf15c2393663cd9990281f5c915525f810a... (81 bytes)
  + Authentication Tag          : 04a4f16dfcb8b1f9e3a5e8825b17b0c9

-----------------------------------------------------------------
TEST CASE 01: Bob dùng đúng Private Key của mình
[BOB] Giải mã thành công: "Báo cáo tiến độ Nhóm 7: PGP Hybrid Encryption hoạt động chính xác!"
>>> KẾT QUẢ: [PASSED] Khôi phục chính xác 100% dữ liệu.

-----------------------------------------------------------------
TEST CASE 02: Kẻ tấn công sửa đổi 1 byte trong Ciphertext
[BOB] CẢNH BÁO AN TOÀN: Phát hiện dữ liệu bị can thiệp!
      Chi tiết ngoại lệ: MAC check failed (MAC / Authentication Tag không khớp)
>>> KẾT QUẢ: [PASSED] Chặn thành công tấn công sửa đổi bản mã.

-----------------------------------------------------------------
TEST CASE 03: Giải mã bằng Private Key không hợp lệ (Khóa của Eve)
[EVE] Thất bại: Giải mã RSA ra Session Key sai -> AES-GCM từ chối xác thực.
      Chi tiết ngoại lệ: MAC check failed (Sai khóa phiên dẫn đến kiểm thực thất bại)
>>> KẾT QUẢ: [PASSED] Từ chối truy cập trái phép khi sai khóa.
=================================================================
```

== Thực nghiệm truyền thông qua Socket TCP giữa 2 máy mạng LAN
Để tiến gần hơn tới bài toán thực tế của môn học Mạng máy tính, nhóm đã thực hiện kết nối giữa hai máy tính trong cùng mạng Wi-Fi cục bộ:
- *Máy B (Bob – Server):* Khởi động `server_bob.py`, sinh cặp khóa RSA 512-bit và lắng nghe kết nối tại địa chỉ `0.0.0.0:5000`. Màn hình tự động in ra địa chỉ IP LAN của máy (ví dụ: `192.168.1.3`) và chuỗi SHA-256 fingerprint của Public Key.
- *Máy A (Alice – Client):* Khởi động `client_alice.py 192.168.1.3`. Chương trình tự động gửi lệnh truy vấn `GET_PUBLIC_KEY` để lấy Public Key của Bob, in dấu vân tay SHA-256 fingerprint để người dùng đối chiếu chéo. Sau đó, Alice nhập thông điệp bản rõ và chọn một trong 3 chế độ gửi: gửi chuẩn, giả lập sửa Ciphertext, hoặc giả lập sai khóa phiên. Toàn bộ quá trình gửi nhận diễn ra tức thì với độ trễ mạng LAN dưới 15 ms và máy Bob hiển thị trực quan thông điệp nhận được cùng cảnh báo nếu bị can thiệp.

Quy trình bắt tay trao đổi khóa công khai và truyền nhận bản tin PGP Hybrid qua kết nối TCP Socket giữa hai máy tính được tổng hợp trong @fig-socket-sequence.

#v(0.3em)
#align(center)[
  #fig-socket-sequence <fig-socket-sequence>
]
#v(0.3em)

== Giao diện mô phỏng trực quan NiceGUI (Web Simulator)
Nhằm trực quan hóa luồng dữ liệu và từng bước biến đổi toán học của thuật toán, nhóm đã xây dựng ứng dụng Web Simulator bằng NiceGUI (chạy tại `http://localhost:8080`) với hai chế độ màn hình:
+ *Chế độ "Mô Phỏng PGP (Tích Hợp)":* Trực quan hóa góc nhìn phân tán theo 3 cột thực thể: Alice (Client) $arrow.r$ Kênh Mạng TCP $arrow.r$ Bob (Server). Giao diện tích hợp sơ đồ 8 khối dữ liệu động đổi màu theo thời gian thực (vàng: đang tính toán, xanh: thành công, đỏ: lỗi can thiệp) và bảng Terminal console ở đáy màn hình có thể kéo giãn linh hoạt để quan sát từng bước biến đổi đại số.
+ *Chế độ "Chi Tiết Từng Khối Thuật Toán":* Trực quan hóa góc nhìn chiều sâu toán học từ trên xuống dưới gồm 5 khối liên hoàn: Khối 1 (Tạo khóa RSA Bob) $arrow.r$ Khối 2 (Mã hóa AES-GCM Alice) $arrow.r$ Khối 3 (Mã hóa RSA khóa $K$) $arrow.r$ Khối 4 (Giải mã RSA khóa $K$) $arrow.r$ Khối 5 (Giải mã AES-GCM khôi phục bản rõ thông điệp $M$). Giao diện sử dụng trực tiếp giá trị số nguyên 128-bit của khóa phiên $K$ thật xuyên suốt từ Khối 2 đến Khối 5, thống nhất ký hiệu ($M$ là bản rõ, $K$ là khóa phiên) và khép kín quy trình bằng việc dùng khóa phiên đã giải mã để khôi phục nguyên vẹn thông điệp đầu vào.
