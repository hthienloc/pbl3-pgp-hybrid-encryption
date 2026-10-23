= Demo chương trình và kết quả kiểm thử

Để đánh giá toàn diện tính đúng đắn, khả năng chống can thiệp và xử lý lỗi của chương trình Python, nhóm đã thiết lập 3 kịch bản kiểm thử trọng tâm:

#align(center)[
  #table(
    columns: (auto, 1.2fr, 1.8fr),
    fill: (x, y) => if y == 0 { rgb("#e0e7ff") } else if calc.even(y) { rgb("#f8fafc") } else { none },
    stroke: 0.5pt + rgb("#cbd5e1"),
    inset: 8pt,
    [*Kiểm thử*], [*Kịch bản thử nghiệm*], [*Kết quả quan sát & Phân tích*],
    [*Test 01*], [Bob sử dụng đúng Private Key tương ứng với Public Key của mình.], [Khôi phục thành công 100% nội dung thông điệp gốc ban đầu. Quy trình giải mã khóa phiên và giải mã dữ liệu diễn ra chính xác.],
    [*Test 02*], [Kẻ tấn công (Man-in-the-Middle) can thiệp, sửa đổi một phần bản mã trước khi Bob giải mã.], [Phát hiện can thiệp: Chương trình cảnh báo lỗi xác thực tính toàn vẹn (Authentication Tag không khớp) trong chế độ AES-GCM.],
    [*Test 03*], [Giải mã bằng một Private Key không khớp (khóa của người khác hoặc khóa sai số học).], [Thất bại: Phép tính RSA cho ra giá trị Session Key sai lệch, quá trình giải mã AES bị từ chối hoặc ném ngoại lệ.]
  )
]

== Minh chứng thực nghiệm
- Khi báo cáo, chạy trực tiếp cả 3 kịch bản kiểm thử trong terminal Python.
- Trình chiếu nhật ký log chi tiết từng bước: từ bản rõ ban đầu, bản mã sinh ra, dạng biểu diễn nhị phân/hex của khóa phiên, đến kết quả bắt ngoại lệ khi dữ liệu bị sửa đổi.
- Lưu ý không kết luận rằng mọi chế độ AES đều tự động phát hiện được sửa đổi; cần chỉ rõ cơ chế xác thực toàn vẹn chỉ có khi sử dụng chế độ Authenticated Encryption (như AES-GCM) hoặc gắn kèm HMAC (đối với AES-CBC).
