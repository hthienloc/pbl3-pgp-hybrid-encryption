#import "@preview/fletcher:0.5.6" as fletcher: diagram, node, edge

= Quy trình Hybrid Encryption

Quy trình truyền tin an toàn giữa Alice (gửi) và Bob (nhận) gồm các bước sau:

#align(center)[
  #table(
    columns: (1fr, 1fr),
    fill: (x, y) => if y == 0 { rgb("#dbeafe") } else { none },
    stroke: 0.5pt + rgb("#bfdbfe"),
    inset: 9pt,
    [*Phía Alice (Mã hóa)*], [*Phía Bob (Giải mã)*],
    [
      + Sinh Session Key ngẫu nhiên ($K$).
      + Dùng AES mã hóa dữ liệu: $C_("data") = "AES"_K (M)$.
      + Dùng Public Key Bob mã hóa $K$: $C_("key") = "RSA"_(E_B)(K)$.
      + Ghép gói tin và gửi cho Bob.
    ],
    [
      + Nhận gói tin từ Alice qua mạng.
      + Dùng Private Key Bob giải mã lấy lại: $K = "RSA"_(D_B)(C_("key"))$.
      + Dùng $K$ giải mã dữ liệu: $M = "AES"_K (C_("data"))$.
      + Kiểm tra tính toàn vẹn qua Authentication Tag.
    ]
  )
]

== Sơ đồ tuần tự tương tác (Sequence Diagram)

#v(0.3em)
#align(center)[
  #figure(
    diagram(
      spacing: (28mm, 9mm),
      node-stroke: 0.8pt + rgb("#3b82f6"),
      node-fill: rgb("#eff6ff"),
      node-corner-radius: 4pt,
      edge-stroke: 0.8pt + rgb("#475569"),

      node((0, 0), align(center)[*Alice*\ (Người gửi)], name: <alice>, fill: rgb("#dbeafe"), stroke: 1pt + rgb("#2563eb")),
      node((1, 0), align(center)[*Kênh mạng*\ (Gói tin)], name: <channel>, fill: rgb("#f1f5f9"), stroke: 1pt + rgb("#64748b")),
      node((2, 0), align(center)[*Bob*\ (Người nhận)], name: <bob>, fill: rgb("#ede9fe"), stroke: 1pt + rgb("#7c3aed")),

      edge(<alice>, (0, 0.6), "--", stroke: 0.5pt + rgb("#94a3b8")),
      edge((0, 1.3), (0, 1.5), "--", stroke: 0.5pt + rgb("#94a3b8")),
      edge((0, 2.2), (0, 2.4), "--", stroke: 0.5pt + rgb("#94a3b8")),
      edge((0, 3.1), (0, 4.8), "--", stroke: 0.5pt + rgb("#94a3b8")),

      edge(<channel>, (1, 3.0), "--", stroke: 0.5pt + rgb("#94a3b8")),
      edge((1, 3.8), (1, 4.8), "--", stroke: 0.5pt + rgb("#94a3b8")),

      edge(<bob>, (2, 3.7), "--", stroke: 0.5pt + rgb("#94a3b8")),
      edge((2, 4.4), (2, 4.6), "--", stroke: 0.5pt + rgb("#94a3b8")),
      edge((2, 5.3), (2, 5.5), "--", stroke: 0.5pt + rgb("#94a3b8")),

      node((0, 0.95), align(left)[*1. Sinh khóa* $K$\ ngẫu nhiên], name: <a1>, stroke: 0.5pt + rgb("#f59e0b"), fill: rgb("#fef3c7"), shape: rect),
      node((0, 1.85), align(left)[*2. Mã hóa AES*:\ $C_("data") = "AES"_K (M)$], name: <a2>, stroke: 0.5pt + rgb("#3b82f6"), fill: rgb("#eff6ff"), shape: rect),
      node((0, 2.75), align(left)[*3. Mã hóa RSA*:\ $C_("key") = "RSA"_(E_B)(K)$], name: <a3>, stroke: 0.5pt + rgb("#7c3aed"), fill: rgb("#f5f3ff"), shape: rect),

      edge((0, 3.4), (1, 3.4), "-|>", [Gửi gói tin], label-pos: 0.35, label-side: left),
      node((1, 3.4), align(center)[*Gói tin PGP:*\ {$C_("key"), "IV", C_("data"), "Tag"$\}], name: <pkg>, stroke: 0.8pt + rgb("#16a34a"), fill: rgb("#dcfce7"), shape: rect),
      edge((1, 3.4), (2, 3.4), "-|>", [Tiếp nhận], label-pos: 0.65, label-side: left),

      node((2, 4.05), align(left)[*4. Giải mã RSA*:\ $K = "RSA"_(D_B)(C_("key"))$], name: <b1>, stroke: 0.5pt + rgb("#7c3aed"), fill: rgb("#f5f3ff"), shape: rect),
      node((2, 4.95), align(left)[*5. Giải mã AES & Xác thực*:\ $M = "AES"_K (C_("data"))$], name: <b2>, stroke: 0.5pt + rgb("#16a34a"), fill: rgb("#dcfce7"), shape: rect),
    ),
    caption: [Sơ đồ tuần tự quy trình truyền thông mã hóa lai PGP giữa Alice và Bob],
  )
]
