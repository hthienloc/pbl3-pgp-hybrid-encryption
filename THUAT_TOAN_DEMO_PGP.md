# TÀI LIỆU GIẢI THÍCH CHI TIẾT THUẬT TOÁN VÀ TIẾN TRÌNH TÍNH TOÁN
## Ứng Dụng Mô Phỏng PGP Hybrid Encryption (RSA + AES-GCM)

---

## 1. Tổng Quan Kiến Trúc Mã Hóa Lai (Hybrid Cryptosystem)

Mô hình mã hóa lai trong ứng dụng kết hợp giữa **mật mã đối xứng (AES-128-GCM)** và **mật mã bất đối xứng (RSA-256)** nhằm giải quyết đồng thời hai bài toán:

1. **Hiệu năng xử lý dữ liệu lớn:** Thuật toán đối xứng AES mã hóa trực tiếp nội dung dữ liệu $M$ với tốc độ phần cứng cao.
2. **Phân phối khóa qua môi trường mở:** Thuật toán bất đối xứng RSA chỉ mã hóa duy nhất khóa phiên $K$ (16 bytes), cho phép chuyển giao khóa an toàn qua mạng mà không cần kênh bảo mật từ trước.

### Bảng so sánh đặc tính kỹ thuật giữa hai thuật toán trong hệ thống:

| Tiêu chí | AES-128-GCM (Đối xứng) | RSA-256 (Bất đối xứng) |
| :--- | :--- | :--- |
| **Không gian khóa** | 128-bit ($2^{128}$ tổ hợp) | Modulus 256-bit ($n \approx 2^{256}$) |
| **Cặp khóa sử dụng** | Một khóa phiên bí mật $K$ dùng chung | Cặp khóa công khai $(e, n)$ và bí mật $(d, n)$ |
| **Vai trò trong PGP** | Mã hóa khối dữ liệu $M$ và sinh mã chứng thực | Mã hóa và bảo vệ khóa phiên $K$ |
| **Độ phức tạp tính toán** | Thấp (chủ yếu là phép XOR, bảng tra S-box) | Cao (lũy thừa mô-đun trên số nguyên lớn) |
| **Tính chất toàn vẹn** | Tích hợp sẵn qua hàm băm GHASH | Cần cơ chế đệm an toàn hoặc chữ ký số |

---

## 2. Giải Thích Chi Tiết Từng Bước Tính Toán Số Học

Quy trình xử lý dữ liệu trên giao diện mô phỏng trải qua 7 bước nghiệp vụ tương ứng với luồng dữ liệu thời gian thực:

```
[Bản rõ M] 
   │
   ├─► (Bước 1: CSPRNG) ────────► [Khóa K (16B)] 
   │                                   │
   ├─► (Bước 2: AES-GCM) ◄─────────────┤
   │        │                          │
   │        ▼                          ▼
   │   [IV, C_data, Tag]        (Bước 3: RSA Enc) ◄── [Public Key Bob (e, n)]
   │        │                          │
   │        ▼                          ▼
   │   {C_data, IV, Tag}            [C_key]
   │        │                          │
   └────────┴──────────┬───────────────┘
                       ▼
            (Bước 4: TCP Packet)
                       │
       ════════════════╪════════════════ Kênh truyền mạng (Có thể bị tấn công sửa bit)
                       │
                       ▼
            [Gói tin nhận tại Bob]
                       │
                       ├─► [C_key] ──► (Bước 5: RSA Dec) ◄── [Private Key Bob (d, n)]
                       │                    │
                       │                    ▼
                       │               [Khôi phục K]
                       │                    │
                       └─► [C_data, Tag, IV]┤
                                            ▼
                               (Bước 6: GHASH Verify & AES Dec)
                                            │
                                            ▼
                                     [Bản rõ M' = M]
```

---

### Bước 0: Sinh cặp khóa RSA của Bob (RSA Key Generation)
- **Mục đích:** Khởi tạo danh tính mật mã cho bên nhận (Bob).
- **Các bước số học:**
  1. *Sinh số nguyên tố:* Thuật toán sinh ngẫu nhiên hai số nguyên tố lớn độc lập $p$ và $q$ (mỗi số 128-bit) bằng cách sử dụng kiểm tra nguyên tố xác suất **Miller-Rabin** (số vòng lặp $k = 40$).
  2. *Tính Modulus:* 
     $$n = p \times q \quad (\text{độ dài } \approx 256 \text{ bits})$$
  3. *Tính hàm phi Euler:*
     $$\phi(n) = (p - 1)(q - 1)$$
  4. *Chọn số mũ công khai $e$:* Cố định $e = 65537$ (số nguyên tố Fermat $F_4 = 2^{16} + 1$).
     - *Lý do:* Dạng nhị phân của $e$ là $10000000000000001_2$ (chỉ có đúng 2 bit 1). Phép lũy thừa mô-đun chỉ mất 16 phép bình phương và 1 phép nhân.
  5. *Tính số mũ bí mật $d$:* Sử dụng **thuật toán Euclid mở rộng** tìm phần tử nghịch đảo nhân của $e$ theo mô-đun $\phi(n)$:
     $$e \times d \equiv 1 \pmod{\phi(n)}$$
- **Kết quả:** Bob công khai cặp Public Key $(e, n)$ cho Alice và giữ bí mật Private Key $(d, n)$.

---

### Bước 1: Alice sinh khóa phiên ngẫu nhiên $K$ (Session Key Generation)
- **Mục đích:** Tạo khóa bí mật tạm thời dùng một lần (ephemeral key) để mã hóa dữ liệu.
- **Cơ chế tính toán:**
  - Gọi hàm `os.urandom(16)` để lấy 16 bytes (128 bits) dữ liệu ngẫu nhiên từ bộ sinh số ngẫu nhiên an toàn của hệ điều hành (CSPRNG - `/dev/urandom`).
  - Chuỗi nhị phân: $K \in \{0, 1\}^{128}$.
  - Chuyển đổi sang số nguyên lớn hệ thập phân để phục vụ tính toán RSA:
    $$m_K = \sum_{i=0}^{15} K[i] \times 256^{15 - i}$$
  - Đảm bảo điều kiện biên: $m_K < 2^{128} < n \approx 2^{256}$.

---

### Bước 2: Alice mã hóa dữ liệu qua AES-GCM (Authenticated Encryption)
- **Mục đích:** Bảo vệ tính bí mật và tính toàn vẹn của bản rõ $M$.
- **Cơ chế tính toán:**
  1. *Sinh vector khởi tạo (IV / Nonce):* Sinh chuỗi ngẫu nhiên 12 bytes (96 bits) bằng CSPRNG. Vector này bảo đảm nếu gửi cùng một bản rõ $M$ nhiều lần, chuỗi bản mã thu được vẫn hoàn toàn khác biệt.
  2. *Mã hóa dòng CTR Mode (Counter Mode):*
     - Ghép Counter Block ban đầu: $\text{CB}_1 = \text{IV} \,\|\, 00000002_{16}$.
     - Bản rõ $M$ được chia thành các khối 16 bytes $P_1, P_2, \dots, P_m$.
     - Bản mã $C_i$ được tính bằng phép cộng XOR bitwise với dòng khóa sinh bởi AES:
       $$C_i = P_i \oplus \text{AES}_K(\text{CB}_i)$$
  3. *Sinh thẻ chứng thực toàn vẹn bằng hàm băm GHASH:*
     - Tính khóa băm: $H = \text{AES}_K(0^{128})$.
     - Thực hiện nhân đa thức lặp Horner trên trường hữu hạn Galois $GF(2^{128})$ theo đa thức nguyên thủy $f(x) = x^{128} + x^7 + x^2 + x + 1$:
       $$X_1 = C_1 \cdot H$$
       $$X_i = (X_{i-1} \oplus C_i) \cdot H$$
     - Tính Authentication Tag cuối cùng:
       $$\text{Tag} = (X_m \oplus \text{len}(A) \,\|\, \text{len}(C)) \cdot H \oplus \text{AES}_K(\text{CB}_0)$$
       với $\text{CB}_0 = \text{IV} \,\|\, 00000001_{16}$.

---

### Bước 3: Alice dùng RSA Bob mã hóa khóa phiên $K$
- **Mục đích:** Bảo vệ khóa $K$ khi truyền qua mạng công khai.
- **Cơ chế tính toán:**
  - Nạp số nguyên $m_K$ và cặp Public Key $(e, n)$ của Bob.
  - Áp dụng thuật toán **Square-and-Multiply (Bình phương và nhân liên tiếp)** để tính giá trị lũy thừa mô-đun:
    $$C_{\text{key}} = (m_K)^e \pmod n$$
  - Biểu diễn $e = 65537$ dạng nhị phân: chuỗi bit $b_{16} b_{15} \dots b_0 = 10000000000000001_2$.
  - Biến chạy $A$ khởi tạo bằng 1. Với mỗi bit:
    - Luôn thực hiện: $A \leftarrow (A^2) \pmod n$.
    - Nếu bit bằng 1: $A \leftarrow (A \times m_K) \pmod n$.
  - Kết quả $C_{\text{key}}$ là số nguyên lớn 256-bit được xuất dưới dạng mã Hex.

---

### Bước 4: Đóng gói khung truyền thông mạng (Packet Framing)
- **Mục đích:** Chuẩn hóa dữ liệu theo giao thức mạng để bên nhận phân tích cú pháp (parse).
- **Cấu trúc gói tin JSON Envelope:**
  ```json
  {
    "C_key": "0x4b7f8e...",
    "IV": "3d5f2a1b9c8e...",
    "C_data": "7a8b9c...",
    "Tag": "f1e2d3..."
  }
  ```
- **Cơ chế truyền qua TCP Socket:**
  - Đóng khung tiền tố độ dài (Length-Prefixed Framing):
    $$\text{Frame} = [\text{4 Bytes độ dài Payload (Big-endian)}] + [\text{Payload chuỗi JSON UTF-8}]$$
  - Cơ chế này giúp bộ nhận của Bob đọc chính xác số lượng bytes cần thiết của một gói, xử lý triệt để hiện tượng phân mảnh dữ liệu (TCP Stream Fragmentation).

---

### Bước 5: Bob giải mã RSA để khôi phục khóa phiên $K$
- **Mục đích:** Lấy lại khóa đối xứng $K$ từ trường $C_{\text{key}}$.
- **Cơ chế số học:**
  - Bob sử dụng khóa bí mật $d$ của mình để tính:
    $$m_K' = (C_{\text{key}})^d \pmod n$$
  - **Chứng minh tính đúng đắn dựa trên Định lý Euler:**
    - Do $e \cdot d \equiv 1 \pmod{\phi(n)}$, tồn tại số nguyên $k$ sao cho $e \cdot d = 1 + k \cdot \phi(n)$.
    - Thế vào biểu thức giải mã:
      $$m_K' \equiv (m_K^e)^d \equiv m_K^{e \cdot d} \equiv m_K^{1 + k \cdot \phi(n)} \pmod n$$
      $$m_K' \equiv m_K \times (m_K^{\phi(n)})^k \pmod n$$
    - Theo Định lý Euler, nếu $\gcd(m_K, n) = 1$ thì $m_K^{\phi(n)} \equiv 1 \pmod n$:
      $$m_K' \equiv m_K \times (1)^k \equiv m_K \pmod n$$
  - Chuyển số nguyên $m_K'$ thu được về đúng 16 bytes nhị phân của Session Key $K$.

---

### Bước 6: Bob xác thực GHASH và giải mã bản rõ AES-GCM
- **Mục đích:** Kiểm tra dữ liệu có bị kẻ tấn công sửa đổi trên đường truyền không, và khôi phục bản rõ $M$.
- **Cơ chế kiểm soát 2 tầng:**
  1. *Tầng 1 - Xác thực toàn vẹn (Integrity Check):*
     - Bộ giải mã dùng khóa $K$ vừa khôi phục và dữ liệu $C_{\text{data}}$ nhận được để tính toán lại mã kiểm tra $\text{Tag}_{\text{computed}}$ bằng hàm băm GHASH.
     - So sánh:
       $$\text{Tag}_{\text{computed}} \stackrel{?}{=} \text{Tag}_{\text{received}}$$
     - **Tình huống bình thường:** Hai thẻ trùng khớp $\rightarrow$ Dữ liệu nguyên vẹn 100%, chuyển sang bước giải mã.
     - **Tình huống bị tấn công (khi bấm nút "Sửa Bit"):** Kẻ tấn công đảo 1 bit trong $C_{\text{data}}$ ($C_0 \leftarrow C_0 \oplus \text{0xFF}$). Phép nhân Horner trên trường Galois $GF(2^{128})$ lập tức khuếch tán sự thay đổi ra toàn bộ giá trị băm khiến:
       $$\text{Tag}_{\text{computed}} \neq \text{Tag}_{\text{received}}$$
       Thư viện kích hoạt ngoại lệ `ValueError: MAC check failed`. Gói tin bị hủy bỏ ngay lập tức, bộ giải mã từ chối xuất dữ liệu ra ngoài, bảo vệ an toàn cho hệ thống.
  2. *Tầng 2 - Giải mã Counter Mode:*
     - Khi kiểm tra tính toàn vẹn thành công, bản rõ được tái tạo bằng cách XOR ngược lại:
       $$P_i = C_i \oplus \text{AES}_K(\text{CB}_i)$$
     - Ghép các khối $P_i$ và chuyển đổi UTF-8 thu lại chuỗi ban đầu: `"Xin chào Cô Hạnh, bọn em là nhóm 7"`.

---

## 3. Ý Nghĩa Của Sơ Đồ Khối Và Bảng Console Dưới Cùng

1. **Sơ đồ 8 khối trực quan:**
   - Thể hiện sự chuyển dịch của dòng dữ liệu từ dạng rõ $\rightarrow$ khóa đối xứng $\rightarrow$ khối mã hóa $\rightarrow$ gói tin mạng $\rightarrow$ giải mã khôi phục.
   - Trạng thái màu sắc phản ánh tức thời:
     - **Vàng:** Khối đang thực hiện phép tính toán số học.
     - **Xanh lá:** Khối đã hoàn tất và dữ liệu hợp lệ.
     - **Đỏ:** Phát hiện hành vi can thiệp dữ liệu trên đường truyền (Test case tấn công).
2. **Bảng Console dán đáy (Fixed Resizable Terminal):**
   - Lưu trữ vết (trace log) 20 bước tính toán chi tiết nhất của hệ thống.
   - Hiển thị từng phép biến đổi: giá trị byte entropy, giá trị số nguyên nhị phân của số mũ $e$, công thức Euler áp dụng và kết quả so sánh Tag.
   - Thanh kéo phía trên cho phép người thuyết trình điều chỉnh độ cao linh hoạt để trình bày trực tiếp các phép tính toán số học cho hội đồng mà không cần mở mã nguồn.
