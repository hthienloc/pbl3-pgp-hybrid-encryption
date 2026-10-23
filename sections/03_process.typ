= Quy trình Hybrid Encryption

Quy trình vận hành mã hóa lai giữa phía gửi (Alice) và phía nhận (Bob) gồm hai chu trình rõ ràng và chặt chẽ:

#align(center)[
  #table(
    columns: (1fr, 1fr),
    fill: (x, y) => if y == 0 { rgb("#dbeafe") } else { none },
    stroke: 0.5pt + rgb("#bfdbfe"),
    inset: 10pt,
    [*ALICE – Phía mã hóa*], [*BOB – Phía giải mã*],
    [
      + Chuẩn bị thông điệp gốc ($M$).
      + Sinh ngẫu nhiên khóa phiên ($K_("session")$).
      + Sử dụng AES cùng $K_("session")$ để mã hóa thông điệp thành $C_("data")$.
      + Dùng Public Key RSA của Bob để mã hóa $K_("session")$ thành $C_("key")$.
      + Đóng gói ${C_("key"), C_("data")}$ (kèm tham số bảo mật) và gửi cho Bob.
    ],
    [
      + Tiếp nhận gói dữ liệu mã hóa từ Alice.
      + Dùng Private Key RSA của Bob để giải mã $C_("key")$, khôi phục $K_("session")$.
      + Dùng AES cùng $K_("session")$ đã khôi phục để giải mã $C_("data")$.
      + Kiểm tra tính toàn vẹn / xác thực (nếu dùng chế độ có MAC như GCM).
      + Nhận lại thông điệp gốc chính xác.
    ]
  )
]

== Chi tiết luồng xử lý
+ *Giai đoạn chuẩn bị phía gửi:* Alice tạo một khóa phiên đối xứng ngẫu nhiên chỉ có giá trị cho một lần truyền thông duy nhất. Khóa này bảo đảm tính bí mật ngay cả khi các phiên trước đó bị rò rỉ.
+ *Mã hóa dữ liệu:* Thông điệp được mã hóa với AES (thường là chế độ GCM hoặc CBC có kèm IV/Nonce).
+ *Đóng gói & Chuyển giao:* Gói tin truyền trên mạng bao gồm khóa phiên đã được mã hóa bằng khóa công khai RSA của Bob và bản mã dữ liệu.
+ *Khôi phục dữ liệu phía nhận:* Bob nhận gói tin, sử dụng khóa riêng tương ứng với khóa công khai của mình để giải mã khóa phiên, sau đó dùng khóa phiên đó giải mã bản tin AES.
