= Demo chương trình và kết quả kiểm thử

Để đánh giá toàn diện tính đúng đắn, khả năng chống can thiệp và xử lý lỗi của chương trình Python (`src/hybrid_demo.py`), nhóm đã thiết lập 3 kịch bản kiểm thử trọng tâm:

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

== Minh chứng thực nghiệm trên terminal

Dưới đây là nhật ký xuất trực tiếp từ terminal khi thực thi chương trình `python3 src/hybrid_demo.py`:

```text
=================================================================
DEMO PGP HYBRID ENCRYPTION (RSA + AES-GCM)
=================================================================

[ALICE] Thông điệp gốc: "Báo cáo tiến độ Nhóm 7: PGP Hybrid Encryption hoạt động chính xác!"
[ALICE] Mã hóa hoàn tất:
  + Encrypted Session Key (RSA) : 2843
  + Nonce (AES-GCM)              : 48241c998fc06ff8e676cbb77d3ba152
  + Ciphertext (AES)            : e33b37b786e44a47b86fd935c285367ae60ccea3... (81 bytes)
  + Authentication Tag          : f36635e20b731180628dcfd7aaceab49

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
[EVE] Thất bại: Không giải mã được Session Key và bản mã.
      Chi tiết ngoại lệ: MAC check failed (Sai Session Key dẫn đến xác thực thất bại)
>>> KẾT QUẢ: [PASSED] Từ chối truy cập trái phép khi sai khóa.
=================================================================
```

#import "../components.typ": info-box
#info-box(title: "Nhận xét kết quả kiểm thử")[
  Ba tình huống kiểm thử trên cho thấy mô hình kết hợp RSA và AES-GCM đáp ứng tính bí mật của nội dung thông điệp trên đường truyền, đồng thời phát hiện được các can thiệp làm sai lệch dữ liệu.
]
