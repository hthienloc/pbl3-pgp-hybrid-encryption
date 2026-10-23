#import "@preview/fletcher:0.5.6" as fletcher: diagram, node, edge

= Tích hợp RSA và AES trong Hybrid Encryption

Trong mô hình mã hóa lai hoàn chỉnh, RSA tuyệt đối không tham gia trực tiếp vào việc mã hóa khối dữ liệu thông điệp dài mà đóng vai trò là "két sắt" bảo vệ khóa đối xứng (Session Key). AES đảm nhận toàn bộ việc mã hóa dữ liệu tốc độ cao.

== Cấu trúc gói tin dữ liệu đóng gói (Packet Payload)
Khi dữ liệu được truyền tải qua kênh mạng theo mô hình PGP (tương ứng với các gói PKESK và SEIPD trong RFC 4880), thông điệp đóng gói gồm 4 thành phần thiết yếu sau:

#v(0.3em)
#align(center)[
  #figure(
    diagram(
      spacing: (0mm, 0mm),
      node-stroke: 1pt + rgb("#334155"),
      node-corner-radius: 3pt,

      node((0, 0), align(center)[*Encrypted Session Key*\ #text(size: 8.5pt)[Mã hóa bằng RSA Bob]\ #text(size: 8pt, fill: rgb("#475569"))[(PKESK Packet)]], fill: rgb("#ede9fe"), stroke: 1pt + rgb("#7c3aed"), width: 3.5cm, height: 1.5cm),
      node((1, 0), align(center)[*Nonce / IV*\ #text(size: 8.5pt)[Giá trị ngẫu nhiên]\ #text(size: 8pt, fill: rgb("#475569"))[(12 bytes AES-GCM)]], fill: rgb("#fef3c7"), stroke: 1pt + rgb("#f59e0b"), width: 3.0cm, height: 1.5cm),
      node((2, 0), align(center)[*AES Ciphertext*\ #text(size: 8.5pt)[Bản mã dữ liệu lớn]\ #text(size: 8pt, fill: rgb("#475569"))[(SEIPD Packet)]], fill: rgb("#dbeafe"), stroke: 1pt + rgb("#2563eb"), width: 4.0cm, height: 1.5cm),
      node((3, 0), align(center)[*Auth Tag*\ #text(size: 8.5pt)[Mã kiểm thực MAC]\ #text(size: 8pt, fill: rgb("#475569"))[(16 bytes Integrity)]], fill: rgb("#dcfce7"), stroke: 1pt + rgb("#16a34a"), width: 3.2cm, height: 1.5cm),
    ),
    caption: [Cấu trúc gói tin dữ liệu hoàn chỉnh truyền qua mạng],
  )
]
#v(0.3em)

== Phân công nhiệm vụ hai phía

#align(center)[
  #table(
    columns: (1fr, 1fr),
    fill: (x, y) => if y == 0 { rgb("#e0e7ff") } else { none },
    stroke: 0.5pt + rgb("#cbd5e1"),
    inset: 9pt,
    [*Phía Alice (Mã hóa)*], [*Phía Bob (Giải mã)*],
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
  )
]

== Mã nguồn tích hợp then chốt (`src/hybrid_demo.py`)

```python
# Phía Alice: Mã hóa dữ liệu bằng AES-GCM và bảo vệ khóa phiên bằng RSA
session_key = os.urandom(16)
cipher_aes = AES.new(session_key, AES.MODE_GCM)
ciphertext, auth_tag = cipher_aes.encrypt_and_digest(plaintext)
enc_session_key = rsa_encrypt(bob_pub_key, int.from_bytes(session_key, 'big') % bob_pub_key[1])

# Phía Bob: Dùng Private Key RSA khôi phục khóa phiên và xác thực Tag
recovered_key = rsa_decrypt(bob_priv_key, enc_session_key)
cipher_bob = AES.new(session_key, AES.MODE_GCM, nonce=package["nonce"])
plaintext_recovered = cipher_bob.decrypt_and_verify(ciphertext, auth_tag)
```

#import "../components.typ": info-box
#info-box(title: "Lưu ý kỹ thuật và tính minh bạch")[
  - *Chế độ AES-GCM:* Sử dụng *Nonce* (Number used once) nhằm triệt tiêu hiện tượng trùng lặp khối mã và sử dụng *Authentication Tag* (128-bit) để bảo đảm toàn vẹn dữ liệu.
  - *Ranh giới triển khai:* Nhóm tự lập trình thuật toán số học RSA để nắm vững nguyên lý toán học, đồng thời tích hợp thư viện AES chuẩn công nghiệp (`Cryptodome`) để bảo đảm hiệu năng và tính an toàn mật mã.
]
