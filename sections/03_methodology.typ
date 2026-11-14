#import "../figures.typ": fig-sequence-interaction, fig-packet-layout, fig-aes-spn-flow, fig-aes-gcm-flow
#import "../styles.typ": report-table

= Phương pháp thực hiện

== Quy trình mã hóa lai và phân vai thuật toán
Trong kiến trúc truyền thông giữa Alice (bên gửi) và Bob (bên nhận), mỗi lớp mật mã đảm nhiệm một vai trò độc lập: RSA giải quyết bài toán trao đổi khóa qua kênh mạng không tin cậy, còn AES-GCM bảo vệ nội dung thông điệp và chống sửa đổi dữ liệu. Quy trình năm giai đoạn được tóm tắt trong @tbl-hybrid-process và minh họa tuần tự tại @fig-sequence-interaction.

#figure(
  report-table(
    columns: (1.0fr, 1.8fr, 1.8fr),
    headers: ("Giai đoạn", "Phía Alice (Người gửi)", "Phía Bob (Người nhận)"),
    rows: (
      ([GĐ 0: Khởi tạo khóa], [Nhận khóa công khai $(e, n)$ của Bob và đối chiếu dấu vân tay SHA-256.], [Sinh cặp khóa RSA gồm khóa công khai $(e, n)$ và khóa bí mật $(d, n)$.]),
      ([GĐ 1: Sinh khóa phiên], [Dùng bộ sinh số ngẫu nhiên an toàn tạo khóa phiên $K$ dài 128 bit (16 byte).], [Mở cổng mạng chờ nhận kết nối từ phía gửi.]),
      ([GĐ 2: Mã hóa hai lớp], [- Dùng AES-GCM mã hóa $M$ bằng $K$ tạo bản mã dữ liệu, vector khởi tạo và thẻ xác thực. \ - Dùng RSA mã hóa $K$ bằng $(e, n)$ tạo bản mã khóa phiên.], [Không thực hiện.]),
      ([GĐ 3: Đóng gói & Gửi], [Đóng gói bốn thành phần vào cấu trúc JSON kèm tiền tố 4 byte độ dài và gửi qua TCP.], [Đọc 4 byte độ dài rồi nhận trọn vẹn phần thân gói tin vào bộ nhớ đệm.]),
      ([GĐ 4: Giải mã & Kiểm tra], [Chờ phản hồi trạng thái xử lý từ bên nhận.], [- Dùng khóa bí mật $d$ giải mã RSA khôi phục khóa phiên $K'$. \ - Tính lại thẻ xác thực bằng GHASH; nếu khớp mới giải mã ra bản rõ $M'$.]),
    ),
  ),
  caption: [Quy trình thực hiện mã hóa lai giữa Alice và Bob],
) <tbl-hybrid-process>

#v(0.3em)
#align(center)[
  #fig-sequence-interaction <fig-sequence-interaction>
]
#v(0.3em)

== Cơ sở toán học và kích thước khóa của RSA
Hệ mật RSA sử dụng trong đề tài thực hiện phép tính số học trên số nguyên lớn theo bốn bước:
+ *Sinh số nguyên tố xác suất Miller–Rabin:* Hai số nguyên tố phân biệt $p$ và $q$ được kiểm tra bằng giải thuật Miller–Rabin @rabin1980 với $k = 20$ vòng lặp ngẫu nhiên, cho xác suất nhầm hợp số nhỏ hơn $(1/4)^(20) approx 9.09 times 10^(-13)$.
+ *Tính modulus $n$ và hàm Euler:* Modulus hệ thống được tính theo @eq-rsa-modulus và hàm phi Euler theo @eq-rsa-phi:
  $ n = p dot q $ <eq-rsa-modulus>
  $ phi(n) = (p - 1)(q - 1) $ <eq-rsa-phi>
+ *Chọn số mũ công khai Fermat:* Chọn cố định $e = 65537 = 2^(16) + 1$ vì biểu diễn nhị phân $10000000000000001_2$ chỉ có hai bit 1, giúp phép bình phương và nhân liên tiếp chỉ cần 16 phép bình phương và 1 phép nhân theo mô-đun.
+ *Tìm khóa bí mật bằng giải thuật Euclid mở rộng:* Giải phương trình đồng dư ở @eq-rsa-inverse để tìm $d$ trong thời gian $O(log(phi(n)))$:
  $ e dot d equiv 1 (mod phi(n)) $ <eq-rsa-inverse>

Toàn bộ hệ thống thống nhất dùng một cấu hình kích thước bit duy nhất cho cả mô phỏng thuật toán và truyền thông mạng LAN, với ý nghĩa từng đại lượng như sau:
- Mỗi số nguyên tố $p, q$ có kích thước *256 bit*, nên modulus $n = p dot q$ có kích thước *512 bit*.
- Khóa phiên AES gốc $K$ luôn có kích thước cố định *128 bit* ($K < 2^(128) < n$).
- Bản mã khóa phiên $C_"key"$ sau khi mã hóa bằng RSA có kích thước *512 bit* (bằng kích thước modulus $n$).

Quá trình mã hóa và giải mã RSA tại @eq-rsa-enc và @eq-rsa-dec thỏa mãn tính đúng đắn nhờ Định lý Euler:
$ C_"key" = K^e mod n $ <eq-rsa-enc>
$ K' = (C_"key")^d mod n = K^(e dot d) mod n $ <eq-rsa-dec>

Vì $e dot d = 1 + k dot phi(n)$, khi $gcd(K, n) = 1$ thì $K^(phi(n)) equiv 1 (mod n)$, nên $K' equiv K dot 1^k equiv K (mod n)$. Trường hợp hiếm gặp $gcd(K, n) != 1$ ($K$ chia hết cho $p$ hoặc $q$), kết hợp Định lý Fermat nhỏ trên từng thừa số $p, q$ và Định lý Số dư Trung Hoa (CRT) vẫn bảo đảm $K^(e dot d) equiv K (mod n)$.

== Lý thuyết và lưu đồ thuật toán mã hóa khối AES-128
AES là thuật toán mã hóa khối đối xứng hoạt động trên từng khối dữ liệu 128 bit (16 byte), được tổ chức thành ma trận trạng thái kích thước $4 times 4$ byte. Với khóa phiên $K$ dài 128 bit, dữ liệu đi qua bước cộng khóa khởi tạo và 10 vòng biến đổi theo cấu trúc mạng thay thế – hoán vị (SPN) như trình bày trong @fig-aes-spn-flow.

#v(0.3em)
#align(center)[
  #fig-aes-spn-flow <fig-aes-spn-flow>
]
#v(0.3em)

Mỗi vòng biến đổi của AES thực hiện bốn phép toán đại số cơ bản sau:
- *Thế phi tuyến (`SubBytes`):* Thay thế từng byte trong ma trận trạng thái bằng một byte tương ứng trong bảng thế S-box cố định nhằm tạo tính phi tuyến, chống lại phân tích mật mã tuyến tính và vi sai.
- *Dịch hàng (`ShiftRows`):* Dịch vòng sang trái từng hàng của ma trận trạng thái (hàng 0 giữ nguyên, hàng 1 dịch 1 byte, hàng 2 dịch 2 byte, hàng 3 dịch 3 byte) để khuếch tán dữ liệu theo chiều ngang.
- *Trộn cột (`MixColumns`):* Nhân từng cột của ma trận trạng thái với một đa thức cố định trên trường hữu hạn $"GF"(2^8)$ nhằm trộn đều ảnh hưởng của từng byte trên toàn cột (phép toán này được bỏ qua ở vòng cuối thứ 10).
- *Cộng khóa vòng (`AddRoundKey`):* Thực hiện phép cộng loại trừ theo từng bit (XOR) giữa ma trận trạng thái hiện tại với khóa vòng $K_r$ sinh ra từ thuật toán mở rộng khóa.

== Chế độ mã hóa xác thực AES-GCM (AEAD)
AES-GCM thuộc họ mật mã xác thực có dữ liệu bổ sung AEAD (*Authenticated Encryption with Associated Data*), cho phép bảo vệ đồng thời tính bí mật của bản rõ và tính toàn vẹn của cả bản mã lẫn dữ liệu đi kèm (nếu có). Lưu đồ nguyên lý của AES-GCM theo chuẩn NIST SP 800-38D @nist_sp800_38d được thể hiện trong @fig-aes-gcm-flow.

#v(0.3em)
#align(center)[
  #fig-aes-gcm-flow <fig-aes-gcm-flow>
]
#v(0.3em)

Với vector khởi tạo Nonce dài 96 bit (12 byte), khối đếm ban đầu $J_0$ được tạo theo @eq-gcm-j0 và các khối đếm mã hóa tiếp theo tăng dần 32 bit cuối theo @eq-gcm-cbi:
$ J_0 = "CB"_0 = "Nonce" || "00000001"_(16) $ <eq-gcm-j0>
$ "CB"_i = "inc"_(32)("CB"_(i-1)) = "Nonce" || (i + 1)_(32) quad (i >= 1) $ <eq-gcm-cbi>

Bản rõ $M$ được chia thành các khối 128 bit $P_1, P_2, dots, P_m$ và mã hóa dòng theo chế độ bộ đếm (CTR) bằng @eq-gcm-ctr, loại bỏ nhu cầu đệm khối dữ liệu:
$ C_i = P_i xor "AES"_K ("CB"_i) $ <eq-gcm-ctr>

Song song với quá trình tạo bản mã, hàm băm GHASH tạo khóa băm $H = "AES"_K (0^(128))$ và thực hiện phép nhân tích lũy trên trường Galois $"GF"(2^(128))$ theo đa thức bất khả quy ở @eq-gcm-poly:
$ f(x) = x^(128) + x^7 + x^2 + x + 1 $ <eq-gcm-poly>

Nếu khối bản mã cuối $C_m$ chưa đủ 128 bit, hệ thống đệm thêm các bit 0 về bên phải. Giá trị băm tích lũy qua từng khối là $X_i = (X_(i-1) xor C_i) dot H$ với $X_0 = 0^(128)$. Cuối cùng, khối độ dài 128 bit chứa độ dài tính theo bit của dữ liệu bổ sung $A$ (rỗng trong hệ thống này) và bản mã $C$ được nhân thêm để tạo thẻ xác thực 128-bit tại @eq-gcm-tag:
$ "Tag" = ((X_m xor ("len"_(64)(A) || "len"_(64)(C))) dot H) xor "AES"_K (J_0) $ <eq-gcm-tag>

Nhờ tính khuếch tán trên trường $"GF"(2^(128))$, chỉ cần 1 bit trong bản mã bị thay đổi trên đường truyền, thẻ xác thực tính lại tại bên nhận sẽ khác hoàn toàn với thẻ xác thực nhận được. Khi phát hiện sai lệch, bên nhận lập tức báo lỗi kiểm tra toàn vẹn và hủy gói tin thay vì giải mã ra dữ liệu sai.

== Đóng gói khung truyền thông Socket TCP và xác thực dấu vân tay
Giao thức TCP truyền dữ liệu theo luồng byte liên tục nên có thể xảy ra hiện tượng phân mảnh hoặc dính gói. Để phân tách ranh giới từng bức điện, bên gửi gắn tiền tố 4 byte số nguyên không dấu theo thứ tự byte mạng (Big-Endian) quy định kích thước chính xác của gói JSON đi kèm. Bốn thành phần mật mã trong gói tin được mô tả tại @tbl-packet-fields và quy trình phân tích tại bên nhận thể hiện trong @fig-packet-layout.

#figure(
  report-table(
    columns: (1.2fr, 1.1fr, 1.1fr, 1.7fr),
    headers: ("Thành phần", "Kích thước gốc", "Biểu diễn truyền tải", "Vai trò mật mã"),
    rows: (
      ([Khóa phiên mã hóa], [512 bit], [Số nguyên / Hex], [Khóa phiên 128-bit đã mã hóa bằng khóa công khai của Bob qua RSA.]),
      ([Vector khởi tạo], [12 byte (96 bit)], [Base64 / Hex], [Giá trị ngẫu nhiên dùng một lần cho chế độ AES-GCM.]),
      ([Bản mã dữ liệu], [Bằng độ dài $M$], [Base64 / Hex], [Nội dung thông điệp $M$ đã mã hóa đối xứng bằng AES-CTR.]),
      ([Thẻ xác thực], [16 byte (128 bit)], [Base64 / Hex], [Mã kiểm tra toàn vẹn sinh bởi hàm băm GHASH.]),
    ),
  ),
  caption: [Cấu trúc bốn thành phần mật mã trong gói tin truyền qua mạng],
) <tbl-packet-fields>

Để phòng ngừa tấn công giả mạo khóa công khai (tấn công kẻ đứng giữa), hệ thống tính dấu vân tay số dài 64 ký tự thập lục phân theo hàm băm SHA-256 ở @eq-fingerprint để Alice và Bob đối chiếu qua kênh ngoài trước khi truyền tin:
$ "fingerprint"("khóa công khai") = "SHA256"("RSA:" || e || ":" || n) $ <eq-fingerprint>

#v(0.3em)
#align(center)[
  #fig-packet-layout <fig-packet-layout>
]
#v(0.3em)
