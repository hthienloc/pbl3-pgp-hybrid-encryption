#import "@preview/fletcher:0.5.6" as fletcher: diagram, node, edge
#import "@preview/chronos:0.3.0"
#import "theme.typ": (
  color-text-muted,
  color-text-subtle,
  color-surface-tint,
  color-surface-subtle,
  color-surface-cond,
)
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

#let f-diagram(..args) = {
  set par(justify: false)
  diagram(..args)
}

// --- HÌNH 1: NGUYÊN LÝ MÃ HÓA VÀ GIẢI MÃ LAI RSA - AES (FLETCHER GRID) ---
#let fig-hybrid-overview = figure(
  f-diagram(
    spacing: (10mm, 7mm),
    node-stroke: 0.7pt + color-text-muted,
    node-corner-radius: 3pt,
    edge-stroke: 0.75pt + black,
    {
      // Styles
      let box-proc = (fill: color-surface-tint, width: 32mm, inset: 5pt)
      let box-data = (fill: white, width: 32mm, inset: 5pt)
      let box-key = (fill: white, stroke: (paint: color-text-subtle, thickness: 0.7pt, dash: "dashed"), shape: fletcher.shapes.pill, width: 32mm, inset: 5pt)

      // Alice cluster
      node((0, 0), align(center)[*Bản rõ gốc*\ $M$], ..box-data, name: <m>)
      node((1, 0), align(center)[*Session Key*\ $K$ ngẫu nhiên], ..box-key, name: <k>)
      node((2, 0), align(center)[*Public Key Bob*\ $(e_B, n)$], ..box-key, name: <pub>)

      node((0, 1), align(center)[*Mã hóa AES*\ Dùng khóa $K$], ..box-proc, name: <aes_e>)
      node((2, 1), align(center)[*Mã hóa RSA*\ Bảo vệ $K$], ..box-proc, name: <rsa_e>)

      node((0, 2), align(center)[*Bản mã dữ liệu*\ $C_("data")$], ..box-data, name: <cd>)
      node((2, 2), align(center)[*Khóa phiên mã hóa*\ $C_("key")$], ..box-data, name: <ck>)

      node(
        enclose: (<m>, <pub>, <cd>, <ck>),
        stroke: (paint: color-text-subtle, thickness: 0.7pt, dash: "dashed"),
        fill: none,
        inset: 10pt,
        corner-radius: 5pt,
        name: <alice_box>,
      )
      node((0, -0.52), text(size: 9pt, weight: "bold", fill: color-text-muted)[Phía Alice (Mã hóa)], stroke: none, fill: white, inset: 2pt)

      edge(<m>, <aes_e>, "-|>")
      edge(<k>, (1, 0.5), (0.35, 0.5), <aes_e>, "--|>")
      edge(<k>, (1, 0.5), (1.65, 0.5), <rsa_e>, "--|>")
      edge(<pub>, <rsa_e>, "--|>")
      edge(<aes_e>, <cd>, "-|>")
      edge(<rsa_e>, <ck>, "-|>")

      // Network transmission
      edge(<cd>, <bcd>, "..|>")
      edge(<ck>, <bck>, "..|>")
      node((1, 2.6), text(size: 8pt, fill: color-text-muted)[Kênh mạng (+ Nonce, Tag)], stroke: none, fill: white, inset: 2pt)

      // Bob cluster
      node((0, 3.75), align(center)[*Bản mã dữ liệu*\ $C_("data")$], ..box-data, name: <bcd>)
      node((2, 3.75), align(center)[*Khóa phiên mã hóa*\ $C_("key")$], ..box-data, name: <bck>)
      node((2, 4.75), align(center)[*Giải mã RSA*\ Lấy lại $K$], ..box-proc, name: <rsa_d>)
      node((3.15, 4.75), align(center)[*Private Key Bob*\ $(d_B, n)$], ..box-key, width: 29mm, name: <priv>)

      node((1, 5.55), align(center)[*Session Key*\ $K$ khôi phục], ..box-key, name: <k_out>)
      node((0, 6.35), align(center)[*Giải mã AES*\ Dùng khóa $K$], ..box-proc, name: <aes_d>)
      node((0, 7.35), align(center)[*Bản rõ khôi phục*\ $M' = M$], ..box-data, name: <m_out>)

      node(
        enclose: (<bcd>, <priv>, <m_out>),
        stroke: (paint: color-text-subtle, thickness: 0.7pt, dash: "dashed"),
        fill: none,
        inset: 10pt,
        corner-radius: 5pt,
        name: <bob_box>,
      )
      node((1, 3.22), text(size: 9pt, weight: "bold", fill: color-text-muted)[Phía Bob (Giải mã)], stroke: none, fill: white, inset: 2pt)

      edge(<bcd>, <aes_d>, "-|>")
      edge(<bck>, <rsa_d>, "-|>")
      edge(<priv>, <rsa_d>, "--|>")
      edge(<rsa_d>, (2, 5.55), <k_out>, "--|>")
      edge(<k_out>, (1, 6.35), <aes_d>, "--|>")
      edge(<aes_d>, <m_out>, "-|>")
    },
  ),
  caption: [Sơ đồ nguyên lý mã hóa và giải mã lai RSA – AES khép kín trong mô hình PGP @zhou2011],
)

// --- HÌNH 2: SƠ ĐỒ TUẦN TỰ TƯƠNG TÁC ALICE - BOB (DÙNG CHRONOS HỖ TRỢ MATH) ---
#let fig-sequence-interaction = figure(
  chronos.diagram(width: 100%, {
    import chronos: *
    _par("A", display-name: [*Alice*\ #text(size: 8pt, fill: color-text-subtle)[Người gửi]], color: white, show-bottom: true)
    _par("C", display-name: [*Kênh mạng*\ #text(size: 8pt, fill: color-text-subtle)[Truyền thông]], color: white, show-bottom: true)
    _par("B", display-name: [*Bob*\ #text(size: 8pt, fill: color-text-subtle)[Người nhận]], color: white, show-bottom: true)

    _note("over", pos: "B", shape: "rect", color: color-surface-subtle)[
      #align(left)[
        *0. Sinh cặp khóa RSA:*\
        Public Key $(e_B, n)$, Private Key $(d_B, n)$
      ]
    ]
    _seq("B", "A", comment: [Công khai Public Key $(e_B, n)$], dashed: true)

    _note("over", pos: "A", shape: "rect", color: color-surface-subtle)[
      #align(left)[
        *1. Sinh khóa phiên* $K$ và vector $"IV"$\
        *2. Mã hóa AES-GCM:* $(C_("data"), "Tag") = "AES"_K (M, "IV")$\
        *3. Mã hóa RSA:* $C_("key") = "RSA"_(e_B)(K)$
      ]
    ]

    _seq("A", "C", comment: [Gửi gói tin PGP: $\{C_("key"), "IV", C_("data"), "Tag"\}$])
    _seq("C", "B", comment: [Tiếp nhận gói tin PGP])

    _note("over", pos: "B", shape: "rect", color: color-surface-subtle)[
      #align(left)[
        *4. Giải mã RSA:* $K = "RSA"_(d_B)(C_("key"))$\
        *5. Xác thực toàn vẹn:* Đối chiếu $"Tag"$ (GHASH)\
        *6. Giải mã AES-GCM:* $M = "AES"_K (C_("data"), "IV")$
      ]
    ]
  }),
  caption: [Sơ đồ tuần tự quy trình truyền thông mã hóa lai PGP giữa Alice và Bob],
)

// --- HÌNH 3: VÍ DỤ SỐ HỌC RSA (FLETCHER GRID) ---
#let fig-rsa-numeric-example = figure(
  f-diagram(
    spacing: (14mm, 7mm),
    node-stroke: 0.7pt + color-text-muted,
    node-corner-radius: 3pt,
    edge-stroke: 0.75pt + black,
    {
      let box-proc = (fill: color-surface-tint, width: 42mm, inset: 5pt)
      let box-data = (fill: white, width: 34mm, inset: 5pt)
      let box-key = (fill: white, stroke: (paint: color-text-subtle, thickness: 0.7pt, dash: "dashed"), shape: fletcher.shapes.pill, width: 40mm, inset: 5pt)

      // Alice
      node((-0.7, 0), align(center)[*Bản rõ*\ $M = 125$], ..box-data, name: <m>)
      node((0.7, 0), align(center)[*Khóa công khai*\ $(e = 17, n = 3233)$], ..box-key, name: <pub>)
      node((0, 1.0), align(center)[*Mã hóa RSA*\ $C = M^e mod n$], ..box-proc, name: <enc>)
      node((0, 2.0), align(center)[*Bản mã*\ $C = 1516$], ..box-data, name: <c>)

      node(
        enclose: (<m>, <pub>, <c>),
        stroke: (paint: color-text-subtle, thickness: 0.7pt, dash: "dashed"),
        fill: none,
        inset: 10pt,
        corner-radius: 5pt,
      )
      node((0, -0.55), text(size: 9pt, weight: "bold", fill: color-text-muted)[Alice (Bên gửi)], stroke: none, fill: white, inset: 2pt)

      edge(<m>, (-0.7, 0.5), (-0.35, 0.5), <enc>, "-|>")
      edge(<pub>, (0.7, 0.5), (0.35, 0.5), <enc>, "--|>")
      edge(<enc>, <c>, "-|>")

      // Network
      edge(<c>, <c_bob>, "..|>", label: [Gửi qua mạng], label-side: right)

      // Bob
      node((-0.7, 3.1), align(center)[*Bản mã nhận*\ $C = 1516$], ..box-data, name: <c_bob>)
      node((0.7, 3.1), align(center)[*Khóa bí mật*\ $(d = 2753, n = 3233)$], ..box-key, name: <priv>)
      node((0, 4.1), align(center)[*Giải mã RSA*\ $M' = C^d mod n$], ..box-proc, name: <dec>)
      node((0, 5.1), align(center)[*Khôi phục*\ $M' = 125$], ..box-data, name: <m2>)

      node(
        enclose: (<c_bob>, <priv>, <m2>),
        stroke: (paint: color-text-subtle, thickness: 0.7pt, dash: "dashed"),
        fill: none,
        inset: 10pt,
        corner-radius: 5pt,
      )
      node((0, 2.6), text(size: 9pt, weight: "bold", fill: color-text-muted)[Bob (Bên nhận)], stroke: none, fill: white, inset: 2pt)

      edge(<c_bob>, (-0.7, 3.6), (-0.35, 3.6), <dec>, "-|>")
      edge(<priv>, (0.7, 3.6), (0.35, 3.6), <dec>, "--|>")
      edge(<dec>, <m2>, "-|>")
    },
  ),
  caption: [Sơ đồ chu trình xử lý dữ liệu và khóa trong ví dụ số học RSA giữa Alice và Bob],
)

// --- HÌNH 4: CẤU TRÚC KHUNG GÓI TIN VÀ PHÂN TÍCH CÚ PHÁP TẠI BỘ GIẢI MÃ BOB (FLETCHER GRID) ---
#let fig-packet-layout = figure(
  f-diagram(
    spacing: (2.5mm, 12mm),
    node-stroke: 0.7pt + color-text-muted,
    node-corner-radius: 3pt,
    edge-stroke: 0.75pt + black,
    {
      let box-field = (fill: white, width: 24.5mm, inset: 4pt)
      let box-step = (fill: color-surface-subtle, width: 24.5mm, inset: 4pt)

      // Top row: packet fields
      node((0, 0), align(center)[#text(size: 8pt)[*4 Bytes (Big-Endian)*\ *Độ dài gói*\ #text(size: 7pt, fill: color-text-subtle)[Tiền tố độ dài]]], ..box-field, name: <f_len>)
      node((1, 0), align(center)[#text(size: 8pt)[*Khóa phiên mã hóa*\ $C_("key")$\ #text(size: 7pt, fill: color-text-subtle)[Mã hóa RSA]]], ..box-field, name: <f_key>)
      node((2, 0), align(center)[#text(size: 8pt)[*Vector khởi tạo*\ *Nonce / IV (12B)*\ #text(size: 7pt, fill: color-text-subtle)[Dùng một lần]]], ..box-field, name: <f_nonce>)
      node((3, 0), align(center)[#text(size: 8pt)[*Bản mã dữ liệu*\ $C_("data")$\ #text(size: 7pt, fill: color-text-subtle)[Mã hóa AES-CTR]]], ..box-field, name: <f_data>)
      node((4, 0), align(center)[#text(size: 8pt)[*Thẻ xác thực*\ *Auth Tag (16B)*\ #text(size: 7pt, fill: color-text-subtle)[Hàm băm GHASH]]], ..box-field, name: <f_tag>)

      node(
        enclose: (<f_len>, <f_tag>),
        stroke: (paint: color-text-subtle, thickness: 0.7pt, dash: "dashed"),
        fill: none,
        inset: 12pt,
        corner-radius: 5pt,
      )
      node((2, -0.45), box(width: 0pt, align(center, text(size: 8pt, weight: "bold", fill: color-text-muted)[#box(width: 110mm)[Khung gói tin TCP: \[4B Big-Endian Length\] + \[JSON Envelope UTF-8\]]])), stroke: none, fill: none, inset: 0pt)

      // Bottom row: Bob parsing steps
      node((0, 1), align(center)[#text(size: 8pt)[*1. Đọc khung*\ Đọc đủ độ dài\ #text(size: 7pt, fill: color-text-subtle)[Tách gói JSON]]], ..box-step, name: <p_len>)
      node((1, 1), align(center)[#text(size: 8pt)[*2. Giải mã RSA*\ Khôi phục khóa $K'$\ #text(size: 7pt, fill: color-text-subtle)[Dùng khóa bí mật]]], ..box-step, name: <p_key>)
      node((2, 1), align(center)[#text(size: 8pt)[*3. Khởi tạo bộ đếm*\ Nạp Nonce / IV\ #text(size: 7pt, fill: color-text-subtle)[Tạo $J_0$ và $"CB"_i$]]], ..box-step, name: <p_nonce>)
      node((3, 1), align(center)[#text(size: 8pt)[*4. Giải mã AES*\ Giải mã dòng CTR\ #text(size: 7pt, fill: color-text-subtle)[Khôi phục $M'$]]], ..box-step, name: <p_data>)
      node((4, 1), align(center)[#text(size: 8pt)[*5. Kiểm tra Tag*\ Đối chiếu GHASH\ #text(size: 7pt, fill: color-text-subtle)[Chống sửa đổi]]], ..box-step, name: <p_tag>)

      node(
        enclose: (<p_len>, <p_tag>),
        stroke: (paint: color-text-subtle, thickness: 0.7pt, dash: "dashed"),
        fill: none,
        inset: 12pt,
        corner-radius: 5pt,
      )
      node((2, 1.45), box(width: 0pt, align(center, text(size: 8pt, weight: "bold", fill: color-text-muted)[#box(width: 110mm)[Phân tích cú pháp và xử lý tuần tự tại bộ nhận của Bob]])), stroke: none, fill: none, inset: 0pt)

      // Clean straight vertical arrows
      edge(<f_len>, <p_len>, "-|>")
      edge(<f_key>, <p_key>, "-|>")
      edge(<f_nonce>, <p_nonce>, "-|>")
      edge(<f_data>, <p_data>, "-|>")
      edge(<f_tag>, <p_tag>, "-|>")
    },
  ),
  caption: [Sơ đồ cấu trúc khung gói tin (Packet Framing) và luồng phân tích cú pháp tại bộ nhận của Bob],
)


// --- HÌNH 5: SƠ ĐỒ TUẦN TỰ TRUYỀN THÔNG QUA SOCKET TCP (DÙNG CHRONOS) ---
#let fig-socket-sequence = figure(
  chronos.diagram(width: 100%, {
    import chronos: *
    _par("A", display-name: [*Alice (TCP Client)*\ #text(size: 8pt, fill: color-text-subtle)[Máy gửi]], color: white, show-bottom: true)
    _par("C", display-name: [*Kênh TCP :5000*\ #text(size: 8pt, fill: color-text-subtle)[Length-prefixed JSON]], color: white, show-bottom: true)
    _par("B", display-name: [*Bob (TCP Server)*\ #text(size: 8pt, fill: color-text-subtle)[Máy nhận]], color: white, show-bottom: true)

    _note("over", pos: "B", shape: "rect", color: color-surface-subtle)[
      #align(left)[
        *0. Khởi tạo Server:*\
        Sinh khóa RSA $(e_B, n), (d_B, n)$\
        Lắng nghe tại cổng 5000
      ]
    ]

    _seq("A", "B", comment: [1. Yêu cầu lấy khóa công khai])
    _seq("B", "A", comment: [2. Trả Public Key $(e_B, n)$], dashed: true)

    _note("across", shape: "rect", color: color-surface-subtle)[
      *3. Xác thực ngoại vi (Out-of-Band):* Đối chiếu SHA-256 Public Key Fingerprint
    ]

    _note("over", pos: "A", shape: "rect", color: color-surface-subtle)[
      #align(left)[
        *4. Đóng gói Hybrid PGP:*\
        - Sinh khóa phiên $K$ (16B) & $"nonce"$ (12B)\
        - $(C_("data"), "Tag") = "AES-GCM"_K (M, "nonce")$\
        - $C_("key") = "RSA"_(e_B)(K)$
      ]
    ]

    _seq("A", "C", comment: [5. Gửi `[4B Length] + JSON Envelope`])
    _seq("C", "B", comment: [$C_("key")$ (hex), $"nonce", C_("data"), "Tag"$ (Base64)])

    _note("over", pos: "B", shape: "rect", color: color-surface-subtle)[
      #align(left)[
        *6. Giải mã & Xác thực:*\
        - $K = "RSA"_(d_B)(C_("key"))$\
        - Kiểm thực $"Tag"$ (GHASH) & giải mã $M$
      ]
    ]

    _seq("B", "A", comment: [7. Phản hồi kết quả xác thực (Hợp lệ / Lỗi)], dashed: true)
  }),
  caption: [Sơ đồ tuần tự mô phỏng mã hóa lai qua Socket TCP giữa máy Alice và máy Bob],
)

// --- LƯU ĐỒ THUẬT TOÁN AES-128 (SPN - FLETCHER ORTHOGONAL) ---
#let fig-aes-spn-flow = figure(
  f-diagram(
    spacing: (10mm, 5mm),
    node-stroke: 0.7pt + color-text-muted,
    node-corner-radius: 3pt,
    edge-stroke: 0.75pt + black,
    {
      let box-main = (fill: white, width: 84mm, inset: 4.5pt)
      let box-proc = (fill: color-surface-tint, width: 84mm, inset: 4.5pt)
      let box-cond = (fill: color-surface-cond, shape: fletcher.shapes.diamond, width: 60mm, inset: 4pt)

      node((0, 0), [*Khối bản rõ 128-bit* (Ma trận trạng thái $4 times 4$ byte)], ..box-main, name: <in_blk>)
      node((0, 1), [*Khởi tạo vòng 0:* Cộng khóa vòng (`AddRoundKey`)], ..box-proc, name: <init_key>)
      node((0, 2), [*Thế phi tuyến (`SubBytes`):* Tra bảng S-box 8-bit], ..box-proc, name: <r_sub>)
      node((0, 3), [*Dịch hàng (`ShiftRows`):* Dịch vòng 4 hàng của ma trận], ..box-proc, name: <r_shift>)
      node((0, 4), [*Trộn cột (`MixColumns`):* Nhân ma trận trên $"GF"(2^8)$], ..box-proc, name: <r_mix>)
      node((0, 5), [*Cộng khóa vòng (`AddRoundKey`):* XOR với khóa vòng $K_r$], ..box-proc, name: <r_add>)
      node((0, 6), [*Kiểm tra số vòng* ($r < 10$?)], ..box-cond, name: <cond>)
      node((0, 7.2), [*Vòng cuối (`SubBytes`)*], ..box-proc, name: <f_sub>)
      node((0, 8.2), [*Vòng cuối (`ShiftRows`)* (Bỏ qua `MixColumns`)], ..box-proc, name: <f_shift>)
      node((0, 9.2), [*Vòng cuối (`AddRoundKey`)* với khóa $K_(10)$], ..box-proc, name: <f_add>)
      node((0, 10.2), [*Khối bản mã 128-bit*], ..box-main, name: <out_blk>)

      edge(<in_blk>, <init_key>, "-|>")
      edge(<init_key>, <r_sub>, "-|>")
      edge(<r_sub>, <r_shift>, "-|>")
      edge(<r_shift>, <r_mix>, "-|>")
      edge(<r_mix>, <r_add>, "-|>")
      edge(<r_add>, <cond>, "-|>")
      edge(<cond>, <f_sub>, "-|>", label: [Vòng 10 (cuối)], label-side: left)
      edge(<cond.east>, (1.2, 6), (1.2, 2), <r_sub.east>, "-|>", label: [Vòng 1..9], label-pos: 0.45, label-side: right)
      edge(<f_sub>, <f_shift>, "-|>")
      edge(<f_shift>, <f_add>, "-|>")
      edge(<f_add>, <out_blk>, "-|>")
    },
  ),
  caption: [Lưu đồ thuật toán mã hóa khối AES-128 theo cấu trúc mạng thay thế – hoán vị (SPN)],
)

// --- LƯU ĐỒ CHẾ ĐỘ XÁC THỰC AES-GCM (FLETCHER ORTHOGONAL GRID) ---
#let fig-aes-gcm-flow = figure(
  f-diagram(
    spacing: (7mm, 6mm),
    node-stroke: 0.7pt + color-text-muted,
    node-corner-radius: 3pt,
    edge-stroke: 0.75pt + black,
    {
      let box-main = (fill: white, width: 58mm, inset: 4.5pt)
      let box-proc = (fill: color-surface-tint, width: 58mm, inset: 4.5pt)
      let box-side = (fill: white, width: 32mm, inset: 4.5pt)

      // Left column (J0 branch)
      node((-1, 0), align(center)[*Khối đếm đầu*\ $J_0 = "Nonce" || 1$], ..box-side, name: <cb_init>)
      node((-1, 2), align(center)[*Mã hóa*\ $"AES"_K (J_0)$], ..box-side, fill: color-surface-tint, name: <aes_j0>)

      // Center column (CTR + GHASH spine)
      node((0, 1), align(center)[*Tăng bộ đếm*\ $"CB"_i = "inc"_(32)("CB"_(i-1))$], ..box-proc, name: <cb_inc>)
      node((0, 2), align(center)[*Mã hóa khối*\ $"AES"_K ("CB"_i)$], ..box-proc, name: <aes_ctr>)
      node((0, 3), align(center)[*Phép XOR:*\ $C_i = P_i xor "AES"_K ("CB"_i)$], ..box-proc, name: <xor_p>)
      node((0, 4), align(center)[*Khối bản mã* $C_i$], ..box-main, name: <c_out>)
      node((0, 5), align(center)[*Hàm băm GHASH:*\ $X_i = (X_(i-1) xor C_i) dot H$], ..box-proc, name: <ghash_mul>)
      node((0, 6), align(center)[*Nhân khối độ dài:*\ $(X_m xor ("len"_(64)(A) || "len"_(64)(C))) dot H$], ..box-proc, name: <len_blk>)
      node((0, 7), align(center)[*XOR tạo thẻ:*\ $"GHASH" xor "AES"_K (J_0)$], ..box-proc, name: <tag_xor>)
      node((0, 8), align(center)[*Thẻ xác thực (Tag 128-bit)*], ..box-main, name: <tag_out>)

      // Right column (inputs P_i and H)
      node((1, 3), align(center)[*Khối bản rõ* $P_i$], ..box-side, name: <p_in>)
      node((1, 5), align(center)[*Khóa băm*\ $H = "AES"_K (0^(128))$], ..box-side, name: <h_gen>)

      // Edges (strictly orthogonal)
      edge(<cb_init>, <aes_j0>, "-|>")
      edge(<cb_init>, (0, 0), <cb_inc>, "-|>")
      edge(<cb_inc>, <aes_ctr>, "-|>")
      edge(<aes_ctr>, <xor_p>, "-|>")
      edge(<p_in>, <xor_p>, "-|>")
      edge(<xor_p>, <c_out>, "-|>")
      edge(<c_out>, <ghash_mul>, "-|>")
      edge(<h_gen>, <ghash_mul>, "-|>")
      edge(<ghash_mul>, <len_blk>, "-|>")
      edge(<len_blk>, <tag_xor>, "-|>")
      edge(<aes_j0>, (-1, 7), <tag_xor>, "-|>")
      edge(<tag_xor>, <tag_out>, "-|>")
    },
  ),
  caption: [Lưu đồ nguyên lý mã hóa dòng CTR và xác thực toàn vẹn GHASH trong chế độ AES-GCM],
)
