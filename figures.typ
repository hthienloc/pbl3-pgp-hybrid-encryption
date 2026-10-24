#import "@preview/fletcher:0.5.6" as fletcher: diagram, node, edge
#import "styles.typ": (
  d-node,
  entity-badge,
  stroke-data,
  stroke-process,
  stroke-package,
  stroke-key,
  stroke-auth,
  stroke-network,
  stroke-axis,
)

// --- HÌNH 1: NGUYÊN LÝ MÃ HÓA VÀ GIẢI MÃ LAI RSA - AES ---
#let fig-hybrid-overview = figure(
  diagram(
    spacing: (16mm, 10mm),
    node-stroke: 0.8pt + black,
    node-fill: none,
    node-corner-radius: 3pt,
    edge-stroke: 0.8pt + black,

    // Huy hiệu thực thể
    node((-0.9, 0.6), entity-badge("Alice", "Người gửi", gender: "female"), name: <badge_alice>, stroke: 0.8pt + black, shape: rect, corner-radius: 4pt, inset: 5pt),
    node((-0.9, 4.0), entity-badge("Bob", "Người nhận", gender: "male"), name: <badge_bob>, stroke: 0.8pt + black, shape: rect, corner-radius: 4pt, inset: 5pt),

    // --- HÀNG 1: QUÁ TRÌNH MÃ HÓA (ALICE) ---
    d-node((0, 0), "Bản rõ gốc", sub: $M$, kind: "data", name: <m>),
    d-node((0, 1.2), "Session Key", sub: [$K$ ngẫu nhiên], kind: "key", name: <key>),

    d-node((1.3, 0), "Mã hóa AES", sub: [Dùng khóa $K$], kind: "process", name: <aes_enc>),
    d-node((1.3, 1.2), "Mã hóa RSA", sub: [Bảo vệ $K$], kind: "process", name: <rsa_enc>),
    d-node((1.3, 2.2), "Public Key Bob", sub: [($e_B, n$)], kind: "auth", name: <pub>),

    d-node((2.6, 0), "Bản mã dữ liệu", sub: $C_("data")$, kind: "process", name: <cdata>),
    d-node((2.6, 1.2), "Khóa phiên mã hóa", sub: $C_("key")$, kind: "process", name: <ckey>),

    // --- HÀNG 2: QUÁ TRÌNH GIẢI MÃ (BOB) ---
    d-node((2.6, 3.4), "Bản mã dữ liệu", sub: $C_("data")$, kind: "process", name: <b_cdata>),
    d-node((2.6, 4.6), "Khóa phiên mã hóa", sub: $C_("key")$, kind: "process", name: <b_ckey>),

    d-node((1.3, 3.4), "Giải mã AES", sub: [Dùng khóa $K$], kind: "process", name: <aes_dec>),
    d-node((1.3, 4.6), "Giải mã RSA", sub: [Lấy lại $K$], kind: "process", name: <rsa_dec>),
    d-node((1.3, 5.6), "Private Key Bob", sub: [($d_B, n$)], kind: "key", name: <priv>),

    d-node((0, 3.4), "Bản rõ khôi phục", sub: $M' = M$, kind: "data", name: <m_out>),
    d-node((0, 4.6), "Session Key", sub: [$K$ khôi phục], kind: "key", name: <key_out>),

    // Nối từ thực thể vào quy trình
    edge(<badge_alice>, <m>, stroke: (paint: black, thickness: 0.6pt, dash: "dashed")),
    edge(<badge_bob>, <m_out>, stroke: (paint: black, thickness: 0.6pt, dash: "dashed")),

    // Nối phía Alice: Từ trái sang phải
    edge(<m>, <aes_enc>, "-|>"),
    edge(<key>, (0.6, 1.2), (0.6, 0.3), <aes_enc>, "-|>"),
    edge(<key>, <rsa_enc>, "-|>"),
    edge(<pub>, <rsa_enc>, "-|>"),
    edge(<aes_enc>, <cdata>, "-|>"),
    edge(<rsa_enc>, <ckey>, "-|>"),

    // Đường truyền mạng kết nối từ Alice (tầng trên) sang Bob (tầng dưới)
    edge(<cdata>, (4.3, 0), (4.3, 3.4), <b_cdata>, "-|>", [#text(size: 8pt)[Kênh mạng]], label-pos: 0.5, label-side: right, stroke: stroke-network),
    edge(<ckey>, (3.4, 1.2), (3.4, 4.6), <b_ckey>, "-|>", stroke: stroke-network),

    // Nối phía Bob: Từ phải sang trái
    edge(<b_cdata>, <aes_dec>, "-|>"),
    edge(<b_ckey>, <rsa_dec>, "-|>"),
    edge(<priv>, <rsa_dec>, "-|>"),
    edge(<rsa_dec>, <key_out>, "-|>"),
    edge(<key_out>, (0.7, 4.6), (0.7, 3.7), <aes_dec>, "-|>"),
    edge(<aes_dec>, <m_out>, "-|>"),
  ),
  caption: [Sơ đồ nguyên lý mã hóa và giải mã lai RSA – AES khép kín trong mô hình PGP],
)

// --- HÌNH 2: SƠ ĐỒ TUẦN TỰ TƯƠNG TÁC ALICE - BOB ---
#let fig-sequence-interaction = figure(
  diagram(
    spacing: (28mm, 7.8mm),
    node-stroke: 0.8pt + black,
    node-fill: none,
    node-corner-radius: 3pt,
    edge-stroke: 0.8pt + black,

    // Thực thể đồng nhất với Hình 1
    node((0, 0), entity-badge("Alice", "Người gửi", gender: "female"), name: <alice>, stroke: 0.8pt + black, shape: rect, corner-radius: 4pt, inset: 5pt),
    node((1, 0), align(center)[#text(size: 8pt)[*Kênh mạng*]\ #text(size: 7pt, fill: luma(90))[Truyền thông]], name: <channel>, stroke: 0.8pt + black, shape: rect, corner-radius: 4pt, inset: 5pt),
    node((2, 0), entity-badge("Bob", "Người nhận", gender: "male"), name: <bob>, stroke: 0.8pt + black, shape: rect, corner-radius: 4pt, inset: 5pt),

    // Trục thời gian Alice
    edge(<alice>, (0, 1.45), "--", stroke: stroke-axis),
    edge((0, 2.15), (0, 2.35), "--", stroke: stroke-axis),
    edge((0, 3.05), (0, 3.25), "--", stroke: stroke-axis),
    edge((0, 3.95), (0, 5.8), "--", stroke: stroke-axis),

    // Trục thời gian Kênh mạng
    edge(<channel>, (1, 0.7), "--", stroke: stroke-axis),
    edge((1, 1.3), (1, 4.3), "--", stroke: stroke-axis),
    edge((1, 4.3), (1, 5.8), "--", stroke: stroke-axis),

    // Trục thời gian Bob
    edge(<bob>, (2, 0.65), "--", stroke: stroke-axis),
    edge((2, 1.35), (2, 4.7), "--", stroke: stroke-axis),
    edge((2, 5.3), (2, 5.5), "--", stroke: stroke-axis),
    edge((2, 6.1), (2, 6.3), "--", stroke: stroke-axis),

    // BƯỚC 0: BOB SINH KHÓA VÀ GỬI PUBLIC KEY CHO ALICE
    node((2, 1.0), align(left)[#text(size: 8pt)[*0. Sinh khóa RSA*:\ $(e_B, n)$ & $(d_B, n)$]], name: <b0>, stroke: stroke-key, shape: rect),
    edge((2, 1.0), (0, 1.0), "-|>", [#text(size: 7.5pt)[Công khai Public Key $(e_B, n)$]], label-pos: 0.35, label-side: right, stroke: stroke-network),

    // BƯỚC 1, 2, 3: ALICE TIẾN HÀNH MÃ HÓA
    node((0, 1.8), align(left)[#text(size: 8pt)[*1. Sinh khóa* $K$\ ngẫu nhiên]], name: <a1>, stroke: stroke-key, shape: rect),
    node((0, 2.7), align(left)[#text(size: 8pt)[*2. Mã hóa AES*:\ $C_("data") = "AES"_K (M)$]], name: <a2>, stroke: 0.8pt + black, shape: rect),
    node((0, 3.6), align(left)[#text(size: 8pt)[*3. Mã hóa RSA*:\ $C_("key") = "RSA"_(e_B)(K)$]], name: <a3>, stroke: 0.8pt + black, shape: rect),

    // GỬI GÓI TIN PGP SANG BOB
    edge((0, 4.3), (1, 4.3), "-|>", [#text(size: 8pt)[Gửi gói tin]], label-pos: 0.35, label-side: left),
    node((1, 4.3), align(center)[#text(size: 8pt)[*Gói tin PGP:*\ {$C_("key"), "IV", C_("data"), "Tag"$}]], name: <pkg>, stroke: stroke-package, shape: rect),
    edge((1, 4.3), (2, 4.3), "-|>", [#text(size: 8pt)[Tiếp nhận]], label-pos: 0.65, label-side: left),

    // BƯỚC 4, 5: BOB GIẢI MÃ
    node((2, 5.0), align(left)[#text(size: 8pt)[*4. Giải mã RSA*:\ $K = "RSA"_(d_B)(C_("key"))$]], name: <b1>, stroke: 0.8pt + black, shape: rect),
    node((2, 5.8), align(left)[#text(size: 8pt)[*5. Giải mã AES & Xác thực*:\ $M = "AES"_K (C_("data"))$]], name: <b2>, stroke: stroke-auth, shape: rect),
  ),
  caption: [Sơ đồ tuần tự quy trình truyền thông mã hóa lai PGP giữa Alice và Bob],
)

// --- HÌNH 3: VÍ DỤ SỐ HỌC RSA (CÓ ĐỒNG BỘ ALICE & BOB) ---
#let fig-rsa-numeric-example = figure(
  diagram(
    spacing: (16mm, 11mm),
    node-stroke: 0.8pt + black,
    node-fill: none,
    node-corner-radius: 3pt,
    edge-stroke: 0.8pt + black,

    // Huy hiệu Alice & Bob
    node((-0.9, 0), entity-badge("Alice", "Bên gửi", gender: "female"), name: <badge_alice>, stroke: 0.8pt + black, shape: rect, corner-radius: 4pt, inset: 5pt),
    node((-0.9, 1.4), entity-badge("Bob", "Bên nhận", gender: "male"), name: <badge_bob>, stroke: 0.8pt + black, shape: rect, corner-radius: 4pt, inset: 5pt),

    // Hàng 1: Mã hóa (Alice)
    d-node((0, 0), "Bản rõ", sub: $M = 125$, kind: "data", name: <m>),
    d-node((1.3, 0), "Mã hóa RSA", sub: $C = M^e mod n$, kind: "process", name: <enc>),
    d-node((1.3, -1.0), "Khóa công khai", sub: [$(e=17, n=3233)$], kind: "auth", name: <pub>),
    d-node((2.6, 0), "Bản mã", sub: $C = 1516$, kind: "package", name: <c>),

    // Hàng 2: Giải mã (Bob)
    d-node((2.6, 1.4), "Giải mã RSA", sub: $M' = C^d mod n$, kind: "process", name: <dec>),
    d-node((1.3, 1.4), "Khôi phục", sub: $M' = 125$, kind: "data", name: <m2>),
    d-node((2.6, 2.4), "Khóa bí mật", sub: [$(d=2753, n=3233)$], kind: "key", name: <priv>),

    // Nối chỉ định thực thể
    edge(<badge_alice>, <m>, stroke: (paint: black, thickness: 0.6pt, dash: "dashed")),
    edge(<m2>, <badge_bob>, stroke: (paint: black, thickness: 0.6pt, dash: "dashed")),

    // Nối luồng mã hóa & giải mã
    edge(<m>, <enc>, "-|>"),
    edge(<pub>, <enc>, "-|>"),
    edge(<enc>, <c>, "-|>"),
    edge(<c>, <dec>, "-|>", [#text(size: 7.5pt)[Gửi qua mạng]], label-pos: 0.5, label-side: right, stroke: stroke-network),
    edge(<priv>, <dec>, "-|>"),
    edge(<dec>, <m2>, "-|>"),
  ),
  caption: [Sơ đồ chu trình xử lý dữ liệu và khóa trong ví dụ số học RSA giữa Alice và Bob],
)

// --- HÌNH 4: CẤU TRÚC GÓI DỮ LIỆU ĐÓNG GÓI VÀ PHÂN TÍCH CÚ PHÁP TẠI BỘ GIẢI MÃ BOB ---
#let fig-packet-layout = figure(
  diagram(
    spacing: (13mm, 13mm),
    node-stroke: 0.8pt + black,
    node-fill: none,
    node-corner-radius: 3pt,
    edge-stroke: 0.8pt + black,

    // Huy hiệu Bob (Người nhận / Bộ phân tích gói tin)
    node((-0.9, 0), entity-badge("Bob", "Phía nhận", gender: "male"), name: <badge_bob>, stroke: 0.8pt + black, shape: rect, corner-radius: 4pt, inset: 5pt),

    // Dãy khung gói tin liên tục (Header & Payload)
    node((0, 0), align(center)[
      #text(size: 7.5pt, fill: luma(80))[0 .. 255 (256B)]\
      *RSA Key*\
      #text(size: 8pt)[Khóa phiên]
    ], name: <f_key>, shape: rect, stroke: stroke-process),

    node((1, 0), align(center)[
      #text(size: 7.5pt, fill: luma(80))[256 .. 267 (12B)]\
      *Nonce / IV*\
      #text(size: 8pt)[Ngẫu nhiên GCM]
    ], name: <f_nonce>, shape: rect, stroke: stroke-key),

    node((2, 0), align(center)[
      #text(size: 7.5pt, fill: luma(80))[268 .. 268+L-1 ($L$ B)]\
      *AES Ciphertext*\
      #text(size: 8pt)[Dữ liệu mã hóa]
    ], name: <f_data>, shape: rect, stroke: stroke-process),

    node((3, 0), align(center)[
      #text(size: 7.5pt, fill: luma(80))[Cuối cùng (16B)]\
      *Auth Tag*\
      #text(size: 8pt)[Mã MAC toàn vẹn]
    ], name: <f_tag>, shape: rect, stroke: stroke-auth),

    // Chức năng phân tích cú pháp ở bộ giải mã (Parser Target phía Bob)
    node((0, 1.1), align(center)[
      #text(size: 8pt)[*1. Giải mã RSA*]\
      `rsa_decrypt()`\
      $arrow.b$ Lấy khóa $K$
    ], name: <p_key>, shape: rect, stroke: stroke-data),

    node((1, 1.1), align(center)[
      #text(size: 8pt)[*2. Nạp IV*]\
      `AES.new(K, ...)`\
      $arrow.b$ Nạp `nonce`
    ], name: <p_nonce>, shape: rect, stroke: stroke-key),

    node((2, 1.1), align(center)[
      #text(size: 8pt)[*3. Giải mã AES*]\
      `decrypt()`\
      $arrow.b$ Khôi phục $M$
    ], name: <p_data>, shape: rect, stroke: stroke-data),

    node((3, 1.1), align(center)[
      #text(size: 8pt)[*4. Kiểm thực MAC*]\
      `verify(tag)`\
      $arrow.b$ Chống giả mạo
    ], name: <p_tag>, shape: rect, stroke: stroke-auth),

    // Nối từ badge Bob vào gói tin nhận được
    edge(<badge_bob>, <f_key>, stroke: (paint: black, thickness: 0.6pt, dash: "dashed")),

    // Mũi tên chỉ mục ánh xạ từ trường sang hàm xử lý
    edge(<f_key>, <p_key>, "-|>"),
    edge(<f_nonce>, <p_nonce>, "-|>"),
    edge(<f_data>, <p_data>, "-|>"),
    edge(<f_tag>, <p_tag>, "-|>"),
  ),
  caption: [Sơ đồ cấu trúc khung gói tin (Packet Framing) và luồng phân tích cú pháp tại bộ nhận của Bob],
)
