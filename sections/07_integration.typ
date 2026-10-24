#import "@preview/fletcher:0.5.6" as fletcher: diagram, node, edge

= Tích hợp RSA và AES trong Hybrid Encryption

Trong mô hình mã hóa lai hoàn chỉnh, RSA tuyệt đối không tham gia trực tiếp vào việc mã hóa khối dữ liệu thông điệp dài mà đóng vai trò là "két sắt" bảo vệ Session Key. AES đảm nhận toàn bộ việc mã hóa dữ liệu tốc độ cao.

== Cấu trúc khung gói tin (Packet Framing & Offset)

Khi truyền tải qua mạng, dòng dữ liệu PGP được cấu trúc thành các trường liên tục với vị trí byte (Offset) và kích thước xác định, cho phép bộ giải mã ở phía nhận phân tích cú pháp (parse) chính xác:

#v(0.3em)
#align(center)[
  #figure(
    diagram(
      spacing: (11mm, 12mm),
      node-stroke: 0.8pt + black,
      node-fill: none,
      node-corner-radius: 3pt,
      edge-stroke: 0.8pt + black,

      // Dãy khung gói tin liên tục (Header & Payload)
      node((0, 0), align(center)[
        #text(size: 8pt, fill: luma(80))[0 .. 255 (256B)]\
        *RSA Key*\
        #text(size: 8pt)[Khóa phiên]
      ], name: <f_key>, shape: rect, stroke: 1.4pt + black),

      node((1, 0), align(center)[
        #text(size: 8pt, fill: luma(80))[256 .. 267 (12B)]\
        *Nonce / IV*\
        #text(size: 8pt)[Ngẫu nhiên GCM]
      ], name: <f_nonce>, stroke: (paint: black, thickness: 0.8pt, dash: "dashed")),

      node((2, 0), align(center)[
        #text(size: 8pt, fill: luma(80))[268 .. 268+L-1 ($L$ B)]\
        *AES Ciphertext*\
        #text(size: 8pt)[Dữ liệu mã hóa]
      ], name: <f_data>, stroke: 1.4pt + black),

      node((3, 0), align(center)[
        #text(size: 8pt, fill: luma(80))[Cuối cùng (16B)]\
        *Auth Tag*\
        #text(size: 8pt)[Mã MAC toàn vẹn]
      ], name: <f_tag>, stroke: (paint: black, thickness: 0.8pt, dash: "dash-dotted")),

      // Chức năng phân tích cú pháp ở bộ giải mã (Parser Target)
      node((0, 1), align(center)[
        #text(size: 8pt)[*1. Giải mã RSA*]\
        `rsa_decrypt()`\
        $arrow.b$ Lấy khóa $K$
      ], name: <p_key>, stroke: 0.8pt + black),

      node((1, 1), align(center)[
        #text(size: 8pt)[*2. Nạp IV*]\
        `AES.new(K, ...)`\
        $arrow.b$ Nạp `nonce`
      ], name: <p_nonce>, stroke: (paint: black, thickness: 0.8pt, dash: "dashed")),

      node((2, 1), align(center)[
        #text(size: 8pt)[*3. Giải mã AES*]\
        `decrypt()`\
        $arrow.b$ Khôi phục $M$
      ], name: <p_data>, stroke: 0.8pt + black),

      node((3, 1), align(center)[
        #text(size: 8pt)[*4. Kiểm thực MAC*]\
        `verify(tag)`\
        $arrow.b$ Chống giả mạo
      ], name: <p_tag>, stroke: (paint: black, thickness: 0.8pt, dash: "dash-dotted")),

      // Mũi tên chỉ mục ánh xạ từ trường sang hàm xử lý
      edge(<f_key>, <p_key>, "-|>"),
      edge(<f_nonce>, <p_nonce>, "-|>"),
      edge(<f_data>, <p_data>, "-|>"),
      edge(<f_tag>, <p_tag>, "-|>"),
    ),
    caption: [Sơ đồ cấu trúc khung gói tin (Packet Format) và ánh xạ phân tích cú pháp tại bộ giải mã],
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

== Lưu đồ điều khiển của chương trình tích hợp

Để thể hiện chính xác tiến trình xử lý dữ liệu của mã nguồn Python trong `src/hybrid_demo.py`, lưu đồ thuật toán phân định rõ quy trình mã hóa (Alice) và xác thực giải mã (Bob):

#v(0.3em)
#align(center)[
  #figure(
    diagram(
      spacing: (16mm, 9mm),
      node-stroke: 0.8pt + black,
      node-fill: none,
      node-corner-radius: 4pt,
      edge-stroke: 0.8pt + black,

      // Cột 0: Tiến trình Alice (từ trên xuống)
      node((0, 0), align(center)[#text(size: 8pt)[*1. Dữ liệu gốc*]\ $M$ (Plaintext)], name: <m>, stroke: 0.8pt + black),
      node((0, 1), align(center)[#text(size: 8pt)[*2. Sinh khóa* $K$]\ Ngẫu nhiên 128-bit], name: <genk>, stroke: (paint: black, thickness: 0.8pt, dash: "dashed")),
      node((0, 2), align(center)[#text(size: 8pt)[*3. Mã hóa AES-GCM*]\ $C_("data")$, IV, Tag], name: <aesenc>, stroke: 1.3pt + black),
      node((0, 3), align(center)[#text(size: 8pt)[*4. Mã hóa RSA*]\ $C_("key") = K^e mod n$], name: <rsaenc>, stroke: 1.3pt + black),
      node((0, 4), align(center)[#text(size: 8pt)[*5. Đóng gói payload*]\ {$C_("key"), "IV", C_("data"), "Tag"$\}], name: <pack>, stroke: 1.5pt + black),

      // Cột 1: Kênh truyền mạng
      node((1, 4), align(center)[#text(size: 8pt)[*Kênh truyền tin*]\ (Network)], name: <net>, stroke: 0.8pt + black),

      // Cột 2: Tiến trình Bob (từ dưới lên)
      node((2, 4), align(center)[#text(size: 8pt)[*6. Nhận & Tách gói*]\ 4 trường dữ liệu], name: <unpack>, stroke: 1.5pt + black),
      node((2, 3), align(center)[#text(size: 8pt)[*7. Giải mã RSA*]\ $K = (C_("key"))^d mod n$], name: <rsadec>, stroke: 1.3pt + black),
      node((2, 2), align(center)[#text(size: 8pt)[*8. Giải mã AES-GCM*]\ Dùng $K$ và IV], name: <aesdec>, stroke: (paint: black, thickness: 0.8pt, dash: "dash-dotted")),
      node((2, 1), align(center)[#text(size: 8pt)[*9. Kiểm tra Tag*]\ Đối chiếu MAC], name: <cond>, shape: rect, stroke: 1.3pt + black),

      // Kết quả cuối cùng
      node((1.5, 0), align(center)[#text(size: 8pt)[*Hủy bản tin*]\ `MAC failed`], name: <fail>, stroke: 0.8pt + black),
      node((2.5, 0), align(center)[#text(size: 8pt)[*Khôi phục bản rõ*]\ `Plaintext OK`], name: <ok>, stroke: 1.5pt + black),

      // Luồng tuần tự Alice: 1 -> 2 -> 3 -> 4 -> 5
      edge(<m>, <genk>, "-|>"),
      edge(<genk>, <aesenc>, "-|>"),
      edge(<aesenc>, <rsaenc>, "-|>"),
      edge(<rsaenc>, <pack>, "-|>"),

      // Đường truyền mạng: 5 -> Net -> 6
      edge(<pack>, <net>, "-|>"),
      edge(<net>, <unpack>, "-|>"),

      // Luồng tuần tự Bob: 6 -> 7 -> 8 -> 9
      edge(<unpack>, <rsadec>, "-|>"),
      edge(<rsadec>, <aesdec>, "-|>"),
      edge(<aesdec>, <cond>, "-|>"),

      // Rẽ nhánh kiểm tra Tag
      edge(<cond>, <fail>, "-|>", [#text(size: 8pt)[Sai]], label-pos: 0.5, label-side: left),
      edge(<cond>, <ok>, "-|>", [#text(size: 8pt)[Khớp]], label-pos: 0.5, label-side: right),
    ),
    caption: [Lưu đồ luồng dữ liệu và kiểm thực toàn vẹn trong mã nguồn hybrid_pgp.py],
  )
]
#v(0.3em)

== Mã nguồn tích hợp Hybrid PGP (`algorithms/hybrid_pgp.py`)

#raw(read("../algorithms/hybrid_pgp.py"), lang: "python")

#import "../components.typ": info-box
#info-box(title: "Lưu ý kỹ thuật và tính minh bạch")[
  - *Chế độ AES-GCM:* Sử dụng *Nonce* (Number used once) nhằm triệt tiêu hiện tượng trùng lặp khối mã và sử dụng *Authentication Tag* (128-bit) để bảo đảm toàn vẹn dữ liệu.
  - *Ranh giới triển khai:* Nhóm tự lập trình thuật toán số học RSA để nắm vững nguyên lý toán học, đồng thời tích hợp thư viện AES chuẩn công nghiệp (`Cryptodome`) để bảo đảm hiệu năng và tính an toàn mật mã.
]
