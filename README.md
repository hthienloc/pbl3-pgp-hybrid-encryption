# PBL3: PGP – Hybrid Encryption (RSA & AES)

Báo cáo tiến độ và mã nguồn mô phỏng cơ chế **Mã hóa lai (Hybrid Encryption)** kết hợp giữa thuật toán **RSA** và **AES** theo nguyên lý của chuẩn **PGP/OpenPGP** (RFC 4880, RFC 9580).

> **Học phần:** PBL3: Mạng máy tính  
> **Đơn vị:** Khoa Điện tử và Trí tuệ Nhân tạo – Trường Đại học Bách Khoa, Đại học Đà Nẵng  
> **Giảng viên hướng dẫn:** TS. Trần Thị Minh Hạnh  
> **Nhóm thực hiện (Nhóm 7):**
> - Vũ Duy Dương (106230007)
> - Huỳnh Thiện Lộc (106230052)
> - Phan Vinh Sơn (106230059)

---

## 📌 Giới thiệu đề tài

Trong môi trường truyền thông mạng, việc truyền tải dữ liệu an toàn đòi hỏi đảm bảo đồng thời tính bí mật, toàn vẹn và xác thực.
- **AES (Advanced Encryption Standard):** Hệ mật đối xứng với tốc độ xử lý phần cứng cực cao, tối ưu cho dữ liệu dung lượng lớn nhưng gặp khó khăn trong việc phân phối khóa qua kênh mạng mở.
- **RSA (Rivest–Shamir–Adleman):** Hệ mật bất đối xứng giải quyết triệt để bài toán phân phối khóa bằng cặp khóa công khai / khóa bí mật (Public/Private Key), tuy nhiên chi phí tính toán lũy thừa số học mô-đun lớn gây nghẽn hiệu năng khi mã hóa trực tiếp dữ liệu dài.

**Giải pháp mã hóa lai (Hybrid Encryption):**
1. Người gửi (Alice) sinh ngẫu nhiên một khóa đối xứng dùng một lần (**Session Key**).
2. Dữ liệu thông điệp được mã hóa tốc độ cao bằng **AES** sử dụng Session Key.
3. Session Key được bảo vệ an toàn bằng cách mã hóa qua **RSA** với Public Key của người nhận (Bob).
4. Người nhận (Bob) dùng Private Key của mình để giải mã lấy lại Session Key, sau đó giải mã bản tin AES.

---

## 📂 Cấu trúc thư mục

```text
.
├── README.md               # Tài liệu tổng quan dự án
├── report.pdf              # Bản xuất PDF báo cáo tiến độ hoàn chỉnh
├── main.typ                # Điểm vào chính của tài liệu báo cáo Typst
├── template.typ            # Cấu hình template, layout và trang bìa
├── components.typ          # Các components hộp ghi chú, callout tái sử dụng
├── sections/               # Các chương/mục được module hóa
│   ├── 00_glossary.typ     # Danh mục thuật ngữ và viết tắt
│   ├── 01_introduction.typ # Giới thiệu, bối cảnh, mục tiêu & phạm vi (kèm sơ đồ Fletcher)
│   ├── 02_hybrid_concept.typ# So sánh AES vs RSA & Lý do kết hợp
│   ├── 03_process.typ      # Quy trình gửi (Alice) - nhận (Bob)
│   ├── 04_rsa_keygen.typ   # Quá trình tạo khóa số học RSA
│   ├── 05_rsa_implementation.typ # Cài đặt thuật toán RSA bằng Python thuần
│   ├── 06_rsa_example.typ  # Ví dụ minh họa mã hóa/giải mã số học
│   ├── 07_integration.typ  # Tích hợp khóa phiên RSA & AES
│   ├── 08_testing.typ      # Kịch bản kiểm thử (3 test cases)
│   ├── 09_conclusion.typ   # Kết quả & Hướng phát triển
│   └── 10_qa.typ           # Bộ câu hỏi phản biện & thảo luận
└── src/
    └── rsa.py              # Mã nguồn thuật toán RSA thuần Python (Textbook RSA)
```

---

## 🚀 Hướng dẫn biên dịch và chạy thử

### 1. Biên dịch tài liệu Typst
Yêu cầu đã cài đặt [Typst](https://typst.app/):

```bash
# Biên dịch ra file PDF một lần
typst compile main.typ report.pdf

# Hoặc bật chế độ Hot Reload tự động cập nhật khi chỉnh sửa
typst watch main.typ report.pdf
```

### 2. Chạy thử thuật toán RSA (Python)
Mã nguồn độc lập, không cần cài đặt thư viện bên thứ ba:

```bash
python3 src/rsa.py
```

Kết quả thực nghiệm:
```text
Public Key (e, n): (17, 3233)
Private Key (d, n): (2753, 3233)
Thông điệp gốc: 125
Bản mã sau khi mã hóa: 1516
Bản rõ sau khi giải mã: 125
Kiểm thử thành công: Dữ liệu được khôi phục chính xác 100%!
```

---

## 📜 Giấy phép
Dự án phục vụ mục đích học tập và nghiên cứu trong khuôn khổ môn học PBL3: Mạng máy tính.
