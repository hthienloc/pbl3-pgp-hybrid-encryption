#import "@preview/fletcher:0.5.6" as fletcher: diagram, node, edge

= Ví dụ RSA – Mã hóa và giải mã

Để kiểm chứng tính đúng đắn của giải thuật toán học đã lập trình, nhóm thực hiện chạy thử nghiệm quy trình với bộ tham số:
- Cặp khóa công khai / bí mật: $e = 17$, $d = 2753$, $n = 3233$.
- Thông điệp dạng số cần mã hóa: $M = 125$.

#align(center)[
  #table(
    columns: (1fr, 1.8fr, 1fr),
    fill: (x, y) => if y == 0 { rgb("#e0e7ff") } else if calc.even(y) { rgb("#f8fafc") } else { none },
    stroke: 0.5pt + rgb("#cbd5e1"),
    inset: 9pt,
    [*Giai đoạn*], [*Công thức toán học*], [*Kết quả*],
    [Thông điệp gốc], [Giá trị ban đầu $M$], [$125$],
    [Mã hóa bằng Public Key], [$C = M^e mod n = 125^(17) mod 3233$], [$1516$],
    [Giải mã bằng Private Key], [$M' = C^d mod n = 1516^(2753) mod 3233$], [$125$]
  )
]

== Chuỗi chuyển đổi dữ liệu

#v(0.3em)
#align(center)[
  #figure(
    diagram(
      spacing: (18mm, 10mm),
      node-stroke: 0.8pt + black,
      node-fill: none,
      node-corner-radius: 4pt,
      edge-stroke: 0.8pt + black,

      // Hàng 1: Mã hóa
      node((0, 0), align(center)[*Bản rõ*\ $M = 125$], name: <m>, stroke: 0.8pt + black),
      node((1.2, 0), align(center)[*Mã hóa RSA*\ $C = M^e mod n$], name: <enc>, stroke: 1.3pt + black),
      node((1.2, -0.9), align(center)[*Khóa công khai*\ $(e=17, n=3233)$], name: <pub>, stroke: (paint: black, thickness: 0.8pt, dash: "dash-dotted")),
      node((2.4, 0), align(center)[*Bản mã*\ $C = 1516$], name: <c>, stroke: 1.5pt + black),

      // Hàng 2: Giải mã
      node((2.4, 1.3), align(center)[*Giải mã RSA*\ $M' = C^d mod n$], name: <dec>, stroke: 1.3pt + black),
      node((3.6, 1.3), align(center)[*Khóa bí mật*\ $(d=2753, n=3233)$], name: <priv>, stroke: (paint: black, thickness: 0.8pt, dash: "dashed")),
      node((1.2, 1.3), align(center)[*Khôi phục*\ $M' = 125$], name: <m2>, stroke: 0.8pt + black),

      edge(<m>, <enc>, "-|>"),
      edge(<pub>, <enc>, "-|>"),
      edge(<enc>, <c>, "-|>"),
      edge(<c>, <dec>, "-|>"),
      edge(<priv>, <dec>, "-|>"),
      edge(<dec>, <m2>, "-|>"),
    ),
    caption: [Sơ đồ chu trình xử lý dữ liệu và khóa trong thuật toán RSA số học],
  )
]
#v(0.3em)

Quá trình giải mã cho kết quả $M' = 125$, trùng khớp hoàn toàn với giá trị gốc $M$, xác nhận tính toàn vẹn của cặp phép biến đổi $M^e mod n$ và $C^d mod n$.
