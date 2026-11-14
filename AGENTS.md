# AGENTS.md — Hướng dẫn làm việc với dự án PBL3 (PGP Hybrid Encryption)

## 1. Cấu trúc thư mục

- `main.typ`: File gốc tổng hợp trang bìa, mục lục, các chương và tài liệu tham khảo.
- `template.typ`, `styles.typ`, `components.typ`: Cấu hình bố cục, bảng (`report-table`), hộp thông tin (`info-box`) và định dạng trích dẫn IEEE chuẩn (ngang hàng văn bản `[1]`, không dùng superscript).
- `figures.typ`: Chứa toàn bộ 5 sơ đồ vector (`fig-hybrid-overview`, `fig-sequence-interaction`, `fig-packet-layout`, `fig-rsa-numeric-example`, `fig-socket-sequence`). Không chèn ảnh PNG rời.
- `sections/`: Nội dung báo cáo tách theo chương:
  - `00_abstract.typ` (Tóm tắt & Từ khóa)
  - `01_introduction.typ` – `05_conclusion.typ` (Chương 1–5)
  - `06_appendix.typ` (Phụ lục A, B, C)
- `references.bib`: Nguồn tài liệu tham khảo BibTeX theo chuẩn IEEE.
- `algorithms/`: Lõi thuật toán dùng chung (`euclid.py`, `rsa.py`, `aes_gcm.py`, `hybrid_pgp.py`).
- `PGP_RSA_AES_Socket_3_files/`: Chương trình Client–Server TCP qua mạng LAN (`server_bob.py`, `client_alice.py`, `pgp_crypto.py`).
- `src/`: Kịch bản demo CLI (`hybrid_demo.py`, `rsa.py`) và Web Simulator (`gui_nicegui.py`).

## 2. Quy tắc biên soạn tài liệu (Typst)

- **Nguồn duy nhất cho báo cáo:** Chỉ chỉnh sửa trực tiếp các file `.typ`. Không tạo hay commit các bản báo cáo song song dạng `.md`, `.docx`, `.html` hoặc script sinh báo cáo rời.
- **Biên dịch kiểm tra:** Sau mọi chỉnh sửa tài liệu, bắt buộc chạy lệnh sau và đảm bảo thoát với mã `0`, không có cảnh báo thiếu nhãn/trích dẫn:
  ```bash
  typst compile main.typ report.pdf
  ```
- **Tham chiếu chéo & Trích dẫn:**
  - Luôn dùng nhãn Typst `@fig-...` và `@tbl-...` thay vì gõ cứng `"Hình 1"`, `"Bảng 2"`.
  - Luôn trích dẫn từ `references.bib` bằng `@key` (ví dụ `@nist_sp800_38d`). Không tự sửa kiểu `show cite` thành chỉ số trên.
  - Mọi mục trong `references.bib` phải được trích dẫn ít nhất một lần trong báo cáo; xóa các mục thừa nếu không dùng.

## 3. Văn phong & Thuật ngữ nhất quán

- **Giọng văn học thuật tự nhiên:** Viết trực tiếp, súc tích, đúng ngữ cảnh đồ án sinh viên kỹ thuật. Tránh văn phong kiểu AI:
  - Không lặp lại các từ sáo rỗng (*"then chốt"*, *"cốt lõi"*, *"triệt để"*, *"tuyệt đối"*, *"hoàn hảo"*, *"vượt trội"*, *"tức thời"*, *"giải quyết bài toán..."*).
  - Không lạm dụng cấu trúc liệt kê `*Cụm in đậm:* câu giải thích...` đồng loạt ở mọi mục hoặc chia đối xứng 3 vế máy móc ở phần kết luận.
  - Hạn chế ngắt câu bằng dấu gạch ngang dài (`–`).
- **Thống nhất thuật ngữ:**
  - Dùng tiếng Việt cho các khái niệm đã giới thiệu ở lần đầu: *khóa công khai* (`Public Key`), *khóa bí mật* (`Private Key`), *khóa phiên* (`Session Key`), *bản rõ* (`M`), *bản mã* (`C_data`, `C_key`).
  - Dùng đúng ký hiệu toán học thống nhất: $M$ (bản rõ), $K$ (khóa phiên 128-bit), $n = p dot q$, $\phi(n) = (p - 1)(q - 1)$, $e = 65537$.

## 4. Đồng bộ giữa Báo cáo và Mã nguồn

Mọi số liệu, tên hàm, cấu trúc gói tin và đoạn mã trong báo cáo (đặc biệt ở Chương 3, Chương 4 và `06_appendix.typ`) phải khớp 100% với mã nguồn thực tế:
- **RSA:** `algorithms/rsa.py` dùng `is_prime(n, k=20)` và mặc định `bits=256`; riêng `PGP_RSA_AES_Socket_3_files/server_bob.py` dùng `bits=512`.
- **AES-GCM (NIST SP 800-38D):** Với Nonce 96-bit, khối đếm ban đầu là $J_0 = \text{CB}_0 = \text{Nonce} \parallel \text{00000001}_{16}$ (dùng cho Tag), còn mã hóa CTR bắt đầu từ $\text{CB}_1 = \text{inc}_{32}(\text{CB}_0)$. Đa thức trên $\text{GF}(2^{128})$ là đa thức bất khả quy $f(x) = x^{128} + x^7 + x^2 + x + 1$.
- **Gói tin JSON & Framing:** Tiền tố 4 byte Big-Endian (`!I`) + JSON UTF-8 với 4 trường mật mã `enc_session_key`, `nonce`, `ciphertext`, `auth_tag` (mã hóa Base64 ở Socket, byte/hex ở `algorithms/hybrid_pgp.py`).
- **Nhật ký thực nghiệm:** Chỉ đưa vào báo cáo kết quả chạy thực tế từ `python3 src/hybrid_demo.py` hoặc chạy thực nghiệm thật; không tự bịa số liệu hoặc chuỗi log.
