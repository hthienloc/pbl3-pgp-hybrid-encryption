#import "../styles.typ": report-table
#import "../figures.typ": fig-sequence-interaction

= Quy trình Hybrid Encryption

#align(center)[
  #report-table(
    columns: (1fr, 1fr),
    headers: ("Phía Alice (Mã hóa)", "Phía Bob (Giải mã)"),
    rows: (
      (
        [
          + Nhận Public Key $(e_B, n)$ của Bob từ kênh công khai.
          + Sinh Session Key ($K$) và vector khởi tạo ($"IV"$).
          + Dùng AES-GCM mã hóa: $(C_("data"), "Tag") = "AES"_K (M, "IV")$.
          + Dùng Public Key Bob: $C_("key") = "RSA"_(e_B)(K)$.
          + Ghép gói tin $\{C_("key"), "IV", C_("data"), "Tag"\}$ và gửi qua mạng.
        ],
        [
          + *Khởi tạo:* Bob sinh cặp khóa RSA $(e_B, n)$ & $(d_B, n)$, công khai $(e_B, n)$.
          + Nhận gói tin PGP từ Alice.
          + Dùng Private Key: $K = "RSA"_(d_B)(C_("key"))$.
          + Đối chiếu $"Tag"$ để xác thực toàn vẹn bản mã.
          + Dùng $K$ và $"IV"$ giải mã: $M = "AES"_K (C_("data"), "IV")$.
        ]
      ),
    )
  )
]

== Sơ đồ tuần tự tương tác

#align(center)[
  #fig-sequence-interaction
]
