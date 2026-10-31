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
      node [shape=box, style="rounded,filled", fillcolor="white", penwidth=0.8, margin="0.10,0.06"];
      edge [penwidth=0.8, arrowsize=0.7, color="black"];

      subgraph cluster_alice {
        label="Phía Alice (Mã hóa)";
        labeljust="l";
        style="rounded,dashed";
        color="#64748b";
        fontsize=10;
        { rank=same; m; key; pub; }
        m -> aes_enc;
        key -> aes_enc;
        key -> rsa_enc;
        pub -> rsa_enc;
        aes_enc -> cdata;
        rsa_enc -> ckey;
      }

      subgraph cluster_bob {
        label="Phía Bob (Giải mã)";
        labeljust="l";
        style="rounded,dashed";
        color="#64748b";
        fontsize=10;
        { rank=same; b_cdata; b_ckey; priv; }
        b_cdata -> aes_dec;
        b_ckey -> rsa_dec;
        priv -> rsa_dec;
        rsa_dec -> key_out;
        key_out -> aes_dec;
        aes_dec -> m_out;
      }

      cdata -> b_cdata [style=dashed, label=" Kênh mạng"];
      ckey -> b_ckey [style=dashed];
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
  caption: [Sơ đồ nguyên lý mã hóa và giải mã lai RSA – AES khép kín trong mô hình PGP],
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
      node [shape=box, style="rounded,filled", fillcolor="white", penwidth=0.8, margin="0.10,0.06"];
      edge [penwidth=0.8, arrowsize=0.7, color="black"];

      subgraph cluster_alice {
        label="Alice (Bên gửi)";
        style="rounded,dashed";
        color="#64748b";
        fontsize=10;
        { rank=same; m; pub; }
        m -> enc;
        pub -> enc;
        enc -> c;
      }

      subgraph cluster_bob {
        label="Bob (Bên nhận)";
        style="rounded,dashed";
        color="#64748b";
        fontsize=10;
        { rank=same; c_bob; priv; }
        c_bob -> dec;
        priv -> dec;
        dec -> m2;
      }

      c -> c_bob [style=dashed, label=" Gửi qua mạng"];
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

// --- HÌNH 4: CẤU TRÚC GÓI DỮ LIỆU ĐÓNG GÓI VÀ PHÂN TÍCH CÚ PHÁP TẠI BỘ GIẢI MÃ BOB (DÙNG DIAGRAPH) ---
#let fig-packet-layout = figure(
  raw-render(
    ```dot
    digraph {
      rankdir=TB;
      nodesep=0.18;
      ranksep=0.35;
      node [shape=box, style="rounded,filled", fillcolor="white", penwidth=0.8, margin="0.08,0.05"];
      edge [penwidth=0.8, arrowsize=0.7, color="black"];

      subgraph cluster_packet {
        label="Cấu trúc khung gói tin PGP (Byte Stream)";
        style="rounded,dashed";
        color="#64748b";
        fontsize=10;
        { rank=same; f_key; f_nonce; f_data; f_tag; }
        f_key -> f_nonce -> f_data -> f_tag [style=invis];
      }

      subgraph cluster_bob {
        label="Phân tích cú pháp tại bộ nhận của Bob";
        style="rounded,dashed";
        color="#64748b";
        fontsize=10;
        { rank=same; p_key; p_nonce; p_data; p_tag; }
        p_key -> p_nonce -> p_data -> p_tag [style=invis];
      }

      f_key -> p_key;
      f_nonce -> p_nonce;
      f_data -> p_data;
      f_tag -> p_tag;
    }
    ```,
    labels: (
      "f_key": align(center)[*0 .. 255 (256B)*\ *Khóa RSA* $C_("key")$\ #text(size: 7.5pt)[Khóa phiên mã hóa]],
      "f_nonce": align(center)[*256 .. 267 (12B)*\ *Nonce / IV*\ #text(size: 7.5pt)[Vector GCM]],
      "f_data": align(center)[*268 .. 268+L-1*\ *Bản mã* $C_("data")$\ #text(size: 7.5pt)[Dữ liệu AES-GCM]],
      "f_tag": align(center)[*Cuối cùng (16B)*\ *Auth Tag*\ #text(size: 7.5pt)[Mã băm GHASH]],
      "p_key": align(center)[*1. Giải mã RSA*\ `rsa_decrypt()`\ #text(size: 7.5pt)[Lấy khóa $K$]],
      "p_nonce": align(center)[*2. Nạp IV*\ `AES.new(K, ...)`\ #text(size: 7.5pt)[Nạp nonce]],
      "p_data": align(center)[*3. Giải mã AES*\ `decrypt()`\ #text(size: 7.5pt)[Khôi phục $M$]],
      "p_tag": align(center)[*4. Kiểm thực*\ `verify(tag)`\ #text(size: 7.5pt)[Chống giả mạo]],
    ),
    width: 95%,
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
        `listen(0.0.0.0:5000)`
      ]
    ]

    _seq("A", "B", comment: [1. Yêu cầu khóa: `{"action": "GET_PUBLIC_KEY"}`])
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

    _seq("B", "A", comment: [7. Phản hồi kết quả: `{"status": "OK" | "ERROR"}`], dashed: true)
  }),
  caption: [Sơ đồ tuần tự mô phỏng PGP Hybrid qua Socket TCP giữa máy Alice và máy Bob],
)
