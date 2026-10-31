= Demo chương trình và kết quả kiểm thử

Để kiểm tra tính đúng đắn và khả năng phát hiện lỗi của chương trình Python (`src/hybrid_demo.py`), hệ thống được thử nghiệm qua 3 kịch bản:

#align(center)[
  #table(
    columns: (auto, 1.2fr, 1.8fr),
    fill: (x, y) => if y == 0 { rgb("#e0e7ff") } else if calc.even(y) { rgb("#f8fafc") } else { none },
    stroke: 0.5pt + rgb("#cbd5e1"),
    inset: 8pt,
    [*Kiểm thử*], [*Kịch bản thử nghiệm*], [*Kết quả quan sát & Phân tích*],
    [*Test 01*], [Bob sử dụng đúng Private Key tương ứng với Public Key của mình.], [Khôi phục thành công 100% nội dung thông điệp gốc ban đầu. Khóa phiên và dữ liệu được giải mã chính xác.],
    [*Test 02*], [Kẻ tấn công xen vào giữa (Man-in-the-Middle) can thiệp, đảo 1 bit trong Ciphertext trước khi Bob giải mã.], [Phát hiện can thiệp: Thư viện bắt lỗi ngoại lệ `ValueError: MAC check failed`. Bản tin bị hủy bỏ ngay lập tức.],
    [*Test 03*], [Giải mã bằng một Private Key không khớp (khóa của bên thứ ba Eve).], [Thất bại: Phép tính RSA cho ra giá trị Session Key sai lệch, dẫn tới giải mã AES thất bại và ném ngoại lệ.]
  )
]

== Kết quả thực thi trên terminal

Dưới đây là nhật ký xuất từ terminal khi chạy `python3 src/hybrid_demo.py`:

```text
=================================================================
DEMO PGP HYBRID ENCRYPTION (RSA + AES-GCM)
=================================================================

[ALICE] Thông điệp gốc: "Báo cáo tiến độ Nhóm 7: PGP Hybrid Encryption hoạt động chính xác!"
[ALICE] Mã hóa hoàn tất:
  + Encrypted Session Key (RSA) : 0xbe013053248c3eb35cee26cd3ec7e6ae2c...
  + Nonce (AES-GCM)             : 0398e089ee4da8b197573906d2cc0cd5
  + Ciphertext (AES)            : a558ef5f7a0d67633054f9e7e588c7d8988db1c9f2a8a90e... (81 bytes)
  + Authentication Tag          : a8d0cf9ba50332bc0b175330d498275a

-----------------------------------------------------------------
TEST CASE 01: Bob dùng đúng Private Key của mình
[BOB] Giải mã thành công: "Báo cáo tiến độ Nhóm 7: PGP Hybrid Encryption hoạt động chính xác!"
>>> KẾT QUẢ: [PASSED] Khôi phục chính xác 100% dữ liệu.

-----------------------------------------------------------------
TEST CASE 02: Kẻ tấn công sửa đổi 1 byte trong Ciphertext
[BOB] CẢNH BÁO AN TOÀN: Phát hiện dữ liệu bị can thiệp!
      Chi tiết ngoại lệ: MAC check failed (Authentication Tag không khớp)
>>> KẾT QUẢ: [PASSED] Chặn thành công tấn công sửa đổi bản mã.

-----------------------------------------------------------------
TEST CASE 03: Giải mã bằng Private Key không hợp lệ (Khóa của Eve)
[EVE] Thất bại: Giải mã RSA ra Session Key sai -> AES-GCM từ chối xác thực.
      Chi tiết ngoại lệ: MAC check failed (Sai khóa phiên dẫn đến kiểm thực thất bại)
>>> KẾT QUẢ: [PASSED] Từ chối truy cập trái phép khi sai khóa.
=================================================================
```

#import "../components.typ": info-box
#info-box(title: "Nhận xét kết quả kiểm thử")[
  Ba tình huống kiểm thử trên cho thấy mô hình kết hợp RSA và AES-GCM đáp ứng tính bí mật của nội dung thông điệp trên đường truyền, đồng thời phát hiện được các can thiệp làm sai lệch dữ liệu.
]
