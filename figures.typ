#import "@preview/fletcher:0.5.6" as fletcher: diagram, node, edge
#import "@preview/chronos:0.3.0"
#import "@preview/diagraph:0.3.8": raw-render
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

// --- HÌNH 1: NGUYÊN LÝ MÃ HÓA VÀ GIẢI MÃ LAI RSA - AES (DÙNG DIAGRAPH AUTO-LAYOUT DỌC) ---
#let fig-hybrid-overview = figure(
  raw-render(
    ```dot
    digraph {
      rankdir=TB;
      nodesep=0.35;
      ranksep=0.38;
      node [penwidth=0.8, margin="0.08,0.05"];
      edge [penwidth=0.8, arrowsize=0.7, color="black"];

      // Quy ước hình dạng phân định Input/Output, Khóa và Khối xử lý
      // Input / Output dữ liệu: hình bình hành (parallelogram)
      m        [shape=parallelogram, style="filled", fillcolor="#ffffff"];
      cdata    [shape=parallelogram, style="filled", fillcolor="#ffffff"];
      ckey     [shape=parallelogram, style="filled", fillcolor="#ffffff"];
      b_cdata  [shape=parallelogram, style="filled", fillcolor="#ffffff"];
      b_ckey   [shape=parallelogram, style="filled", fillcolor="#ffffff"];
      m_out    [shape=parallelogram, style="filled", fillcolor="#ffffff"];

      // Khóa và tham số mã hóa: hình ellipse viền nét đứt
      key      [shape=ellipse, style="dashed,filled", fillcolor="#ffffff"];
      pub      [shape=ellipse, style="dashed,filled", fillcolor="#ffffff"];
      priv     [shape=ellipse, style="dashed,filled", fillcolor="#ffffff"];
      key_out  [shape=ellipse, style="dashed,filled", fillcolor="#ffffff"];

      // Khối xử lý logic (Logic Processing): hình hộp góc bo tròn có màu nền
      aes_enc  [shape=box, style="rounded,filled", fillcolor="#f1f5f9"];
      rsa_enc  [shape=box, style="rounded,filled", fillcolor="#f1f5f9"];
      rsa_dec  [shape=box, style="rounded,filled", fillcolor="#f1f5f9"];
      aes_dec  [shape=box, style="rounded,filled", fillcolor="#f1f5f9"];

      subgraph cluster_alice {
        label="Phía Alice (Mã hóa)";
        labeljust="l";
        style="rounded,dashed";
        color="#64748b";
        fontsize=10;
        { rank=same; m; key; pub; }
        m -> aes_enc         [style=solid];
        key -> aes_enc       [style=dashed];
        key -> rsa_enc       [style=dashed];
        pub -> rsa_enc       [style=dashed];
        aes_enc -> cdata     [style=solid];
        rsa_enc -> ckey      [style=solid];
      }

      subgraph cluster_bob {
        label="Phía Bob (Giải mã)";
        labeljust="l";
        style="rounded,dashed";
        color="#64748b";
        fontsize=10;
        { rank=same; b_cdata; b_ckey; priv; }
        b_cdata -> aes_dec   [style=solid];
        b_ckey -> rsa_dec    [style=solid];
        priv -> rsa_dec      [style=dashed];
        rsa_dec -> key_out   [style=dashed];
        key_out -> aes_dec   [style=dashed];
        aes_dec -> m_out     [style=solid];
      }

      cdata -> b_cdata       [style=dotted, label=" Kênh mạng\n(+ Nonce, Tag)"];
      ckey -> b_ckey         [style=dotted];
    }
    ```,
    labels: (
      "m": align(center)[*Bản rõ gốc*\ $M$],
      "key": align(center)[*Session Key*\ $K$ ngẫu nhiên],
      "pub": align(center)[*Public Key Bob*\ $(e_B, n)$],
      "aes_enc": align(center)[*Mã hóa AES*\ Dùng khóa $K$],
      "rsa_enc": align(center)[*Mã hóa RSA*\ Bảo vệ $K$],
      "cdata": align(center)[*Bản mã dữ liệu*\ $C_("data")$],
      "ckey": align(center)[*Khóa phiên mã hóa*\ $C_("key")$],
      "b_cdata": align(center)[*Bản mã dữ liệu*\ $C_("data")$],
      "b_ckey": align(center)[*Khóa phiên mã hóa*\ $C_("key")$],
      "priv": align(center)[*Private Key Bob*\ $(d_B, n)$],
      "rsa_dec": align(center)[*Giải mã RSA*\ Lấy lại $K$],
      "key_out": align(center)[*Session Key*\ $K$ khôi phục],
      "aes_dec": align(center)[*Giải mã AES*\ Dùng khóa $K$],
      "m_out": align(center)[*Bản rõ khôi phục*\ $M' = M$],
    ),
    width: 72%,
  ),
  caption: [Sơ đồ nguyên lý mã hóa và giải mã lai RSA – AES khép kín trong mô hình PGP @zhou2011],
)

// --- HÌNH 2: SƠ ĐỒ TUẦN TỰ TƯƠNG TÁC ALICE - BOB (DÙNG CHRONOS HỖ TRỢ MATH) ---
#let fig-sequence-interaction = figure(
  chronos.diagram(width: 100%, {
    import chronos: *
    _par("A", display-name: [*Alice*\ #text(size: 8pt, fill: luma(80))[Người gửi]], color: white, show-bottom: true)
    _par("C", display-name: [*Kênh mạng*\ #text(size: 8pt, fill: luma(80))[Truyền thông]], color: white, show-bottom: true)
    _par("B", display-name: [*Bob*\ #text(size: 8pt, fill: luma(80))[Người nhận]], color: white, show-bottom: true)

    _note("over", pos: "B", shape: "rect", color: luma(248))[
      #align(left)[
        *0. Sinh cặp khóa RSA:*\
        Public Key $(e_B, n)$, Private Key $(d_B, n)$
      ]
    ]
    _seq("B", "A", comment: [Công khai Public Key $(e_B, n)$], dashed: true)

    _note("over", pos: "A", shape: "rect", color: luma(248))[
      #align(left)[
        *1. Sinh khóa phiên* $K$ và vector $"IV"$\
        *2. Mã hóa AES-GCM:* $(C_("data"), "Tag") = "AES"_K (M, "IV")$\
        *3. Mã hóa RSA:* $C_("key") = "RSA"_(e_B)(K)$
      ]
    ]

    _seq("A", "C", comment: [Gửi gói tin PGP: $\{C_("key"), "IV", C_("data"), "Tag"\}$])
    _seq("C", "B", comment: [Tiếp nhận gói tin PGP])

    _note("over", pos: "B", shape: "rect", color: luma(248))[
      #align(left)[
        *4. Giải mã RSA:* $K = "RSA"_(d_B)(C_("key"))$\
        *5. Xác thực toàn vẹn:* Đối chiếu $"Tag"$ (GHASH)\
        *6. Giải mã AES-GCM:* $M = "AES"_K (C_("data"), "IV")$
      ]
    ]
  }),
  caption: [Sơ đồ tuần tự quy trình truyền thông mã hóa lai PGP giữa Alice và Bob],
)

// --- HÌNH 3: VÍ DỤ SỐ HỌC RSA (DÙNG DIAGRAPH AUTO-LAYOUT DỌC) ---
#let fig-rsa-numeric-example = figure(
  raw-render(
    ```dot
    digraph {
      rankdir=TB;
      nodesep=0.45;
      ranksep=0.38;
      node [penwidth=0.8, margin="0.08,0.05"];
      edge [penwidth=0.8, arrowsize=0.7, color="black"];

      // Input / Output dữ liệu: hình bình hành
      m      [shape=parallelogram, style="filled", fillcolor="#ffffff"];
      c      [shape=parallelogram, style="filled", fillcolor="#ffffff"];
      c_bob  [shape=parallelogram, style="filled", fillcolor="#ffffff"];
      m2     [shape=parallelogram, style="filled", fillcolor="#ffffff"];

      // Khóa bí mật và công khai: hình ellipse viền nét đứt
      pub    [shape=ellipse, style="dashed,filled", fillcolor="#ffffff"];
      priv   [shape=ellipse, style="dashed,filled", fillcolor="#ffffff"];

      // Khối xử lý logic (Logic Processing): hình hộp góc bo tròn có màu nền
      enc    [shape=box, style="rounded,filled", fillcolor="#f1f5f9"];
      dec    [shape=box, style="rounded,filled", fillcolor="#f1f5f9"];

      subgraph cluster_alice {
        label="Alice (Bên gửi)";
        style="rounded,dashed";
        color="#64748b";
        fontsize=10;
        { rank=same; m; pub; }
        m -> enc        [style=solid];
        pub -> enc      [style=dashed];
        enc -> c        [style=solid];
      }

      subgraph cluster_bob {
        label="Bob (Bên nhận)";
        style="rounded,dashed";
        color="#64748b";
        fontsize=10;
        { rank=same; c_bob; priv; }
        c_bob -> dec    [style=solid];
        priv -> dec     [style=dashed];
        dec -> m2       [style=solid];
      }

      c -> c_bob        [style=dotted, label=" Gửi qua mạng"];
    }
    ```,
    labels: (
      "m": align(center)[*Bản rõ*\ $M = 125$],
      "pub": align(center)[*Khóa công khai*\ $(e=17, n=3233)$],
      "enc": align(center)[*Mã hóa RSA*\ $C = M^e mod n$],
      "c": align(center)[*Bản mã*\ $C = 1516$],
      "c_bob": align(center)[*Bản mã nhận*\ $C = 1516$],
      "priv": align(center)[*Khóa bí mật*\ $(d=2753, n=3233)$],
      "dec": align(center)[*Giải mã RSA*\ $M' = C^d mod n$],
      "m2": align(center)[*Khôi phục*\ $M' = 125$],
    ),
    width: 55%,
  ),
  caption: [Sơ đồ chu trình xử lý dữ liệu và khóa trong ví dụ số học RSA giữa Alice và Bob],
)

// --- HÌNH 3: CẤU TRÚC KHUNG GÓI TIN VÀ PHÂN TÍCH CÚ PHÁP TẠI BỘ GIẢI MÃ BOB (DÙNG DIAGRAPH) ---
#let fig-packet-layout = figure(
  raw-render(
    ```dot
    digraph {
      rankdir=TB;
      nodesep=0.16;
      ranksep=0.35;
      node [shape=box, style="rounded,filled", fillcolor="white", penwidth=0.8, margin="0.08,0.05"];
      edge [penwidth=0.8, arrowsize=0.7, color="black"];

      subgraph cluster_packet {
        label="Khung gói tin TCP: [4B Big-Endian Length] + [JSON Envelope UTF-8]";
        style="rounded,dashed";
        color="#64748b";
        fontsize=10;
        { rank=same; f_len; f_key; f_nonce; f_data; f_tag; }
        f_len -> f_key -> f_nonce -> f_data -> f_tag [style=invis];
      }

      subgraph cluster_bob {
        label="Phân tích cú pháp tại bộ nhận của Bob";
        style="rounded,dashed";
        color="#64748b";
        fontsize=10;
        { rank=same; p_len; p_key; p_nonce; p_data; p_tag; }
        p_len -> p_key -> p_nonce -> p_data -> p_tag [style=invis];
      }

      f_len -> p_len;
      f_key -> p_key;
      f_nonce -> p_nonce;
      f_data -> p_data;
      f_tag -> p_tag;
    }
    ```,
    labels: (
      "f_len": align(center)[*4 Bytes (Big-Endian)*\ *Độ dài gói*\ #text(size: 7.5pt)[Tiền tố độ dài]],
      "f_key": align(center)[*Khóa phiên mã hóa*\ $C_("key")$\ #text(size: 7.5pt)[Mã hóa RSA]],
      "f_nonce": align(center)[*Vector khởi tạo*\ *Nonce / IV (12B)*\ #text(size: 7.5pt)[Dùng một lần]],
      "f_data": align(center)[*Bản mã dữ liệu*\ $C_("data")$\ #text(size: 7.5pt)[Mã hóa AES-CTR]],
      "f_tag": align(center)[*Thẻ xác thực*\ *Auth Tag (16B)*\ #text(size: 7.5pt)[Hàm băm GHASH]],
      "p_len": align(center)[*1. Đọc khung*\ Đọc đủ độ dài\ #text(size: 7.5pt)[Tách gói JSON]],
      "p_key": align(center)[*2. Giải mã RSA*\ Khôi phục khóa $K'$\ #text(size: 7.5pt)[Dùng khóa bí mật]],
      "p_nonce": align(center)[*3. Khởi tạo bộ đếm*\ Nạp Nonce / IV\ #text(size: 7.5pt)[Tạo $J_0$ và $"CB"_i$]],
      "p_data": align(center)[*4. Giải mã AES*\ Giải mã dòng CTR\ #text(size: 7.5pt)[Khôi phục $M'$]],
      "p_tag": align(center)[*5. Kiểm tra Tag*\ Đối chiếu GHASH\ #text(size: 7.5pt)[Chống sửa đổi]],
    ),
    width: 98%,
  ),
  caption: [Sơ đồ cấu trúc khung gói tin (Packet Framing) và luồng phân tích cú pháp tại bộ nhận của Bob],
)


// --- HÌNH 5: SƠ ĐỒ TUẦN TỰ TRUYỀN THÔNG QUA SOCKET TCP (DÙNG CHRONOS) ---
#let fig-socket-sequence = figure(
  chronos.diagram(width: 100%, {
    import chronos: *
    _par("A", display-name: [*Alice (TCP Client)*\ #text(size: 8pt, fill: luma(80))[Máy gửi]], color: white, show-bottom: true)
    _par("C", display-name: [*Kênh TCP :5000*\ #text(size: 8pt, fill: luma(80))[Length-prefixed JSON]], color: white, show-bottom: true)
    _par("B", display-name: [*Bob (TCP Server)*\ #text(size: 8pt, fill: luma(80))[Máy nhận]], color: white, show-bottom: true)

    _note("over", pos: "B", shape: "rect", color: luma(248))[
      #align(left)[
        *0. Khởi tạo Server:*\
        Sinh khóa RSA $(e_B, n), (d_B, n)$\
        Lắng nghe tại cổng 5000
      ]
    ]

    _seq("A", "B", comment: [1. Yêu cầu lấy khóa công khai])
    _seq("B", "A", comment: [2. Trả Public Key $(e_B, n)$], dashed: true)

    _note("across", shape: "rect", color: luma(248))[
      *3. Xác thực ngoại vi (Out-of-Band):* Đối chiếu SHA-256 Public Key Fingerprint
    ]

    _note("over", pos: "A", shape: "rect", color: luma(248))[
      #align(left)[
        *4. Đóng gói Hybrid PGP:*\
        - Sinh khóa phiên $K$ (16B) & $"nonce"$ (12B)\
        - $(C_("data"), "Tag") = "AES-GCM"_K (M, "nonce")$\
        - $C_("key") = "RSA"_(e_B)(K)$
      ]
    ]

    _seq("A", "C", comment: [5. Gửi `[4B Length] + JSON Envelope`])
    _seq("C", "B", comment: [$C_("key")$ (hex), $"nonce", C_("data"), "Tag"$ (Base64)])

    _note("over", pos: "B", shape: "rect", color: luma(248))[
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

// --- LƯU ĐỒ THUẬT TOÁN AES-128 (SPN) ---
#let fig-aes-spn-flow = figure(
  raw-render(
    ```dot
    digraph {
      rankdir=TB;
      nodesep=0.25;
      ranksep=0.3;
      node [shape=box, style="rounded,filled", fillcolor="white", penwidth=0.8, margin="0.1,0.06"];
      edge [penwidth=0.8, arrowsize=0.7, color="black"];

      in_blk -> init_key -> r_sub -> r_shift -> r_mix -> r_add -> cond;
      cond -> r_sub [label=" Vòng 1..9"];
      cond -> f_sub [label=" Vòng 10 (cuối)"];
      f_sub -> f_shift -> f_add -> out_blk;
    }
    ```,
    labels: (
      "in_blk": align(center)[*Khối bản rõ 128-bit* (Ma trận trạng thái $4 times 4$ byte)],
      "init_key": align(center)[*Khởi tạo vòng 0:* Cộng khóa vòng (`AddRoundKey`)],
      "r_sub": align(center)[*Thế phi tuyến (`SubBytes`):* Tra bảng S-box 8-bit],
      "r_shift": align(center)[*Dịch hàng (`ShiftRows`):* Dịch vòng 4 hàng của ma trận],
      "r_mix": align(center)[*Trộn cột (`MixColumns`):* Nhân ma trận trên $"GF"(2^8)$],
      "r_add": align(center)[*Cộng khóa vòng (`AddRoundKey`):* Phép XOR với khóa vòng $K_r$],
      "cond": align(center)[*Kiểm tra số vòng* ($r < 10$?)],
      "f_sub": align(center)[*Vòng cuối (`SubBytes`)*],
      "f_shift": align(center)[*Vòng cuối (`ShiftRows`)* (Bỏ qua `MixColumns`)],
      "f_add": align(center)[*Vòng cuối (`AddRoundKey`)* với khóa $K_(10)$],
      "out_blk": align(center)[*Khối bản mã 128-bit*],
    ),
    width: 68%,
  ),
  caption: [Lưu đồ thuật toán mã hóa khối AES-128 theo cấu trúc mạng thay thế – hoán vị (SPN)],
)

// --- LƯU ĐỒ CHẾ ĐỘ XÁC THỰC AES-GCM ---
#let fig-aes-gcm-flow = figure(
  raw-render(
    ```dot
    digraph {
      rankdir=TB;
      nodesep=0.25;
      ranksep=0.32;
      node [shape=box, style="rounded,filled", fillcolor="white", penwidth=0.8, margin="0.1,0.06"];
      edge [penwidth=0.8, arrowsize=0.7, color="black"];

      { rank=same; cb_init; h_gen; }
      cb_init -> cb_inc -> aes_ctr -> xor_p -> c_out;
      p_in -> xor_p;
      c_out -> ghash_mul;
      h_gen -> ghash_mul;
      ghash_mul -> len_blk -> tag_xor -> tag_out;
      cb_init -> aes_j0 -> tag_xor;
    }
    ```,
    labels: (
      "cb_init": align(center)[*Khối đếm đầu* $J_0 = "Nonce" || 1$],
      "h_gen": align(center)[*Khóa băm* $H = "AES"_K (0^(128))$],
      "cb_inc": align(center)[*Tăng bộ đếm* $"CB"_i = "inc"_(32)("CB"_(i-1))$],
      "aes_ctr": align(center)[*Mã hóa khối* $"AES"_K ("CB"_i)$],
      "p_in": align(center)[*Khối bản rõ* $P_i$],
      "xor_p": align(center)[*Phép XOR:* $C_i = P_i xor "AES"_K ("CB"_i)$],
      "c_out": align(center)[*Khối bản mã* $C_i$],
      "ghash_mul": align(center)[*Hàm băm GHASH:* $X_i = (X_(i-1) xor C_i) dot H$ trên $"GF"(2^(128))$],
      "len_blk": align(center)[*Nhân khối độ dài:* $(X_m xor ("len"_(64)(A) || "len"_(64)(C))) dot H$],
      "aes_j0": align(center)[*Mã hóa* $"AES"_K (J_0)$],
      "tag_xor": align(center)[*XOR tạo thẻ:* $"GHASH" xor "AES"_K (J_0)$],
      "tag_out": align(center)[*Thẻ xác thực (Tag 128-bit)*],
    ),
    width: 92%,
  ),
  caption: [Lưu đồ nguyên lý mã hóa dòng CTR và xác thực toàn vẹn GHASH trong chế độ AES-GCM],
)
