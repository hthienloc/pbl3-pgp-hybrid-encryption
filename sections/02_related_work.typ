#import "../styles.typ": report-table

= Các nghiên cứu và phương pháp liên quan

== Tiêu chuẩn mã hóa nâng cao AES và chế độ xác thực GCM
Năm 2001, NIST ban hành Tiêu chuẩn Mã hóa Nâng cao AES (FIPS PUB 197 @nist_fips197) để thay thế DES. AES là mật mã khối kích thước 128 bit, hỗ trợ khóa 128, 192 và 256 bit, hoạt động theo cấu trúc mạng hoán vị - thay thế (SPN) qua 10 đến 14 vòng lặp với bốn phép toán: `SubBytes` (S-box), `ShiftRows`, `MixColumns` trên trường Galois $"GF"(2^8)$ và `AddRoundKey` (XOR).

Các chế độ truyền thống như CBC hay ECB chỉ đảm bảo tính bí mật mà không tự phát hiện được việc sửa đổi bản mã. Để khắc phục, chế độ Galois/Counter Mode (GCM) do McGrew và Viega đề xuất năm 2004 @mcgrew2004 đã được NIST chuẩn hóa trong SP 800-38D @nist_sp800_38d. Thuộc nhóm AEAD (Authenticated Encryption with Associated Data), AES-GCM kết hợp mã hóa dòng Counter Mode (CTR) song song với hàm băm vạn năng GHASH trên $"GF"(2^(128))$, sinh ra Authentication Tag 128-bit giúp phát hiện mọi thay đổi bit trên đường truyền.

== Hệ mật mã bất đối xứng RSA và bài toán phân tích số nguyên
Khái niệm mật mã khóa công khai do Diffie và Hellman đề xuất năm 1976 @diffie_hellman1976 cho phép trao đổi thông tin mật mà không cần thỏa thuận khóa trước. Trên cơ sở đó, Rivest, Shamir và Adleman công bố thuật toán RSA năm 1977 tại MIT @rivest1978. Độ an toàn của RSA dựa trên bài toán phân tích số nguyên lớn (Integer Factorization Problem): việc tính $n = p dot q$ từ hai số nguyên tố $p, q$ rất nhanh, nhưng tìm ngược lại $p, q$ từ $n$ chưa có thuật toán thời gian đa thức trên máy tính cổ điển khi $n >= 2048$ bit.

Chuẩn PKCS #1 / RFC 8017 @rfc8017 quy định cấu trúc khóa và cơ chế toán học của RSA: công khai $(e, n)$ và giữ bí mật $d$. Nhờ tính đối ngẫu toán học, dữ liệu mã hóa bằng khóa công khai $(e, n)$ chỉ giải mã được bằng khóa bí mật $(d, n)$ (đảm bảo bảo mật), trong khi dữ liệu xử lý bằng khóa bí mật $(d, n)$ có thể kiểm chứng bằng khóa công khai $(e, n)$ (tạo chữ ký số).

== Chuẩn bảo mật thư điện tử PGP và OpenPGP
Năm 1991, Phil Zimmermann phát triển PGP (Pretty Good Privacy), sau được IETF chuẩn hóa thành OpenPGP qua RFC 4880 @rfc4880 và RFC 9580 @rfc9580. OpenPGP tích hợp các chuẩn mật mã sẵn có: mã hóa đối xứng (AES, Triple-DES, IDEA) cho nội dung thư; mã hóa bất đối xứng (RSA, ElGamal, ECC) cho khóa phiên; và hàm băm (SHA-256, SHA-512) kết hợp RSA cho chữ ký số. OpenPGP cũng sử dụng mô hình Web of Trust, cho phép người dùng ký chéo khóa công khai thay vì phụ thuộc vào CA tập trung.

== So sánh kỹ thuật và lý do kết hợp mã hóa lai
@tbl-aes-rsa-compare đối chiếu đặc tính kỹ thuật giữa AES và RSA, cho thấy mỗi hệ mật có ưu điểm và hạn chế riêng.

#figure(
  report-table(
    columns: (1.1fr, 1.5fr, 1.5fr),
    headers: ("Tiêu chí so sánh", "AES-128-GCM (Đối xứng)", "RSA-256 / 512 (Bất đối xứng)"),
    rows: (
      ([Số lượng khóa], [1 khóa phiên bí mật $K$ chung cho cả hai đầu.], [Cặp khóa: khóa công khai $(e, n)$ và khóa bí mật $(d, n)$.]),
      ([Tốc độ & Chi phí], [Rất nhanh; chi phí phần cứng thấp (XOR, tra bảng S-box).], [Chậm; đòi hỏi nhân và lũy thừa mô-đun trên số nguyên lớn.]),
      ([Xử lý dữ liệu lớn], [Phù hợp cho tệp tin, video và luồng mạng lớn.], [Không phù hợp; chỉ mã hóa được giá trị nhỏ hơn modulus $n$.]),
      ([Phân phối khóa], [Khó; cần kênh truyền an toàn sẵn để chia sẻ $K$.], [Dễ; khóa công khai phát tán tự do qua mạng mở.]),
      ([Toàn vẹn & Chống sửa đổi], [Tích hợp sẵn qua GHASH và Authentication Tag 128-bit.], [Không tự kiểm thực; cần chữ ký số (RSA-PSS + băm) và RSA-OAEP cho IND-CCA2.]),
    ),
  ),
  caption: [So sánh đặc tính kỹ thuật giữa hệ mật mã đối xứng AES và bất đối xứng RSA.],
) <tbl-aes-rsa-compare>

Mô hình mã hóa lai kết hợp cả hai hệ mật theo nguyên lý: AES mã hóa dữ liệu, RSA bảo vệ khóa phiên. Gói tin PGP Hybrid được biểu diễn bởi:

$ "PGP_Packet" = { "RSA"_(e_B)(K), quad "AES"_K (M) } $

Trong đó $e_B$ là khóa công khai của Bob, $K$ là khóa phiên ngẫu nhiên dùng một lần do Alice tạo, và $M$ là bản rõ. Cách kết hợp này tận dụng được tốc độ của AES và khả năng phân phối khóa của RSA. Trong phạm vi đồ án, kích thước khóa RSA được chọn là 256/512-bit để phục vụ mô phỏng; khi triển khai thực tế cần dùng khóa từ 2048-bit trở lên kèm đệm RSA-OAEP.
