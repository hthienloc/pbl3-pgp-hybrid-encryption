#import "@preview/fletcher:0.5.6" as fletcher: diagram, node, edge

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
      + Sinh ngẫu nhiên Session Key ($K$).
      + Sử dụng AES cùng $K$ để mã hóa thông điệp thành $C_("data")$.
      + Dùng Public Key RSA của Bob để mã hóa $K$ thành $C_("key")$.
      + Đóng gói ${C_("key"), C_("data")}$ (kèm IV/Nonce và Tag) gửi cho Bob.
    ],
    [
      + Tiếp nhận gói dữ liệu mã hóa từ Alice qua kênh mạng.
      + Dùng Private Key RSA của Bob để giải mã $C_("key")$, khôi phục $K$.
      + Dùng AES cùng Session Key $K$ đã khôi phục để giải mã $C_("data")$.
      + Kiểm tra tính toàn vẹn và xác thực thông qua Authentication Tag.
      + Nhận lại thông điệp gốc chính xác.
    ]
  )
]

== Sơ đồ tuần tự tương tác (Sequence Diagram)

#v(0.5em)
#align(center)[
  #figure(
    diagram(
      spacing: (28mm, 11mm),
      node-stroke: 0.8pt + rgb("#3b82f6"),
      node-fill: rgb("#eff6ff"),
      node-corner-radius: 4pt,
      edge-stroke: 0.8pt + rgb("#475569"),

      // Các thực thể
      node((0, 0), align(center)[*Alice*\ (Người gửi)], name: <alice>, fill: rgb("#dbeafe"), stroke: 1pt + rgb("#2563eb")),
      node((1, 0), align(center)[*Kênh truyền mạng*\ (Gói tin đóng gói)], name: <channel>, fill: rgb("#f1f5f9"), stroke: 1pt + rgb("#64748b")),
      node((2, 0), align(center)[*Bob*\ (Người nhận)], name: <bob>, fill: rgb("#ede9fe"), stroke: 1pt + rgb("#7c3aed")),

      // Trục thời gian sống (Lifelines)
      node((0, 4.5), [], name: <alice_end>, stroke: none, fill: none),
      node((1, 4.5), [], name: <channel_end>, stroke: none, fill: none),
      node((2, 4.5), [], name: <bob_end>, stroke: none, fill: none),

      edge(<alice>, <alice_end>, "--", stroke: 0.5pt + rgb("#94a3b8")),
      edge(<channel>, <channel_end>, "--", stroke: 0.5pt + rgb("#94a3b8")),
      edge(<bob>, <bob_end>, "--", stroke: 0.5pt + rgb("#94a3b8")),

      // Các bước của Alice
      node((0, 0.9), align(left)[*1. Sinh khóa* $K$\ ngẫu nhiên], name: <a1>, stroke: 0.5pt + rgb("#f59e0b"), fill: rgb("#fef3c7"), shape: rect),
      node((0, 1.8), align(left)[*2. Mã hóa AES*:\ $C_("data") = "AES"_K (M)$], name: <a2>, stroke: 0.5pt + rgb("#3b82f6"), fill: rgb("#eff6ff"), shape: rect),
      node((0, 2.7), align(left)[*3. Mã hóa RSA*:\ $C_("key") = "RSA"_(E_B)(K)$], name: <a3>, stroke: 0.5pt + rgb("#7c3aed"), fill: rgb("#f5f3ff"), shape: rect),

      // Truyền gói tin qua kênh mạng
      edge((0, 3.2), (1, 3.2), "-|>", [Gửi gói tin], label-side: left),
      node((1, 3.2), align(center)[*Gói tin:*\ {$C_("key"), "IV", C_("data"), "Tag"$\}], name: <pkg>, stroke: 0.8pt + rgb("#16a34a"), fill: rgb("#dcfce7"), shape: rect),
      edge((1, 3.2), (2, 3.2), "-|>", [Tiếp nhận], label-side: left),

      // Các bước của Bob
      node((2, 3.7), align(left)[*4. Giải mã RSA*:\ $K = "RSA"_(D_B)(C_("key"))$], name: <b1>, stroke: 0.5pt + rgb("#7c3aed"), fill: rgb("#f5f3ff"), shape: rect),
      node((2, 4.5), align(left)[*5. Giải mã AES & Xác thực Tag*:\ $M = "AES"_K (C_("data"))$], name: <b2>, stroke: 0.5pt + rgb("#16a34a"), fill: rgb("#dcfce7"), shape: rect),
    ),
    caption: [Sơ đồ tuần tự quy trình truyền thông mã hóa lai PGP giữa Alice và Bob],
  )
]
#v(0.5em)

== Chi tiết luồng xử lý
+ *Giai đoạn chuẩn bị phía gửi:* Alice tạo một Session Key đối xứng ngẫu nhiên chỉ có giá trị cho một lần truyền thông duy nhất. Khóa này bảo đảm tính bí mật ngay cả khi các phiên trước đó bị rò rỉ.
+ *Mã hóa dữ liệu:* Thông điệp được mã hóa với AES (chế độ AES-GCM kèm Nonce và Authentication Tag).
+ *Đóng gói & Chuyển giao:* Gói tin truyền trên mạng bao gồm Session Key đã được mã hóa bằng Public Key RSA của Bob và bản mã dữ liệu.
+ *Khôi phục dữ liệu phía nhận:* Bob nhận gói tin, sử dụng Private Key tương ứng của mình để giải mã Session Key, sau đó dùng Session Key đó giải mã bản tin AES và kiểm tra tính hợp lệ của Authentication Tag.
