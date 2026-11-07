# KỊCH BẢN BÁO CÁO TIẾN ĐỘ ĐỒ ÁN PBL3 (PGP HYBRID ENCRYPTION)
**Chủ đề:** Nguyên lý RSA và mô hình mã hóa lai RSA – AES  
**GVHD:** TS. Trần Thị Minh Hạnh | **Nhóm:** 7  
**Thời lượng dự kiến:** ~7 – 10 phút  

---

## 1. Mở đầu: Báo cáo việc tiếp thu góp ý của cô ở buổi trước (~1 phút)

> *"Em chào cô ạ. Ở buổi góp ý trước, cô có dặn nhóm hai nhiệm vụ trọng tâm để hoàn thiện báo cáo:*
> 1. *Vẽ lại toàn bộ hệ thống sơ đồ kỹ thuật cho chuẩn mực, rõ ràng từng trường dữ liệu và luồng truyền thông.*
> 2. *Hiện thực hóa mô hình từ tiến trình cục bộ lên môi trường mạng thực tế bằng bản Demo truyền thông qua Socket TCP giữa 2 máy.*
>
> *Hôm nay, nhóm em xin phép báo cáo kết quả chi tiết mà nhóm đã thực hiện theo đúng các yêu cầu trên của cô ạ."*

---

## 2. Phần 1: Báo cáo kết quả chuẩn hóa & vẽ lại hệ thống sơ đồ (~3 phút)
*(Chuyển qua các trang tương ứng trong báo cáo: Hình 1, Hình 2, Hình 4)*

### a. Sơ đồ tuần tự tương tác Alice – Bob (Hình 2)
> *"Thưa cô, trước đây sơ đồ của nhóm chưa làm rõ vai trò của các tham số khi truyền tin. Nhóm đã vẽ lại hoàn chỉnh sơ đồ tuần tự thể hiện rõ 4 thành phần trong gói tin PGP gồm: `{C_key, IV, C_data, Tag}`:*
> - *Phía Alice không chỉ sinh Session Key $K$ mà còn sinh vector khởi tạo **IV** (12 bytes) cho chế độ **AES-GCM** để chống lặp bản mã.*
> - *Quá trình mã hóa sinh ra đồng thời bản mã **$C_{\text{data}}$** và thẻ kiểm thực **Tag (16 bytes)**.*
> - *Tại phía Bob, sơ đồ thể hiện rõ quy trình 2 bước: Đầu tiên dùng Private Key RSA giải mã $C_{\text{key}}$ để lấy lại $K$; sau đó nạp $K$, IV và đối chiếu **Tag** bằng hàm GHASH để xác thực toàn vẹn trước khi giải mã bản rõ $M$."*

### b. Sơ đồ cấu trúc khung gói tin & phân tích cú pháp (Hình 4)
> *"Để phục vụ cho việc truyền trên mạng, nhóm đã thiết kế lại sơ đồ cấu trúc byte stream liên tục (Packet Framing) với các offset cụ thể:*
> - *`0 đến 255 (256B)`: Chứa khóa phiên RSA đã mã hóa ($C_{\text{key}}$).*
> - *`256 đến 267 (12B)`: Chứa Nonce / IV của GCM.*
> - *`268 đến 268+L-1`: Chứa bản mã AES ($C_{\text{data}}$).*
> - *`16 bytes cuối cùng`: Chứa Authentication Tag.*
>
> *Phía dưới sơ đồ ánh xạ trực tiếp từng khối byte này vào 4 hàm phân tích cú pháp tương ứng của Bob: `rsa_decrypt()`, `AES.new()`, `decrypt()` và `verify()`."*

---

## 3. Phần 2: Hiện thực hóa mô phỏng qua Socket TCP (Hình 5 & Demo) (~4 phút)
*(Chiếu Mục 10: Sơ đồ Hình 5 và terminal chạy demo mạng)*

### a. Kiến trúc & xử lý luồng mạng
> *"Theo yêu cầu của cô về phần demo TCP, nhóm đã tách kiến trúc thành 3 tệp độc lập:*
> - *`server_bob.py`: Đóng vai trò máy nhận, sinh cặp khóa RSA tự động và mở socket lắng nghe tại cổng `5000`.*
> - *`client_alice.py`: Đóng vai trò máy gửi, kết nối tới IP của Bob, lấy Public Key và truyền gói tin PGP.*
> - *`pgp_crypto.py`: Cầu nối chuyển đổi giữa cấu trúc JSON/Base64 trên đường truyền và các thuật toán toán học.*
>
> *Vì TCP là luồng byte stream (không có ranh giới tin nhắn), nhóm đã áp dụng cơ chế **Length-prefixed framing (4 bytes length)** đặt ở đầu mỗi gói tin, giúp bên nhận đọc chính xác kích thước gói mà không bị hiện tượng phân mảnh dữ liệu."*

### b. Cơ chế bắt tay & Xác thực ngoại vi (Out-of-band Authentication)
> *(Điểm mấu chốt giải thích câu hỏi kỹ thuật)*  
> *"Đặc biệt, khi truyền thông qua Socket TCP, một lỗ hổng lớn là kẻ tấn công đứng giữa (Man-in-the-Middle) có thể tráo Public Key của Bob khi Alice yêu cầu `GET_PUBLIC_KEY`.*  
> *Để giải quyết vấn đề này theo đúng nguyên lý PGP:*
> - *Chương trình tự động tính toán **Fingerprint SHA-256** của khóa công khai.*
> - *Alice và Bob tiến hành **Xác thực ngoại vi (Out-of-Band)** bằng cách đối chiếu chuỗi Fingerprint này qua một kênh tin cậy độc lập (như đối chiếu trực tiếp màn hình terminal của nhau hoặc qua điện thoại).*
> - *Khi hai chuỗi băm trùng khớp 100%, Alice mới thực hiện mã hóa và gửi gói tin PGP."*

### c. Kết quả kiểm thử thực nghiệm trên Socket
> *"Nhóm đã kiểm thử thành công trên 3 kịch bản thực tế:*
> 1. *Gửi gói tin bình thường $\rightarrow$ Bob giải mã chính xác và phản hồi `status: OK`.*
> 2. *Giả lập hacker can thiệp sửa đổi 1 byte trên đường truyền $\rightarrow$ AES-GCM tại Bob phát hiện lỗi `MAC check failed`, lập tức từ chối gói tin và phản hồi `status: ERROR`.*
> 3. *Giả lập can thiệp làm sai lệch khóa phiên $\rightarrow$ Bob không thể giải mã và ném ngoại lệ an toàn."*

---

## 4. Phần 3: Kết luận & Kế hoạch giai đoạn tới (~1 phút)

> *"Dạ thưa cô, như vậy nhóm đã hoàn thành trọn vẹn 2 yêu cầu của cô ở buổi trước: chuẩn hóa toàn bộ sơ đồ kỹ thuật và xây dựng thành công demo PGP Hybrid chạy ổn định trên socket TCP.*
> 
> *Trong giai đoạn tiếp theo, nhóm dự kiến hoàn thiện các mục:*
> 1. *Bổ sung thêm cơ chế **Chữ ký số (Digital Signature)** kết hợp RSA và SHA-256 để chống chối bỏ.*
> 2. *Thử nghiệm đóng gói truyền nhận các **tệp tin nhị phân lớn** (ảnh, PDF).*
> 3. *Đo đạc **Benchmark** hiệu năng (thông lượng và thời gian xử lý) giữa RSA thuần và mô hình Hybrid để đưa vào báo cáo nghiệm thu.*
>
> *Nhóm em xin cảm ơn cô và rất mong nhận được thêm những ý kiến nhận xét của cô ạ!"*

---

## PHẦN PHỤ LỤC: CÂU HỎI THƯỜNG GẶP CỦA GIẢNG VIÊN (FAQ)

| Câu hỏi của GV | Cách trả lời trọng tâm |
| :--- | :--- |
| **"Tại sao gọi là xác thực ngoại vi (Out-of-band)?"** | Dạ vì kênh TCP chính (in-band) chưa có hạ tầng khóa công khai CA nên có thể bị can thiệp. Việc kiểm tra vân tay (Fingerprint) qua một kênh độc lập bên ngoài (nhìn màn hình, SMS, gọi điện) được gọi là out-of-band. |
| **"Authentication Tag trong AES-GCM dùng để làm gì?"** | Dạ Tag là mã băm GHASH dài 16 bytes (128-bit) trên trường Galois $\mathbb{F}_{2^{128}}$. Nó đảm bảo tính toàn vẹn (Integrity): nếu bản mã bị sửa dù chỉ 1 bit trên đường truyền mạng, việc kiểm tra Tag sẽ thất bại ngay lập tức. |
| **"Tại sao phải dùng Length-prefixed 4 bytes ở socket TCP?"** | Dạ vì TCP là Byte Stream chứ không phải Message-oriented (như UDP). Nếu không có 4 byte độ dài quy ước ở đầu, bên nhận sẽ không biết khi nào một gói tin JSON kết thúc, dẫn tới lỗi dính gói hoặc thiếu gói. |
| **"Khóa phiên AES-128 được mã hóa thế nào qua RSA?"** | Dạ khóa phiên 16 bytes được chuyển đổi thành số nguyên 128-bit, sau đó dùng hàm lũy thừa modulo của RSA: $C_{\text{key}} = K^{e} \pmod n$. Do modulus $n$ sinh ngẫu nhiên 256-bit lớn hơn $2^{128}$ nên khóa được mã hóa trọn vẹn mà không bị tràn bit. |
