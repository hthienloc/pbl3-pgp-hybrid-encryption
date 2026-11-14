#import "../styles.typ": report-table

= Các nghiên cứu và phương pháp liên quan

== Tiêu chuẩn mã hóa nâng cao AES và chế độ xác thực GCM
Năm 2001, Viện Tiêu chuẩn và Công nghệ Quốc gia Hoa Kỳ (NIST) đã chính thức ban hành Tiêu chuẩn Mã hóa Nâng cao AES theo FIPS PUB 197 @nist_fips197, thay thế cho chuẩn mã hóa cũ DES vốn đã lỗi thời trước các cuộc tấn công vét cạn. AES là hệ mật mã khối (block cipher) với kích thước khối dữ liệu cố định là 128 bit và hỗ trợ ba độ dài khóa tiêu chuẩn: 128, 192 và 256 bit. Thuật toán vận hành dựa trên cấu trúc mạng hoán vị – thay thế (Substitution-Permutation Network), trong đó dữ liệu trải qua từ 10 đến 14 vòng lặp biến đổi với bốn phép toán đại số chính: `SubBytes` (phi tuyến hóa qua S-box), `ShiftRows` (hoán vị hàng), `MixColumns` (khuếch tán cột trên trường Galois $"GF"(2^8)$) và `AddRoundKey` (cộng khóa vòng bằng phép XOR).

Trong các chế độ hoạt động truyền thống của mật mã khối như CBC (Cipher Block Chaining) hay ECB (Electronic Codebook), hệ thống chỉ đảm bảo tính bí mật mà không có khả năng tự phát hiện nếu dữ liệu bị sửa đổi. Kẻ tấn công có thể can thiệp vào các khối bản mã để làm thay đổi nội dung giải mã mà không kích hoạt bất kỳ cảnh báo nào. Để khắc phục triệt để lỗ hổng này, chế độ Galois/Counter Mode (GCM) được đề xuất bởi McGrew và Viega năm 2004 @mcgrew2004 và được NIST chuẩn hóa trong tài liệu SP 800-38D @nist_sp800_38d. AES-GCM thuộc họ mật mã xác thực có dữ liệu bổ sung (AEAD – Authenticated Encryption with Associated Data). Nó kết hợp chế độ mã hóa dòng Counter Mode (CTR) có khả năng tính toán song song với hàm băm vạn năng GHASH trên trường hữu hạn Galois $"GF"(2^(128))$. Nhờ đó, AES-GCM không chỉ bảo vệ tính bí mật tuyệt đối của nội dung thông điệp mà còn sinh ra một thẻ chứng thực mật mã (Authentication Tag) 128-bit, đảm bảo phát hiện tức thời bất kỳ hành vi thay đổi dù chỉ một bit trên đường truyền.

== Hệ mật mã bất đối xứng RSA và bài toán phân tích số nguyên
Ý tưởng đột phá về mật mã khóa công khai được khởi xướng bởi Whitfield Diffie và Martin Hellman vào năm 1976 @diffie_hellman1976, mở ra kỷ nguyên mới cho phép hai bên trao đổi thông tin bí mật mà không cần thỏa thuận khóa trước. Dựa trên ý tưởng này, Ronald Rivest, Adi Shamir và Leonard Adleman đã phát minh ra thuật toán RSA vào năm 1977 tại Viện Công nghệ Massachusetts (MIT) @rivest1978. Bảo mật của hệ mật RSA dựa trên độ khó tính toán của bài toán phân tích một số nguyên hợp số lớn thành tích của hai thừa số nguyên tố (Integer Factorization Problem). Cụ thể, việc tính tích $n = p dot q$ từ hai số nguyên tố $p$ và $q$ là một phép nhân trực tiếp cực kỳ dễ dàng trên máy tính; tuy nhiên, chiều ngược lại – tìm $p$ và $q$ từ giá trị tích $n$ – là bài toán chưa có lời giải trong thời gian đa thức trên máy tính cổ điển khi $n$ đạt độ dài từ 2048 bit trở lên.

Chuẩn mật mã khóa công khai PKCS #1 / RFC 8017 @rfc8017 quy định chi tiết cấu trúc cặp khóa và cơ chế toán học của RSA. Người sở hữu công khai cặp khóa $(e, n)$ cho toàn thể người dùng trên mạng và giữ bí mật tuyệt đối khóa $d$. Một ưu điểm vượt trội của RSA là tính đối ngẫu toán học: nếu thông điệp được mã hóa bằng Public Key $(e, n)$ thì chỉ có Private Key $(d, n)$ giải mã được (phục vụ bảo mật dữ liệu); ngược lại, nếu thông điệp được xử lý bằng Private Key $(d, n)$ thì bất kỳ ai có Public Key $(e, n)$ cũng có thể kiểm chứng được (phục vụ tạo chữ ký số).

== Chuẩn bảo mật thư điện tử PGP và OpenPGP
Năm 1991, Phil Zimmermann phát triển phần mềm PGP (Pretty Good Privacy) nhằm cung cấp công cụ bảo vệ quyền riêng tư cá nhân khi trao đổi thư điện tử qua mạng Internet. Sau đó, Tổ chức Đặc trách Kỹ thuật Internet (IETF) đã chuẩn hóa công nghệ này thành bộ chuẩn mở OpenPGP qua RFC 4880 @rfc4880 và mới nhất là RFC 9580 @rfc9580. OpenPGP không xây dựng một thuật toán mật mã riêng biệt mà đóng vai trò như một bộ giao thức tích hợp các giải thuật mật mã tiêu chuẩn: sử dụng mã hóa đối xứng (AES, Triple-DES, IDEA) để bảo vệ thân thư điện tử; sử dụng mật mã khóa công khai (RSA, ElGamal, ECC) để mã hóa khóa phiên; và sử dụng hàm băm (SHA-256, SHA-512) kết hợp RSA để tạo chữ ký điện tử. Đặc biệt, OpenPGP tiên phong xây dựng mô hình mạng lưới tín nhiệm (Web of Trust), cho phép người dùng tự ký chéo khóa công khai của nhau để xác thực danh tính mà không phụ thuộc vào một cơ quan cấp chứng chỉ tập trung (CA).

== So sánh kỹ thuật và lý do kết hợp mã hóa lai
@tbl-aes-rsa-compare so sánh chi tiết các đặc tính kỹ thuật cốt lõi giữa hệ mật mã đối xứng AES và hệ mật mã bất đối xứng RSA. Qua đó có thể thấy mỗi hệ mật đều sở hữu những ưu thế độc nhất nhưng lại đi kèm với những hạn chế lớn không thể giải quyết độc lập.

#figure(
  report-table(
    columns: (1.1fr, 1.5fr, 1.5fr),
    headers: ("Tiêu chí so sánh", "AES-128-GCM (Đối xứng)", "RSA-256 / 512 (Bất đối xứng)"),
    rows: (
      ([Số lượng khóa], [Dùng duy nhất 1 khóa phiên bí mật $K$ chung cho cả hai đầu.], [Dùng cặp khóa: Public Key $(e, n)$ và Private Key $(d, n)$.]),
      ([Tốc độ & Chi phí tính toán], [Cực kỳ nhanh; chi phí phần cứng thấp nhờ các phép toán XOR và tra bảng S-box.], [Rất chậm; đòi hỏi các phép nhân và lũy thừa mô-đun trên số nguyên lớn hàng trăm bit.]),
      ([Xử lý dữ liệu lớn], [Tối ưu hóa tuyệt vời cho các tệp tin, dòng video và luồng truyền thông mạng lớn.], [Không khả thi; chỉ mã hóa được dữ liệu có giá trị số học nhỏ hơn modulus $n$.]),
      ([Phân phối khóa qua mạng], [Rất khó khăn; đòi hỏi phải có kênh truyền an toàn sẵn từ trước để chia sẻ khóa $K$.], [Rất dễ dàng; khóa công khai được phát tán tự do qua mạng mà không sợ lộ.]),
      ([Toàn vẹn & Chống sửa đổi], [Tích hợp sẵn qua hàm băm GHASH và Authentication Tag 128-bit.], [Thuần túy không tự kiểm thực toàn vẹn; cần kết hợp chữ ký số (RSA-PSS + hàm băm) và dùng RSA-OAEP để bảo mật IND-CCA2.]),
    ),
  ),
  caption: [So sánh đặc tính kỹ thuật giữa hệ mật mã đối xứng AES và bất đối xứng RSA.],
) <tbl-aes-rsa-compare>

Từ những phân tích trên, giải pháp *Mã hóa lai (Hybrid Encryption)* ra đời theo nguyên lý: _"AES đảm nhận việc mã hóa dữ liệu lớn, RSA đảm nhận việc bảo vệ và vận chuyển khóa đối xứng"_. Công thức tổng quát biểu diễn gói tin PGP Hybrid được xác định bởi:

$ "PGP_Packet" = { "RSA"_(e_B)(K), quad "AES"_K (M) } $

Trong đó, $e_B$ là khóa công khai của người nhận Bob, $K$ là khóa phiên ngẫu nhiên dùng một lần do Alice khởi tạo, và $M$ là thông điệp bản rõ ban đầu. Nhờ mô hình này, hệ thống khắc phục được sự đánh đổi giữa tốc độ xử lý dữ liệu lớn của AES và khả năng phân phối khóa qua kênh mở của RSA (lưu ý: kích thước khóa RSA 256/512-bit trong đồ án phục vụ mục đích học thuật và mô phỏng; hệ thống triển khai thực tế cần sử dụng RSA $\ge 2048$-bit kèm đệm RSA-OAEP).
