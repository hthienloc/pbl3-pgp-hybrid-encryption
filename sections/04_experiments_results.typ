#import "../figures.typ": fig-rsa-numeric-example, fig-socket-sequence
#import "../styles.typ": report-table

= Thực nghiệm và kết quả

== Môi trường thực nghiệm và kiến trúc mã nguồn
Hệ thống tổ chức lõi thuật toán tại `algorithms/` dùng chung cho giao diện NiceGUI, bên cạnh các kịch bản CLI và Socket TCP:
- `algorithms/euclid.py`: Thuật toán Euclid mở rộng (`extended_gcd`) và nghịch đảo mô-đun (`mod_inverse`).
- `algorithms/rsa.py`: Kiểm tra nguyên tố Miller–Rabin (`is_prime`, $k = 20$), sinh số nguyên tố (`generate_prime`), sinh khóa (`generate_rsa_keys`), mã hóa (`rsa_encrypt`) và giải mã (`rsa_decrypt`).
- `algorithms/aes_gcm.py`: Hàm `aes_gcm_encrypt` và `aes_gcm_decrypt` sử dụng thư viện PyCryptodome.
- `algorithms/hybrid_pgp.py`: Đóng gói và giải mã luồng lai PGP (`alice_encrypt_package`, `bob_decrypt_package`).
- `PGP_RSA_AES_Socket_3_files/`: Gồm `pgp_crypto.py`, `server_bob.py` (TCP Server, RSA 512-bit) và `client_alice.py` (TCP Client) truyền thông qua mạng LAN.
- `src/hybrid_demo.py`: Kịch bản CLI chạy 3 kịch bản kiểm thử bảo mật (kết hợp `src/rsa.py`).
- `src/gui_nicegui.py`: Ứng dụng web mô phỏng tương tác hai chế độ.

== Ví dụ số học minh họa thuật toán RSA trên không gian nhỏ
Để kiểm chứng `algorithms/rsa.py` bằng tính toán thủ công, @tbl-rsa-example và @fig-rsa-numeric-example trình bày ví dụ trên không gian số nhỏ.

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

#v(0.3em)
#align(center)[
  #fig-rsa-numeric-example <fig-rsa-numeric-example>
]
#v(0.3em)

== Kết quả thực nghiệm 3 kịch bản kiểm thử an toàn
@tbl-test-cases tổng hợp kết quả 3 kịch bản kiểm thử trong `src/hybrid_demo.py`.

#figure(
  report-table(
    columns: (1.1fr, 1.5fr, 1.6fr, 1.1fr),
    headers: ("Kịch bản", "Mô tả thực nghiệm", "Cơ chế phản ứng của hệ thống", "Kết luận"),
    rows: (
      ([Test Case 01: \ Truyền thông hợp lệ], [Bob dùng đúng Private Key $(d, n)$ để giải mã.], [RSA khôi phục 16 bytes Session Key $K$; AES-GCM khớp Tag GHASH và giải mã 100% bản rõ.], [*PASSED* \ Khôi phục chính xác 100%.]),
      ([Test Case 02: \ Tấn công can thiệp sửa bit (MITM)], [Đảo 1 byte trong Ciphertext ($C_"data"[0] xor "0xFF"$) trên đường truyền.], [Khóa $K$ khôi phục đúng, nhưng GHASH phát hiện Tag sai khác; ném `ValueError: MAC check failed` và hủy gói tin.], [*PASSED* \ Chặn tấn công sửa đổi bản mã.]),
      ([Test Case 03: \ Tấn công nghe lén bằng sai khóa], [Eve dùng Private Key khác không hợp lệ để giải mã gói tin.], [RSA giải ra Session Key $K'$ sai; AES-GCM đối chiếu Tag thất bại và từ chối xuất dữ liệu.], [*PASSED* \ Ngăn truy cập trái phép.]),
    ),
  ),
  caption: [Tổng hợp kết quả thực nghiệm 3 kịch bản kiểm thử bảo mật và toàn vẹn.],
) <tbl-test-cases>

Nhật ký thực thi thực tế khi chạy `python3 src/hybrid_demo.py`:

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
Thử nghiệm truyền thông được thực hiện giữa hai máy tính trong cùng mạng Wi-Fi cục bộ:
- *Máy B (Bob – Server):* Chạy `server_bob.py`, sinh cặp khóa RSA 512-bit, lắng nghe tại `0.0.0.0:5000` và hiển thị IP LAN (ví dụ `192.168.1.3`) cùng SHA-256 fingerprint của Public Key.
- *Máy A (Alice – Client):* Chạy `client_alice.py 192.168.1.3`, gửi lệnh `GET_PUBLIC_KEY` để lấy Public Key của Bob và đối chiếu SHA-256 fingerprint. Alice nhập thông điệp và chọn 1 trong 3 chế độ gửi (gửi chuẩn, giả lập sửa Ciphertext, giả lập sai khóa phiên). Độ trễ truyền nhận qua mạng LAN dưới 15 ms; phía Bob hiển thị bản rõ giải mã hoặc cảnh báo khi phát hiện can thiệp.

Luồng bắt tay trao đổi khóa và truyền nhận bản tin qua TCP Socket được minh họa trong @fig-socket-sequence.

#v(0.3em)
#align(center)[
  #fig-socket-sequence <fig-socket-sequence>
]
#v(0.3em)

== Giao diện mô phỏng trực quan NiceGUI (Web Simulator)
Ứng dụng Web Simulator xây dựng bằng NiceGUI (`http://localhost:8080`) cung cấp hai chế độ mô phỏng:
+ *Chế độ "Mô Phỏng PGP (Tích Hợp)":* Trình bày luồng dữ liệu theo 3 cột thực thể: Alice (Client) $arrow.r$ Kênh Mạng TCP $arrow.r$ Bob (Server), gồm sơ đồ 8 khối dữ liệu động theo thời gian thực và bảng console log ghi lại từng bước xử lý.
+ *Chế độ "Chi Tiết Từng Khối Thuật Toán":* Trình bày 5 khối tuần tự từ trên xuống: Khối 1 (Tạo khóa RSA Bob) $arrow.r$ Khối 2 (Mã hóa AES-GCM Alice) $arrow.r$ Khối 3 (Mã hóa RSA khóa $K$) $arrow.r$ Khối 4 (Giải mã RSA khóa $K$) $arrow.r$ Khối 5 (Giải mã AES-GCM khôi phục $M$). Luồng dữ liệu truyền trực tiếp giá trị số nguyên 128-bit của khóa phiên $K$ thật xuyên suốt từ Khối 2 đến Khối 5 để khôi phục thông điệp gốc.
