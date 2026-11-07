# CẨM NANG TOÀN DIỆN VÀ KỊCH BẢN BÁO CÁO ĐỒ ÁN PBL3 (MẠNG MÁY TÍNH)
**Đề tài:** Nghiên cứu nguyên lý RSA và xây dựng mô hình mã hóa lai PGP kết hợp RSA – AES  
**Giảng viên hướng dẫn:** TS. Trần Thị Minh Hạnh  
**Sinh viên thực hiện (Nhóm 7):** Vũ Duy Dương, Huỳnh Thiện Lộc, Phan Vinh Sơn  
**Tài liệu tham chiếu:** [Báo cáo tiến độ hoàn chỉnh (`report.pdf`)](file:///home/loccun/Documents/Năm%204%20-%20Kì%201/PBL3%20-%20Mạng%20máy%20tính/Report/report.pdf)

---

## MỤC LỤC TÀI LIỆU
1. **Bức tranh tổng quan của Đồ án (Cheat Sheet cho Sinh viên)**
2. **Kịch bản nói chi tiết từng phần (Bám sát phản biện của GVHD)**
3. **Cơ sở Toán học & Bản chất Thuật toán (Giải thích cặn kẽ)**
4. **Kiến trúc mạng TCP Socket & Các giải pháp kỹ thuật cốt lõi**
5. **Bộ câu hỏi phản biện chuyên sâu và cách trả lời lấy điểm tuyệt đối**

---

# PHẦN 1: BỨC TRANH TỔNG QUAN (CHEAT SHEET CHO SINH VIÊN)

Trước khi lên gặp cô, bạn cần nắm chắc 4 câu trả lời "xương sống" này:

1. **Đề tài giải quyết vấn đề gì?**  
   Giải quyết bài toán đánh đổi trong truyền thông bảo mật mạng: **AES rất nhanh** nhưng không thể tự gửi khóa bí mật qua kênh mạng mở; **RSA giải quyết được việc chia sẻ khóa** bằng cặp Public/Private Key nhưng tính toán lũy thừa modulo trên số lớn quá nặng, không thể mã hóa trực tiếp thông điệp dài. Do đó phải dùng **mã hóa lai (Hybrid)**: dùng AES mã hóa dữ liệu, dùng RSA mã hóa khóa AES.
2. **Tại sao lại dùng AES-GCM mà không phải AES-CBC thông thường?**  
   AES-CBC chỉ có tính bí mật (Confidentiality). Muốn toàn vẹn phải ghép thêm HMAC (mô hình Encrypt-then-MAC rất dễ sai sót). Trong khi đó, **AES-GCM là chuẩn mã hóa xác thực AEAD** (Authenticated Encryption with Associated Data), vừa mã hóa vừa tự sinh **Authentication Tag (16B)** bằng hàm băm GHASH để phát hiện ngay lập tức nếu bản mã bị sửa dù chỉ 1 bit trên đường truyền.
3. **Tại sao có bước "Xác thực ngoại vi" (Out-of-band)?**  
   Khi Alice hỏi lấy Public Key qua Socket TCP, kênh TCP chưa có chứng chỉ số CA nên có thể bị kẻ tấn công đứng giữa (Man-in-the-Middle) tráo khóa. Hai bên bắt buộc phải dùng kênh phụ bên ngoài (nhìn màn hình, điện thoại) để **đối chiếu Fingerprint SHA-256** của khóa công khai.
4. **Đóng gói tin qua TCP như thế nào?**  
   TCP là byte stream (dòng byte liên tục, không có ranh giới gói). Nhóm dùng kỹ thuật **Length-prefixed framing (4 byte Big-Endian)** ở đầu mỗi gói tin để bên nhận biết chính xác kích thước gói mà đọc trọn vẹn, không bị lỗi dính gói hoặc chia cắt gói.

---

# PHẦN 2: KỊCH BẢN TRÌNH BÀY CHI TIẾT (10 – 12 PHÚT)

### 1. Mở đầu: Báo cáo tiếp thu ý kiến buổi trước (~1.5 phút)
> *"Em chào cô ạ. Ở buổi làm việc trước, cô có yêu cầu nhóm 2 nội dung chính để hoàn thiện đồ án:*
> 1. *Vẽ lại toàn bộ hệ thống sơ đồ kỹ thuật cho chuẩn mực, làm rõ vị trí byte và chức năng của từng tham số.*
> 2. *Hiện thực hóa bài toán từ việc chạy cục bộ sang môi trường mạng thực tế bằng bản Demo truyền thông qua Socket TCP giữa 2 máy.*
>
> *Hôm nay, nhóm em xin phép trình bày toàn bộ tiến độ và kết quả mà nhóm đã đạt được từ trước đến nay, bám sát các góp ý của cô ạ."*

---

### 2. Tổng quan bài toán & Lý do chọn mô hình PGP Hybrid (~2 phút)
*(Chỉ vào Báo cáo: Mục 2 & Mục 3)*

> *"Thưa cô, trong mạng máy tính, bài toán bảo mật đòi hỏi 3 yếu tố: **Tính bí mật**, **Tính toàn vẹn** và **Tính xác thực**.
> - Mã hóa đối xứng **AES** có ưu thế tốc độ xử lý phần cực nhanh, nhưng nhược điểm lớn nhất là: **Làm sao Alice và Bob thỏa thuận được khóa phiên bí mật khi kênh truyền mở?**
> - Mã hóa bất đối xứng **RSA** giải quyết việc trao đổi khóa nhờ Public Key, nhưng tốc độ chậm gấp hàng trăm lần do chi phí tính toán số học trên số nguyên lớn.
> 
> Chuẩn **OpenPGP** giải quyết sự đánh đổi này bằng cơ chế mã hóa lai:
> - Dữ liệu bản rõ $M$ được mã hóa bằng AES với một khóa phiên ngẫu nhiên $K$ (Session Key 128-bit).
> - Khóa phiên $K$ lại được mã hóa bằng khóa công khai RSA của Bob ($e_B, n$).
> - Gói tin truyền đi là sự kết hợp: $\{ \text{Khóa phiên đã mã hóa}, \text{Dữ liệu đã mã hóa} \}$. Nhờ đó tốc độ vẫn tối ưu như AES mà kênh truyền khóa vẫn an toàn như RSA."*

---

### 3. Sơ đồ tuần tự và Cấu trúc khung gói tin (Đã vẽ lại) (~3 phút)
*(Chuyển tới Hình 2 và Hình 4 trong báo cáo)*

> *"Để khắc phục sơ đồ cũ còn thiếu chi tiết, nhóm đã chuẩn hóa lại hai sơ đồ kỹ thuật quan trọng:*
>
> ***Thứ nhất là Hình 2 - Sơ đồ tuần tự tương tác Alice - Bob:***
> *Sơ đồ này làm rõ cả 4 thành phần thực tế của gói tin:*
> 1. *Bob sinh cặp khóa RSA $(e_B, n)$ và $(d_B, n)$, sau đó công khai $(e_B, n)$.*
> 2. *Alice sinh khóa phiên $K$ 128-bit và vector khởi tạo **IV (12 bytes)** cho AES-GCM.*
> 3. *Alice mã hóa dữ liệu: $(C_{\text{data}}, \text{Tag}) = \text{AES}_K(M, \text{IV})$, trong đó **Tag 16 bytes** là mã kiểm thực toàn vẹn GHASH.*
> 4. *Alice mã hóa khóa phiên: $C_{\text{key}} = K^{e_B} \pmod n$.*
> 5. *Gói tin PGP gồm 4 thành phần `{C_key, IV, C_data, Tag}` được chuyển qua mạng.*
> 6. *Bob nhận gói: Dùng Private Key $(d_B, n)$ giải mã $C_{\text{key}}$ lấy lại $K$. Sau đó đối chiếu **Tag** để kiểm tra dữ liệu có bị kẻ gian sửa đổi không; nếu hợp lệ mới dùng $K$ và IV giải mã lấy lại thông điệp gốc $M$.*
>
> ***Thứ hai là Hình 4 - Cấu trúc khung gói tin (Packet Framing & Offset):***
> *Nhóm đã thiết kế lại thành sơ đồ luồng byte stream liên tục:*
> - *`Offset 0 .. 255 (256 bytes)`: Khóa phiên mã hóa RSA ($C_{\text{key}}$).*
> - *`Offset 256 .. 267 (12 bytes)`: Nonce/IV của AES-GCM.*
> - *`Offset 268 .. 268+L-1`: Dữ liệu bản mã $C_{\text{data}}$.*
> - *`16 bytes cuối`: Authentication Tag.*
> *Sơ đồ ánh xạ trực tiếp từng vị trí byte vào 4 hàm phân tích cú pháp ở bộ nhận của Bob: `rsa_decrypt()`, `AES.new()`, `decrypt()` và `verify()`."*

---

### 4. Thuật toán tự cài đặt & Kết quả kiểm nghiệm Terminal (~2.5 phút)
*(Chỉ vào Mục 5, 6, 7 & 9)*

> *"Về phần triển khai thuật toán:*
> - *Nhóm **tự lập trình hoàn toàn thuật toán số học RSA bằng Python thuần** trong thư mục `algorithms/`: tự viết giải thuật **Euclid mở rộng** để tìm số nghịch đảo modulo $d = e^{-1} \pmod{\phi(n)}$, và tích hợp thuật toán kiểm tra số nguyên tố xác suất **Miller–Rabin** để sinh khóa động an toàn.*
> - *Đồng thời nhóm tích hợp thư viện chuẩn công nghiệp cho AES-GCM để đảm bảo tính an toàn mật mã thực tế.*
>
> *Nhóm đã chạy kiểm thử 3 kịch bản thực nghiệm:*
> - *Kịch bản 1: Bob dùng đúng khóa $\rightarrow$ Khôi phục chính xác 100% bản rõ ban đầu.*
> - *Kịch bản 2: Giả lập kẻ tấn công đứng giữa sửa 1 byte trong Ciphertext $\rightarrow$ Hàm `verify()` của Bob lập tức báo lỗi `MAC check failed` và hủy gói tin, chứng minh cơ chế toàn vẹn hoạt động hoàn hảo.*
> - *Kịch bản 3: Kẻ thứ ba (Eve) cố dùng khóa riêng của mình để giải mã $\rightarrow$ Hệ thống từ chối xác thực vì giải mã ra sai khóa phiên $K$."*

---

### 5. Hiện thực hóa Demo qua Socket TCP giữa 2 máy (Mục 10) (~2.5 phút)
*(Chiếu Mục 10 và mở terminal nếu có demo trực tiếp)*

> *"Đáp ứng đúng yêu cầu của cô về việc đưa lên mạng TCP, nhóm đã phát triển thành công bộ demo trong thư mục `PGP_RSA_AES_Socket_3_files/`:*
> - *Gồm `server_bob.py` (lắng nghe tại cổng 5000), `client_alice.py` (kết nối qua IP LAN) và `pgp_crypto.py` (xử lý chuyển đổi giao thức).*
> - *Chương trình áp dụng **Length-prefixed framing (4 bytes)** ở đầu mỗi gói tin để giải quyết triệt để bài toán phân mảnh/dính gói của giao thức TCP byte stream.*
> - *Đặc biệt, nhóm đã giải quyết bài toán tấn công giả mạo Man-in-the-Middle khi truyền khóa công khai lần đầu bằng cơ chế **Xác thực ngoại vi (Out-of-band)**: Cả 2 máy tự tính và in ra chuỗi **Fingerprint SHA-256** của khóa. Người dùng đối chiếu chuỗi này qua kênh ngoài trước khi cho phép truyền tin mã hóa.*
> - *Chương trình đã được kiểm thử truyền thành công giữa 2 máy tính độc lập trong mạng LAN với đầy đủ nhật ký trao đổi gói tin."*

---

### 6. Kết luận & Hướng phát triển giai đoạn tiếp theo (~1 phút)
*(Chỉ vào Mục 11)*

> *"Thưa cô, tổng kết lại, nhóm đã nắm vững toàn bộ lý thuyết nền tảng, hoàn thiện bộ mã nguồn giải thuật số học và xây dựng thành công bản demo PGP Hybrid chạy ổn định trên socket mạng TCP.*
> 
> *Trong giai đoạn tới trước khi nghiệm thu, nhóm sẽ triển khai tiếp 3 hướng:*
> 1. *Tích hợp thêm module **Chữ ký số (Digital Signature)** kết hợp RSA và SHA-256 để đảm bảo tính chống chối bỏ (Non-repudiation).*
> 2. *Thử nghiệm đóng gói truyền nhận **tệp tin lớn** (ảnh, PDF nhị phân).*
> 3. *Xây dựng kịch bản **Benchmark đo đạc định lượng** so sánh thời gian thực thi giữa RSA thuần và Hybrid Encryption.*
>
> *Nhóm xin cảm ơn cô và rất mong nhận được những góp ý của cô để hoàn thiện đồ án ạ!"*

---

# PHẦN 3: CƠ SỞ TOÁN HỌC & BẢN CHẤT KỸ THUẬT CẦN NHỚ

Nếu cô hỏi sâu vào bảng hay vào công thức, đây là những kiến thức bạn phải nắm nằm lòng:

### 1. Thuật toán RSA (Số học thuần)
1. **Chọn 2 số nguyên tố lớn** $p$ và $q$ (trong code dùng Miller–Rabin để sinh ngẫu nhiên).
2. **Tính Modulus:** $n = p \times q$.
3. **Tính hàm phi Euler:** $\phi(n) = (p-1)(q-1)$.
4. **Chọn số mũ công khai $e$:** Thỏa mãn $1 < e < \phi(n)$ và $\gcd(e, \phi(n)) = 1$ (thường chọn $e = 65537$ hoặc $e = 17$ cho ví dụ nhỏ).
5. **Tính số mũ bí mật $d$:** Là phần tử nghịch đảo modulo của $e$ theo $\phi(n)$:  
   $$e \cdot d \equiv 1 \pmod{\phi(n)}$$
   Hàm này được nhóm tự lập trình bằng **Thuật toán Euclid mở rộng** (`extended_gcd`).
6. **Mã hóa:** $C = M^e \pmod n$.
7. **Giải mã:** $M = C^d \pmod n$.

### 2. Cơ chế mã hóa xác thực AES-GCM (AEAD)
- **Bản mã $C$:** Mã hóa theo chế độ CTR (Counter Mode): $C_i = P_i \oplus \text{AES}_K(\text{CB}_i)$.
- **Authentication Tag (16B):** Được tính bằng phép nhân lặp Horner trên trường hữu hạn Galois $\mathbb{F}_{2^{128}}$ với đa thức bất khả quy:
  $$f(x) = x^{128} + x^7 + x^2 + x + 1$$
  Mỗi khối bản mã $C_i$ được băm luân phiên qua hàm GHASH. Do tính chất khuếch tán của Galois Field, nếu chỉ cần 1 bit của $C_i$ bị lật, giá trị Tag cuối cùng sẽ sai hoàn toàn.

---

# PHẦN 4: KIẾN TRÚC MẠNG TCP SOCKET

1. **Vấn đề phân mảnh TCP:** TCP là luồng byte, không có khái niệm "kết thúc tin nhắn". Nếu gửi 2 chuỗi JSON liên tiếp, bên nhận có thể nhận cả 2 chuỗi trong 1 lệnh `recv()` (dính gói) hoặc nhận nửa chuỗi đầu (xé gói).
2. **Giải pháp nhóm dùng (Length-prefixed):**
   - Trước khi gửi JSON, nhóm tính độ dài byte $L$, dùng `struct.pack("!I", L)` tạo 4 byte số nguyên không dấu (Big-Endian) gửi trước.
   - Bên nhận dùng hàm `recv_exact(conn, 4)` đọc đúng 4 byte đầu để biết $L$, sau đó gọi tiếp `recv_exact(conn, L)` để đọc trọn vẹn JSON.
3. **Format gói tin trên đường truyền:**
   ```json
   {
     "enc_session_key": "hex_string",
     "nonce": "base64_string",
     "ciphertext": "base64_string",
     "auth_tag": "base64_string"
   }
   ```
   Do các trường nhị phân không in được trực tiếp dưới dạng văn bản, nhóm mã hóa Base64 cho `nonce`, `ciphertext`, `auth_tag`, và biểu diễn hex cho số nguyên lớn `enc_session_key`.

---

# PHẦN 5: BỘ CÂU HỎI PHẢN BIỆN CHUYỂN TIẾP CỦA GIẢNG VIÊN (FAQ)

### Câu 1: "Tại sao nhóm gọi việc so sánh Fingerprint là Xác thực ngoại vi (Out-of-band)?"
* **Trả lời:** "Thưa cô, vì kênh truyền TCP chính (cổng 5000) là kênh nội vi (In-band), hiện tại chưa có bên thứ ba như Certificate Authority (CA) để chứng thực chứng chỉ số. Do đó, kẻ tấn công Man-in-the-Middle có thể đứng giữa tráo Public Key. Việc Alice và Bob kiểm tra chuỗi băm Fingerprint qua một phương tiện độc lập hoàn toàn với kết nối mạng này (như nhìn trực tiếp màn hình của nhau, gọi điện thoại, hoặc quét mã QR) được mật mã học định nghĩa là kênh ngoại vi (Out-of-band), giúp xác thực chính xác chủ nhân của khóa."

### Câu 2: "Tại sao không dùng RSA mã hóa luôn cả file cho tiện mà phải sinh thêm AES?"
* **Trả lời:** "Thưa cô, có hai lý do chí mạng:
  1. *Hiệu năng:* Phép toán lũy thừa modulo trên số lớn của RSA cực kỳ tốn CPU. Nếu mã hóa một file vài chục MB bằng RSA thì máy sẽ bị nghẽn, trong khi AES có hỗ trợ phần cứng (tập lệnh AES-NI) mã hóa hàng trăm MB/giây.
  2. *Giới hạn kích thước:* Bản rõ $M$ trong RSA bắt buộc phải nhỏ hơn modulus $n$ ($M < n$). Muốn mã hóa file lớn bằng RSA thì phải chia nhỏ file thành từng block và mã hóa từng block, điều này vừa chậm vừa không an toàn trước các kiểu tấn công toán học."

### Câu 3: "IV trong AES-GCM có cần giữ bí mật không? Nếu lộ thì sao?"
* **Trả lời:** "Thưa cô, IV (Vector khởi tạo) **không cần giữ bí mật** và được truyền công khai trong gói tin. Nhiệm vụ của IV là đảm bảo rằng nếu ta mã hóa cùng một nội dung thông điệp 2 lần bằng cùng một khóa $K$, thì 2 bản mã sinh ra vẫn hoàn toàn khác nhau. Tuy nhiên, quy tắc sống còn của AES-GCM là **không bao giờ được tái sử dụng cùng một cặp (Khóa $K$, IV)**, vì nếu tái sử dụng sẽ làm lộ khóa xác thực GHASH."

### Câu 4: "Tại sao trong báo cáo nói modulus $n$ phải lớn hơn $2^{128}$?"
* **Trả lời:** "Thưa cô, vì Session Key của AES-128 dài 16 bytes = 128 bits. Nhóm chuyển 16 bytes này thành một số nguyên duy nhất để RSA mã hóa một lần ($C_{\text{key}} = K^e \pmod n$). Để phép mã hóa không bị tràn số hoặc bị cắt cụt do phép modulo, số modulus $n$ của Bob bắt buộc phải lớn hơn giá trị tối đa của số 128-bit ($n > 2^{128}$). Trong code, nhóm sinh khóa RSA 256-bit hoặc 512-bit nên hoàn toàn đáp ứng điều kiện này."
