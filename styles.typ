#import "@preview/fletcher:0.5.6" as fletcher: node, edge

// --- BẢNG ĐẶC TẢ ĐỒ THỊ CHUẨN MONOCHROME ---
#let stroke-data = 0.8pt + black
#let stroke-process = 1.3pt + black
#let stroke-package = 1.5pt + black
#let stroke-key = (paint: black, thickness: 0.8pt, dash: "dashed")
#let stroke-auth = (paint: black, thickness: 0.8pt, dash: "dash-dotted")
#let stroke-network = (paint: black, thickness: 1pt, dash: "dash-dotted")
#let stroke-axis = 0.5pt + black

// Icon hình học đại diện cho Alice (Nữ) và Bob (Nam)
#let user-icon-alice = {
  box(width: 13pt, height: 13pt)[
    #place(top + center, circle(radius: 2.8pt, stroke: 0.8pt + black))
    #place(bottom + center, polygon(
      (0pt, 6pt),
      (5pt, 0pt),
      (10pt, 6pt),
      fill: none,
      stroke: 0.8pt + black
    ))
  ]
}

#let user-icon-bob = {
  box(width: 13pt, height: 13pt)[
    #place(top + center, circle(radius: 2.8pt, stroke: 0.8pt + black))
    #place(bottom + center, rect(
      width: 9pt,
      height: 5.5pt,
      radius: (top: 2.5pt),
      fill: none,
      stroke: 0.8pt + black
    ))
  ]
}

// Huy hiệu thực thể
#let entity-badge(name, role, gender: "female") = {
  stack(
    dir: ttb,
    spacing: 2pt,
    if gender == "female" { user-icon-alice } else { user-icon-bob },
    text(size: 8pt, weight: "bold")[#name],
    text(size: 7pt, fill: luma(90))[#role]
  )
}

// Hàm tiện ích tạo Node theo ngữ nghĩa
#let d-node(pos, title, sub: none, kind: "data", name: none, radius: 3pt, width: auto) = {
  let s = if kind == "process" { stroke-process }
    else if kind == "key" { stroke-key }
    else if kind == "auth" { stroke-auth }
    else if kind == "package" { stroke-package }
    else { stroke-data }

  node(
    pos,
    align(center)[
      #text(size: 8pt)[#strong(title)]
      #if sub != none [ \ #text(size: 8pt)[#sub] ]
    ],
    name: name,
    stroke: s,
    fill: none,
    corner-radius: radius,
    width: width,
  )
}

// Bảng biểu chuẩn hóa đơn sắc (Monochrome Table)
#let report-table(columns: (1fr, 1fr), headers: (), rows: ()) = {
  table(
    columns: columns,
    fill: (x, y) => if y == 0 { luma(242) } else if calc.even(y) { luma(250) } else { none },
    stroke: 0.5pt + luma(180),
    inset: 8pt,
    ..headers.map(h => align(center)[#strong(h)]),
    ..rows.flatten()
  )
}
