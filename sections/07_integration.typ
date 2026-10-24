#import "../styles.typ": report-table
#import "../figures.typ": fig-packet-layout

= Tích hợp RSA và AES trong Hybrid Encryption

Trong mô hình mã hóa lai hoàn chỉnh, RSA tuyệt đối không tham gia trực tiếp vào việc mã hóa khối dữ liệu thông điệp dài mà đóng vai trò là "két sắt" bảo vệ Session Key. AES đảm nhận toàn bộ việc mã hóa dữ liệu tốc độ cao.

== Cấu trúc khung gói tin (Packet Framing & Offset)

Khi truyền tải qua mạng, dòng dữ liệu PGP được cấu trúc thành các trường liên tục với vị trí byte (Offset) và kích thước xác định, cho phép bộ giải mã ở phía nhận phân tích cú pháp (parse) chính xác:

#v(0.3em)
#align(center)[
  #fig-packet-layout
]
#v(0.3em)

Trong cấu trúc gói tin trên, hai thành phần bổ trợ thiết yếu của chế độ mã hóa xác thực AES-GCM gồm có:
- *Vector khởi tạo (IV - Initialization Vector / Nonce):* Là một chuỗi ngẫu nhiên dài 12 bytes (96 bits) được sinh mới cho mỗi thông điệp. IV đóng vai trò ngăn chặn việc hai thông điệp có nội dung giống nhau sinh ra cùng một bản mã khi dùng chung khóa phiên. IV không cần giữ bí mật và được truyền công khai trong gói tin, nhưng tuyệt đối không được tái sử dụng cùng một cặp $(K, "IV")$.
- *Mã xác thực thông điệp (Authentication Tag):* Là một thẻ kiểm thực mật mã dài 16 bytes (128 bits) được hàm băm GHASH tự động tính toán từ toàn bộ dữ liệu mã hóa. Tag hoạt động như một "tem niêm phong điện tử": nếu kẻ tấn công sửa đổi bất kỳ bit nào trên Ciphertext khi gói tin di chuyển trên mạng, phép xác minh Tag tại phía Bob sẽ thất bại ngay lập tức, giúp bảo toàn tính toàn vẹn dữ liệu.

== Cơ sở toán học của AES-GCM (AEAD)

Chế độ AES-GCM kết hợp hai nền tảng số học để đạt được tính bảo mật và toàn vẹn song song:

1. *Mã hóa dòng CTR Mode:* Các khối bản rõ $P_i$ được mã hóa qua phép XOR với chuỗi khóa giả ngẫu nhiên sinh bởi thuật toán AES:
$ C_i = P_i xor "AES"_K ("CB"_i) $
với $"CB"_i$ là giá trị Counter Block tính từ Nonce (12 bytes) nối với bộ đếm 32-bit tăng dần.

2. *Xác thực toàn vẹn bằng hàm băm GHASH:* Giá trị kiểm thực Authentication Tag được tính trên trường hữu hạn Galois $FF_(2^(128))$ dựa trên đa thức bất khả quy:
$ f(x) = x^(128) + x^7 + x^2 + x + 1 $
Khóa băm xác thực $H = "AES"_K (0^(128))$ được dùng để thực hiện phép nhân đa thức lặp Horner trên $FF_(2^(128))$ qua từng khối bản mã $C_i$:
$ X_i = (X_(i-1) xor C_i) dot H $
Giá trị Authentication Tag cuối cùng:
$ "Tag" = X_m xor "AES"_K ("CB"_0) $
Nếu kẻ tấn công can thiệp bất kỳ bit nào trên Ciphertext ($C_i arrow.r C'_i$), giá trị băm $X'_m$ sẽ biến đổi hoàn toàn theo tính chất khuếch tán của trường Galois, làm phép so sánh Tag tại phía Bob thất bại lập tức.

== Phân công nhiệm vụ hai phía

#align(center)[
  #report-table(
    columns: (1fr, 1fr),
    headers: ("Phía Alice (Mã hóa)", "Phía Bob (Giải mã)"),
    rows: (
      (
        [
          - Sinh Session Key ngẫu nhiên (128-bit).
          - Dùng AES-GCM mã hóa thông điệp bằng Session Key $\to$ tạo ra Ciphertext, Nonce và Authentication Tag.
          - Dùng Public Key RSA của Bob mã hóa Session Key $\to$ Encrypted Key.
          - Ghép 4 thành phần thành gói tin duy nhất gửi đi.
        ],
        [
          - Tiếp nhận toàn bộ gói tin từ Alice qua mạng.
          - Dùng Private Key RSA của Bob giải mã Session Key.
          - Dùng Session Key và Nonce giải mã Ciphertext bằng AES-GCM.
          - Đối chiếu Authentication Tag để kiểm tra tính toàn vẹn và chống giả mạo trước khi nhận thông điệp gốc.
        ]
      ),
    )
  )
]

== Luồng điều khiển của mô-đun tích hợp

Tiến trình xử lý trong mã nguồn `algorithms/hybrid_pgp.py` được tổ chức thành hai luồng độc lập tương ứng với hai hàm nghiệp vụ:

1. *Hàm đóng gói mã hóa (`alice_encrypt_package`):*
   - Khởi tạo khóa phiên ngẫu nhiên $K$ độ dài 128-bit (`os.urandom(16)`).
   - Mã hóa bản rõ $M$ bằng AES-GCM với khóa $K$, trích xuất bộ ba: Ciphertext ($C_("data")$), Nonce (IV 12 bytes) và Authentication Tag (16 bytes).
   - Dùng Public Key của Bob $(e_B, n)$ mã hóa khóa phiên $K$ theo thuật toán RSA: $C_("key") = K^{e_B} mod n$.
   - Ghép 4 thành phần thành cấu trúc payload duy nhất để truyền qua mạng.

2. *Hàm tiếp nhận và giải mã (`bob_decrypt_package`):*
   - Tách gói tin nhận được thành 4 thành phần theo cấu trúc offset đã định nghĩa ở Hình 4.
   - Dùng Private Key của Bob $(d_B, n)$ giải mã trường $C_("key")$ để khôi phục lại khóa phiên $K$.
   - Nạp $K$, Nonce và Authentication Tag vào bộ giải mã AES-GCM.
   - Thực hiện giải mã và kiểm tra mã xác thực toàn vẹn: nếu dữ liệu bị thay đổi, ngoại lệ `ValueError` lập tức được kích hoạt để hủy thông điệp; ngược lại giải mã thành công bản rõ $M$.

== Mã nguồn tích hợp Hybrid PGP (`algorithms/hybrid_pgp.py`)

#raw(read("../algorithms/hybrid_pgp.py"), lang: "python")

#import "../components.typ": info-box
#info-box(title: "Lưu ý kỹ thuật và tính minh bạch")[
  - *Chế độ AES-GCM:* Sử dụng *Nonce* (Number used once) nhằm triệt tiêu hiện tượng trùng lặp khối mã và sử dụng *Authentication Tag* (128-bit) để bảo đảm toàn vẹn dữ liệu.
  - *Ranh giới triển khai:* Nhóm tự lập trình thuật toán số học RSA để nắm vững nguyên lý toán học, đồng thời tích hợp thư viện AES chuẩn công nghiệp (`Cryptodome`) để bảo đảm hiệu năng và tính an toàn mật mã.
]
