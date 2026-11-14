#import "../figures.typ": fig-sequence-interaction, fig-packet-layout
#import "../styles.typ": report-table

= Phương pháp thực hiện

== Quy trình Hybrid Encryption tổng thể
Kiến trúc truyền thông mật mã học giữa hai thực thể chuẩn mực Alice (Bên gửi) và Bob (Bên nhận) được chuẩn hóa thành 5 giai đoạn tuần tự. Quy trình xử lý dữ liệu và trách nhiệm của từng bên được tóm lược chi tiết trong @tbl-hybrid-process.

#figure(
  report-table(
    columns: (1fr, 1.8fr, 1.8fr),
    headers: ("Giai đoạn", "Phía Alice (Người gửi)", "Phía Bob (Người nhận)"),
    rows: (
      ([GĐ 0: Khởi tạo danh tính], [Truy vấn và nhận khóa công khai Public Key $(e, n)$ của Bob qua mạng hoặc tệp cấu hình.], [Sinh cặp khóa RSA: Public Key $(e, n)$ và Private Key $(d, n)$. Công khai cặp $(e, n)$ cho mọi người.]),
      ([GĐ 1: Sinh khóa phiên $K$], [Kích hoạt bộ sinh số ngẫu nhiên an toàn CSPRNG (`os.urandom`) sinh Session Key $K$ (16 bytes = 128-bit).], [Ở trạng thái chờ gói tin từ phía gửi qua socket mạng.]),
      ([GĐ 2: Mã hóa dữ liệu & khóa], [- Dùng AES-GCM mã hóa $M$ bằng $K$ $arrow.r$ tạo `ciphertext`, `nonce`, `auth_tag`. \ - Dùng RSA mã hóa $K$ bằng $(e, n)$ $arrow.r$ tạo `enc_session_key`.], [Không thực hiện.]),
      ([GĐ 3: Đóng gói & Truyền tải], [Ghép gói JSON Envelope 4 trường mật mã (`enc_session_key`, `nonce`, `ciphertext`, `auth_tag`), thêm tiền tố 4-byte độ dài gửi qua TCP.], [TCP Server nhận đủ 4-byte độ dài, đọc chính xác gói tin JSON Envelope vào bộ nhớ đệm.]),
      ([GĐ 4: Giải mã & Kiểm thực], [Hoàn tất nhiệm vụ gửi, chờ phản hồi kết quả từ máy nhận.], [- Dùng Private Key $d$ giải RSA: $K' = (C_"key")^d mod n$. \ - Kiểm tra `auth_tag` bằng GHASH: nếu khớp giải mã ra $M'$.]),
    ),
  ),
  caption: [Quy trình thực hiện mã hóa lai giữa phía gửi (Alice) và phía nhận (Bob).],
) <tbl-hybrid-process>

Sơ đồ tuần tự thể hiện sự tương tác và luồng truyền thông dữ liệu khép kín giữa phía gửi Alice và phía nhận Bob qua kênh mạng được minh họa chi tiết trong @fig-sequence-interaction.

#v(0.3em)
#align(center)[
  #fig-sequence-interaction <fig-sequence-interaction>
]
#v(0.3em)

== Cơ sở số học của thuật toán RSA
Hệ thống mật mã RSA cài đặt trong đề tài sử dụng không gian số nguyên lớn thuần túy với các bước toán học chặt chẽ sau:
+ *Kiểm tra số nguyên tố xác suất Miller–Rabin:* Để sinh các số nguyên tố $p$ và $q$ có độ dài bit chỉ định (128-bit cho mỗi số với RSA-256 ở demo thuật toán, hoặc 256-bit cho mỗi số với RSA-512 ở giao tiếp Socket), giải thuật kiểm tra Miller–Rabin @rabin1980 được áp dụng với số vòng thử nghiệm mặc định $k = 20$ (trong `algorithms/rsa.py`). Xác suất một hợp số lọt qua 20 vòng kiểm tra là nhỏ hơn $(1/4)^(20) approx 9.09 times 10^(-13)$, bảo đảm độ tin cậy cao cho bài toán mô phỏng.
+ *Tính Modulus và hàm số học Euler:* Modulus hệ thống $n = p dot q$ có độ dài xấp xỉ 256 bit (hoặc 512 bit). Hàm số học Euler được tính theo công thức: $phi(n) = (p - 1)(q - 1)$.
+ *Lựa chọn số mũ công khai Fermat $e = 65537$:* Giá trị $e = 2^(16) + 1$ được chọn cố định vì là số nguyên tố Fermat $F_4$. Dạng nhị phân của 65537 là $10000000000000001_2$ chỉ chứa đúng hai bit 1, giúp thuật toán nhân và bình phương liên tiếp chỉ mất đúng 16 phép bình phương và 1 phép nhân theo mô-đun, tối ưu hóa tốc độ xử lý.
+ *Nghịch đảo mô-đun bằng thuật toán Euclid mở rộng:* Khóa bí mật $d$ được tìm bằng cách giải phương trình đồng dư: $e dot d equiv 1 (mod phi(n))$, tương đương với phương trình vô định Bézout: $e dot d + phi(n) dot y = 1$. Thuật toán Euclid mở rộng tính toán đệ quy tìm ra phần tử nghịch đảo $d$ một cách hiệu quả trong thời gian $O(log(phi(n)))$.

*Chứng minh tính đúng đắn toán học dựa trên Định lý Euler:* \
Quá trình giải mã RSA của Bob tính toán:
$ K' = (C_"key")^d mod n = ((K^e) mod n)^d mod n = K^(e dot d) mod n $
Do $e dot d equiv 1 (mod phi(n))$, tồn tại số nguyên $k$ sao cho $e dot d = 1 + k dot phi(n)$. Với trường hợp phổ biến $gcd(K, n) = 1$, theo Định lý Euler ta có $K^(phi(n)) equiv 1 (mod n)$, suy ra:
$ K' equiv K^(1 + k dot phi(n)) equiv K dot (K^(phi(n)))^k equiv K dot 1^k equiv K (mod n) $
Ngay cả trong trường hợp hiếm gặp $gcd(K, n) != 1$ (tức $K$ là bội của $p$ hoặc $q$), kết hợp Định lý Fermat nhỏ trên từng thừa số nguyên tố $p, q$ với Định lý Số dư Trung Hoa (CRT) vẫn bảo đảm $K^(e dot d) equiv K (mod p)$ và $K^(e dot d) equiv K (mod q)$, do đó $K^(e dot d) equiv K (mod n)$. Vì khóa phiên $K$ (128-bit) thỏa mãn điều kiện biên $K < 2^(128) < n$, giá trị khôi phục $K'$ đồng nhất hoàn toàn 100% với khóa phiên $K$ ban đầu của Alice.

== Cơ chế mã hóa xác thực AES-GCM (AEAD)
Thuật toán AES-GCM theo chuẩn NIST SP 800-38D @nist_sp800_38d thực thi hai nhiệm vụ bảo vệ dữ liệu độc lập nhưng gắn kết chặt chẽ:
+ *Mã hóa dòng Counter Mode (CTR):* Với Nonce 96-bit (12 bytes), khối đếm ban đầu (Initial Counter Block) được xác định là $J_0 = "CB"_0 = "Nonce" || "00000001"_(16)$. Bản rõ $M$ được chia thành các khối 16 bytes $P_1, P_2, dots, P_m$; các khối đếm dùng để sinh dòng khóa mã hóa được tăng dần từ $J_0$ bằng phép tăng 32-bit cuối: $"CB"_i = "inc"_(32)("CB"_(i-1))$ với $i >= 1$ (tức $"CB"_1 = "Nonce" || "00000002"_(16)$, $"CB"_2 = "Nonce" || "00000003"_(16)$, ...). Dòng bản mã được tính bằng phép XOR:
  $ C_i = P_i xor "AES"_K ("CB"_i) $
  Cơ chế này loại bỏ hoàn toàn yêu cầu đệm dữ liệu (padding) và hỗ trợ tính toán song song đa luồng.
+ *Xác thực tính toàn vẹn bằng hàm băm GHASH:* Khóa băm xác thực $H = "AES"_K (0^(128))$ được sinh bằng cách mã hóa một khối toàn bit 0. Phép nhân trên trường hữu hạn Galois $"GF"(2^(128))$ được định nghĩa theo đa thức bất khả quy:
  $ f(x) = x^(128) + x^7 + x^2 + x + 1 $
  Nếu khối bản mã cuối $C_m$ chưa đủ 128 bit, nó được đệm bit 0 về bên phải để tròn 128 bit. Giá trị băm tích lũy qua từng khối bản mã là $X_i = (X_(i-1) xor C_i) dot H$ (với $X_0 = 0^(128)$). Cuối cùng, GHASH nhân thêm khối 128-bit biểu diễn độ dài tính theo bit của dữ liệu xác thực bổ sung $A$ và bản mã $C$ ($"len"_(64)(A) || "len"_(64)(C)$, với $A = emptyset$ trong hệ thống này), rồi cộng khóa vòng $J_0 = "CB"_0$ để tạo Authentication Tag:
  $ "Tag" = ((X_m xor ("len"_(64)(A) || "len"_(64)(C))) dot H) xor "AES"_K ("CB"_0) $

Đặc tính khuếch tán (Diffusion) của trường Galois bảo đảm rằng nếu kẻ tấn công sửa đổi dù chỉ duy nhất 1 bit trong bản mã trên đường truyền, giá trị băm GHASH tính toán lại tại Bob sẽ thay đổi hoàn toàn. Khi Bob đối chiếu `"Tag"_"computed"` với `"Tag"_"received"`, hệ thống phát hiện sai lệch và lập tức kích hoạt ngoại lệ `ValueError: MAC check failed`, hủy bỏ gói tin ngay tại tầng giải mã để bảo vệ dữ liệu.

== Đóng gói khung truyền thông mạng và giao thức Socket TCP
Trong môi trường truyền thông mạng, giao thức TCP là giao thức hướng luồng byte (byte stream), không bảo toàn ranh giới giữa các lần truyền dữ liệu. Hiện tượng phân mảnh (fragmentation) hoặc dính gói có thể xảy ra khi một lần đọc socket chỉ nhận được một phần của bức điện. Để khắc phục, hệ thống áp dụng cơ chế *đóng khung tiền tố độ dài (Length-Prefixed Framing)*: mỗi gói tin trước khi gửi lên kết nối mạng đều được đóng tiền tố 4 byte số nguyên không dấu theo thứ tự byte mạng Big-Endian (`!I`) quy định kích thước chính xác của payload JSON UTF-8 đi kèm (kèm giới hạn kích thước tối đa ở phía nhận để chống tràn bộ nhớ).

Cấu trúc trường dữ liệu trong JSON Envelope của gói tin PGP Hybrid được chi tiết hóa trong @tbl-packet-fields. Ở tầng Socket (`PGP_RSA_AES_Socket_3_files/`), khóa phiên mã hóa `enc_session_key` được truyền dưới dạng số nguyên lớn (hoặc chuỗi hex ở CLI demo), trong khi các thành phần nhị phân `nonce`, `ciphertext` và `auth_tag` được mã hóa Base64 để truyền tải an toàn trong JSON UTF-8 (riêng gói tin gửi lên server có thêm trường `"action": "SEND_MESSAGE"`).

#figure(
  report-table(
    columns: (1.1fr, 1.1fr, 1.1fr, 1.8fr),
    headers: ("Tên trường JSON", "Kích thước gốc", "Định dạng truyền tải", "Mô tả vai trò mật mã"),
    rows: (
      ([`enc_session_key`], [256 / 512 bit], [Số nguyên lớn / Hex], [Khóa phiên $K$ (128-bit) đã được mã hóa bằng Public Key của Bob qua RSA.]),
      ([`nonce`], [12 bytes (96 bit)], [Base64 / Hex], [Vector khởi tạo ngẫu nhiên dùng một lần bảo đảm tính ngẫu nhiên cho AES-GCM.]),
      ([`ciphertext`], [Biến thiên ($|M|$ bytes)], [Base64 / Hex], [Bản mã của thông điệp $M$ tạo ra từ thuật toán đối xứng AES dòng CTR Mode.]),
      ([`auth_tag`], [16 bytes (128 bit)], [Base64 / Hex], [Mã xác thực thông điệp sinh bởi hàm băm GHASH trên trường Galois $"GF"(2^(128))$.]),
    ),
  ),
  caption: [Cấu trúc trường dữ liệu của gói tin PGP Hybrid qua mạng.],
) <tbl-packet-fields>

Bên cạnh đóng khung dữ liệu, hệ thống thiết lập cơ chế xác minh dấu vân tay số (SHA-256 Fingerprint) cho khóa công khai của Bob. Trước khi gửi dữ liệu, Alice và Bob có thể đối chiếu chuỗi băm 64 ký tự hex sinh bởi hàm:
$ "fingerprint"("pub_key") = "SHA256"("RSA:" || e || ":" || n) $
Cơ chế này giúp bên gửi xác minh chắc chắn rằng khóa công khai nhận được đúng là của người nhận hợp lệ, phòng tránh cuộc tấn công kẻ đứng giữa (Man-in-the-Middle) giả mạo danh tính.

Quy cách đóng gói khung truyền thông và luồng phân tích cú pháp tương ứng tại bộ nhận của Bob được thể hiện trực quan trong @fig-packet-layout.

#v(0.3em)
#align(center)[
  #fig-packet-layout <fig-packet-layout>
]
#v(0.3em)
