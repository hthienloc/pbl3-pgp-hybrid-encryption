#import "../styles.typ": report-table

= Các nghiên cứu và phương pháp liên quan

== Tổng quan mã hóa đối xứng AES-GCM và bất đối xứng RSA
Năm 2001, Viện Tiêu chuẩn và Công nghệ Quốc gia Hoa Kỳ (NIST) ban hành Tiêu chuẩn Mã hóa Nâng cao AES theo FIPS PUB 197 @nist_fips197 nhằm thay thế chuẩn DES đã lỗi thời. AES là hệ mật mã khối có kích thước khối cố định 128 bit, hỗ trợ khóa 128, 192 hoặc 256 bit, vận hành theo cấu trúc mạng thay thế – hoán vị (SPN). Trong các chế độ hoạt động truyền thống như ECB (*Electronic Codebook*) hay CBC (*Cipher Block Chaining*), hệ mật chỉ bảo vệ tính bí mật mà không tự phát hiện được việc sửa đổi bản mã trên đường truyền. Để khắc phục hạn chế này, McGrew và Viega đề xuất chế độ GCM (*Galois/Counter Mode*) năm 2004 @mcgrew2004 và được NIST chuẩn hóa trong SP 800-38D @nist_sp800_38d. AES-GCM thuộc nhóm mật mã xác thực có dữ liệu bổ sung AEAD (*Authenticated Encryption with Associated Data*), kết hợp mã hóa dòng theo bộ đếm (CTR) với hàm băm đại số GHASH trên trường hữu hạn $"GF"(2^(128))$ để vừa giữ bí mật nội dung vừa sinh thẻ xác thực 128-bit chống giả mạo.

Về nhánh mật mã khóa công khai, khái niệm trao đổi khóa không cần chia sẻ bí mật trước do Diffie và Hellman đề xuất năm 1976 @diffie_hellman1976 là nền tảng cho sự ra đời của thuật toán RSA năm 1977 @rivest1978. Độ an toàn của RSA dựa trên tính khó của bài toán phân tích một hợp số nguyên lớn $n = p dot q$ ra hai thừa số nguyên tố $p, q$. Chuẩn PKCS #1 / RFC 8017 @rfc8017 quy định cặp khóa gồm khóa công khai $(e, n)$ dùng để mã hóa và khóa bí mật $(d, n)$ dùng để giải mã, đồng thời hỗ trợ chiều ngược lại cho chữ ký số.

== Chuẩn OpenPGP và lý do kết hợp mã hóa lai
Chuẩn OpenPGP (RFC 4880 @rfc4880, RFC 9580 @rfc9580) không định nghĩa thuật toán mật mã mới mà đóng vai trò kiến trúc tích hợp các giải thuật tiêu chuẩn: dùng mã hóa đối xứng để bảo vệ nội dung thông điệp, dùng mã hóa bất đối xứng để bảo vệ khóa phiên và dùng hàm băm kết hợp chữ ký số để xác thực danh tính. Sự khác biệt kỹ thuật giữa AES-128-GCM và RSA được tổng hợp trong @tbl-aes-rsa-compare.

#figure(
  report-table(
    columns: (1.1fr, 1.5fr, 1.5fr),
    headers: ("Tiêu chí so sánh", "AES-128-GCM (Đối xứng)", "RSA-256 / 512 (Bất đối xứng)"),
    rows: (
      ([Số lượng khóa], [Dùng chung 1 khóa phiên bí mật $K$ (128-bit) cho cả hai đầu.], [Dùng cặp khóa công khai $(e, n)$ và khóa bí mật $(d, n)$.]),
      ([Tốc độ xử lý], [Nhanh nhờ các phép toán dịch byte, tra bảng và XOR.], [Chậm do tính lũy thừa mô-đun trên số nguyên lớn.]),
      ([Kích thước dữ liệu], [Phù hợp với thông điệp và tệp tin dung lượng lớn.], [Chỉ mã hóa trực tiếp giá trị số học nhỏ hơn modulus $n$.]),
      ([Phân phối khóa], [Khó khăn, cần kênh truyền an toàn để chia sẻ khóa $K$.], [Thuận tiện, khóa công khai phát tán tự do qua mạng mở.]),
      ([Kiểm tra toàn vẹn], [Tích hợp sẵn thẻ xác thực 128-bit từ hàm băm GHASH.], [Không tự kiểm tra toàn vẹn; cần chữ ký số hoặc dùng thêm đệm RSA-OAEP để bảo mật IND-CCA2.]),
    ),
  ),
  caption: [So sánh đặc tính kỹ thuật giữa AES-128-GCM và RSA],
) <tbl-aes-rsa-compare>

Do hai hệ mật bù trừ trực tiếp cho nhau, giải pháp mã hóa lai được hình thành theo nguyên tắc phân vai rõ ràng: AES đảm nhận mã hóa toàn bộ dữ liệu bản rõ $M$ bằng khóa phiên ngẫu nhiên $K$, còn RSA đảm nhận mã hóa chính khóa phiên $K$ bằng khóa công khai $e_B$ của người nhận. Công thức đóng gói tổng quát của một gói tin mã hóa lai được biểu diễn ở @eq-hybrid-packet:

$ "PGP_Packet" = { "RSA"_(e_B)(K), quad "AES"_K (M) } $ <eq-hybrid-packet>

Trong mô hình này, kích thước khóa RSA 256-bit hoặc 512-bit được dùng cho mục đích học thuật và mô phỏng trực quan; khi triển khai trong môi trường sản xuất thực tế, độ dài modulus RSA cần nâng lên tối thiểu 2048 bit kèm cơ chế đệm RSA-OAEP.
