#import "../figures.typ": fig-sequence-interaction, fig-packet-layout
#import "../styles.typ": report-table

= Phương pháp thực hiện

== Quy trình Hybrid Encryption tổng thể
Luồng truyền thông giữa Alice (gửi) và Bob (nhận) gồm 5 giai đoạn tuần tự như mô tả trong @tbl-hybrid-process và sơ đồ tương tác ở @fig-sequence-interaction.

#figure(
  report-table(
    columns: (1fr, 1.8fr, 1.8fr),
    headers: ("Giai đoạn", "Phía Alice (Người gửi)", "Phía Bob (Người nhận)"),
    rows: (
      ([GĐ 0: Khởi tạo danh tính], [Nhận Public Key $(e, n)$ của Bob qua mạng hoặc tệp cấu hình.], [Sinh cặp khóa RSA $(e, n)$ và $(d, n)$; công khai $(e, n)$.]),
      ([GĐ 1: Sinh khóa phiên $K$], [Dùng CSPRNG (`os.urandom`) sinh Session Key $K$ (16 bytes = 128-bit).], [Chờ gói tin từ phía gửi qua socket mạng.]),
      ([GĐ 2: Mã hóa dữ liệu & khóa], [- AES-GCM mã hóa $M$ bằng $K$ $arrow.r$ `ciphertext`, `nonce`, `auth_tag`. \ - RSA mã hóa $K$ bằng $(e, n)$ $arrow.r$ `enc_session_key`.], [Không thực hiện.]),
      ([GĐ 3: Đóng gói & Truyền tải], [Đóng gói JSON Envelope 4 trường mật mã, thêm tiền tố 4-byte độ dài gửi qua TCP.], [Đọc 4-byte độ dài, nhận đủ gói JSON Envelope vào bộ nhớ đệm.]),
      ([GĐ 4: Giải mã & Kiểm thực], [Chờ phản hồi kết quả từ máy nhận.], [- Dùng $d$ giải RSA: $K' = (C_"key")^d mod n$. \ - Kiểm thực `auth_tag` qua GHASH; khớp thì giải mã ra $M'$.]),
    ),
  ),
  caption: [Quy trình thực hiện mã hóa lai giữa phía gửi (Alice) và phía nhận (Bob).],
) <tbl-hybrid-process>

#v(0.3em)
#align(center)[
  #fig-sequence-interaction <fig-sequence-interaction>
]
#v(0.3em)

== Cơ sở số học của thuật toán RSA
Thuật toán RSA số học thuần túy gồm các bước sau:
+ *Kiểm tra nguyên tố xác suất Miller–Rabin:* Sinh hai số nguyên tố $p, q$ (128-bit cho RSA-256 ở demo thuật toán; 256-bit cho RSA-512 ở giao tiếp Socket) bằng thuật toán Miller–Rabin @rabin1980 với $k = 20$ vòng lặp (trong `algorithms/rsa.py`). Xác suất hợp số lọt qua nhỏ hơn $(1/4)^(20) approx 9.09 times 10^(-13)$.
+ *Modulus và hàm Euler:* Tính $n = p dot q$ (256 hoặc 512 bit) và $phi(n) = (p - 1)(q - 1)$.
+ *Số mũ công khai Fermat $e = 65537$:* Chọn $e = 2^(16) + 1$ (số nguyên tố Fermat $F_4$, dạng nhị phân $10000000000000001_2$ chỉ có 2 bit 1), giúp phép lũy thừa theo mô-đun chỉ cần 16 phép bình phương và 1 phép nhân.
+ *Nghịch đảo mô-đun (Euclid mở rộng):* Tìm khóa bí mật $d$ từ $e dot d equiv 1 (mod phi(n))$, tương đương phương trình Bézout $e dot d + phi(n) dot y = 1$, với độ phức tạp $O(log(phi(n)))$.

*Chứng minh tính đúng đắn dựa trên Định lý Euler:* \
Phía Bob tính:
$ K' = (C_"key")^d mod n = ((K^e) mod n)^d mod n = K^(e dot d) mod n $
Vì $e dot d equiv 1 (mod phi(n))$, tồn tại $k in ZZ$ sao cho $e dot d = 1 + k dot phi(n)$. Khi $gcd(K, n) = 1$, theo Định lý Euler $K^(phi(n)) equiv 1 (mod n)$:
$ K' equiv K^(1 + k dot phi(n)) equiv K dot (K^(phi(n)))^k equiv K dot 1^k equiv K (mod n) $
Nếu $gcd(K, n) != 1$ ($K$ là bội của $p$ hoặc $q$), kết hợp Định lý Fermat nhỏ trên $p, q$ và Định lý Số dư Trung Hoa (CRT) vẫn cho $K^(e dot d) equiv K (mod p)$ và $K^(e dot d) equiv K (mod q)$, suy ra $K^(e dot d) equiv K (mod n)$. Do $K$ (128-bit) thỏa $K < 2^(128) < n$, giá trị $K'$ trùng khớp với $K$ ban đầu.

== Cơ chế mã hóa xác thực AES-GCM (AEAD)
Theo chuẩn NIST SP 800-38D @nist_sp800_38d, AES-GCM thực hiện đồng thời mã hóa và xác thực:
+ *Mã hóa dòng Counter Mode (CTR):* Với Nonce 96-bit (12 bytes), khối đếm ban đầu là $J_0 = "CB"_0 = "Nonce" || "00000001"_(16)$. Bản rõ $M$ được chia thành các khối 16 bytes $P_1, P_2, dots, P_m$; các khối đếm tăng dần qua phép tăng 32-bit cuối $"CB"_i = "inc"_(32)("CB"_(i-1))$ ($i >= 1$, tức $"CB"_1 = "Nonce" || "00000002"_(16)$, $"CB"_2 = "Nonce" || "00000003"_(16)$, ...). Bản mã được tính bằng:
  $ C_i = P_i xor "AES"_K ("CB"_i) $
  Cơ chế này không cần padding và hỗ trợ tính toán song song.
+ *Xác thực toàn vẹn bằng GHASH:* Khóa băm $H = "AES"_K (0^(128))$. Phép nhân trên trường hữu hạn $"GF"(2^(128))$ sử dụng đa thức bất khả quy:
  $ f(x) = x^(128) + x^7 + x^2 + x + 1 $
  Khối bản mã cuối $C_m$ nếu chưa đủ 128 bit được đệm bit 0 về bên phải. Giá trị băm tích lũy là $X_i = (X_(i-1) xor C_i) dot H$ ($X_0 = 0^(128)$). Cuối cùng, GHASH nhân thêm khối 128-bit độ dài bit của dữ liệu bổ sung $A$ và bản mã $C$ ($"len"_(64)(A) || "len"_(64)(C)$, với $A = emptyset$), rồi XOR với $"AES"_K ("CB"_0)$ để tạo Authentication Tag:
  $ "Tag" = ((X_m xor ("len"_(64)(A) || "len"_(64)(C))) dot H) xor "AES"_K ("CB"_0) $

Nhờ tính khuếch tán trên $"GF"(2^(128))$, mọi thay đổi dù chỉ 1 bit trong bản mã đều làm sai lệch giá trị GHASH tính lại tại Bob. Khi `"Tag"_"computed" != "Tag"_"received"`, hệ thống ném ngoại lệ `ValueError: MAC check failed` và hủy gói tin ngay tại tầng giải mã.

== Đóng gói khung truyền thông mạng và giao thức Socket TCP
TCP truyền dữ liệu dạng luồng byte (byte stream), không giữ ranh giới thông điệp nên dễ xảy ra phân mảnh hoặc dính gói. Hệ thống khắc phục bằng *đóng khung tiền tố độ dài (Length-Prefixed Framing)*: mỗi gói tin đều gắn tiền tố 4-byte số nguyên không dấu Big-Endian (`!I`) chỉ kích thước payload JSON UTF-8 đi kèm (và kiểm tra giới hạn kích thước tối đa ở phía nhận để chống tràn bộ nhớ).

Cấu trúc JSON Envelope được mô tả trong @tbl-packet-fields. Ở tầng Socket (`PGP_RSA_AES_Socket_3_files/`), `enc_session_key` truyền dưới dạng số nguyên lớn (hoặc chuỗi hex ở CLI demo), còn `nonce`, `ciphertext`, `auth_tag` được mã hóa Base64 (gói tin gửi lên server có thêm `"action": "SEND_MESSAGE"`).

#figure(
  report-table(
    columns: (1.1fr, 1.1fr, 1.1fr, 1.8fr),
    headers: ("Tên trường JSON", "Kích thước gốc", "Định dạng truyền tải", "Mô tả vai trò mật mã"),
    rows: (
      ([`enc_session_key`], [256 / 512 bit], [Số nguyên lớn / Hex], [Khóa phiên $K$ (128-bit) đã mã hóa bằng Public Key của Bob qua RSA.]),
      ([`nonce`], [12 bytes (96 bit)], [Base64 / Hex], [Vector khởi tạo ngẫu nhiên dùng một lần cho AES-GCM.]),
      ([`ciphertext`], [Biến thiên ($|M|$ bytes)], [Base64 / Hex], [Bản mã của $M$ sinh bởi AES CTR Mode.]),
      ([`auth_tag`], [16 bytes (128 bit)], [Base64 / Hex], [Mã xác thực sinh bởi hàm băm GHASH trên $"GF"(2^(128))$.]),
    ),
  ),
  caption: [Cấu trúc trường dữ liệu của gói tin PGP Hybrid qua mạng.],
) <tbl-packet-fields>

Để chống tấn công kẻ đứng giữa (Man-in-the-Middle) giả mạo khóa công khai, hệ thống tạo dấu vân tay SHA-256 (64 ký tự hex) cho Public Key của Bob để hai bên đối chiếu trước khi gửi:
$ "fingerprint"("pub_key") = "SHA256"("RSA:" || e || ":" || n) $

Quy cách đóng gói khung và luồng phân tích cú pháp tại Bob được minh họa trong @fig-packet-layout.

#v(0.3em)
#align(center)[
  #fig-packet-layout <fig-packet-layout>
]
#v(0.3em)
