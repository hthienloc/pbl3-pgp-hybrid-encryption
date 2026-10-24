#import "@preview/basic-report:0.5.0": *
#import "@preview/hydra:0.6.2": hydra

#let project(
  institution: "TRƯỜNG ĐẠI HỌC BÁCH KHOA – ĐẠI HỌC ĐÀ NẴNG\nKHOA ĐIỆN TỬ VÀ TRÍ TUỆ NHÂN TẠO",
  doc-category: "BÁO CÁO TIẾN ĐỘ – NHÓM 7",
  main-title: "PGP",
  sub-title: "Nguyên lý RSA và mô hình mã hóa lai RSA – AES",
  author-str: "Vũ Duy Dương (106230007), Huỳnh Thiện Lộc (106230052), Phan Vinh Sơn (106230059)",
  affiliation-str: "PBL3: Mạng máy tính | GVHD: TS. Trần Thị Minh Hạnh | Đà Nẵng, 2026",
  language: "vi",
  heading-color: rgb("#1d4ed8"),
  heading-font: "Liberation Sans",
  body-font: "Liberation Sans",
  body,
) = {
  // Đồng bộ cấu hình lề & trang thống nhất cho toàn bộ báo cáo
  let page-margin = (top: 2.5cm, bottom: 2.5cm, left: 2.8cm, right: 2.2cm)

  set document(title: main-title + " - " + sub-title, author: author-str)
  set text(lang: language, font: body-font, size: 11pt)
  set par(justify: true, leading: 0.75em, spacing: 1.65em, first-line-indent: 0em)

  // 1. TRANG BÌA (PHÂN BỔ ĐỀU VÀ HÀI HÒA)
  {
    set page(
      paper: "a4",
      margin: page-margin,
      header: none,
      footer: none,
    )
    set text(font: heading-font)

    // Khối 1: Đơn vị đào tạo
    align(center)[
      #text(size: 13pt, weight: "bold", fill: rgb("#1e293b"))[#institution]
      #v(0.4em)
      #line(length: 40%, stroke: 0.8pt + rgb("#94a3b8"))
    ]

    v(1.5fr)

    // Khối 2: Tên báo cáo & Tiêu đề
    align(center)[
      #text(size: 14pt, weight: "bold", fill: rgb("#475569"))[#doc-category]
      #v(0.8em)
      #text(size: 40pt, weight: "bold", fill: heading-color)[#main-title]
      #v(0.6em)
      #text(size: 19pt, weight: "regular", fill: rgb("#334155"))[#sub-title]
    ]

    v(2fr)

    // Khối 3: Thông tin học phần & Người hướng dẫn
    align(left)[
      #rect(
        width: 100%,
        stroke: 0.5pt + rgb("#cbd5e1"),
        fill: rgb("#f8fafc"),
        radius: 4pt,
        inset: 12pt,
      )[
        #grid(
          columns: (1fr),
          row-gutter: 0.8em,
          [
            #for item in affiliation-str.split("\n") [
              #if not item.contains("Đà Nẵng") [
                #text(size: 11pt)[#item] \
              ]
            ]
          ],
          [
            #line(length: 100%, stroke: 0.5pt + rgb("#e2e8f0"))
            #v(0.2em)
            #text(weight: "bold", size: 11pt)[Sinh viên thực hiện:] \
            #v(0.2em)
            #for item in author-str.split("\n") [
              #if not item.contains("Sinh viên") [
                #text(size: 11pt)[#item] \
              ]
            ]
          ]
        )
      ]
    ]

    v(1fr)

    // Khối 4: Địa điểm & Thời gian ở chân trang
    align(center)[
      #text(size: 11pt, fill: rgb("#64748b"), weight: "bold")[Đà Nẵng, 2026]
    ]
    v(0.5cm)
  }

  pagebreak()

  // 2. CẤU HÌNH TRANG NỘI DUNG & HEADER
  set page(
    paper: "a4",
    margin: page-margin,
    header: context {
      grid(
        columns: (1fr, 1fr),
        align: (left, right),
        row-gutter: 0.5em,
        text(font: heading-font, size: 9pt,
          context { hydra(1, use-last: false, skip-starting: false) }
        ),
        text(font: heading-font, size: 9pt, number-type: "lining",
          context { counter(page).display("1") }
        ),
        grid.cell(colspan: 2, line(length: 100%, stroke: 0.5pt + rgb("#cbd5e1"))),
      )
    },
    header-ascent: 1.5em,
  )

  // Định dạng tiêu đề theo phong cách basic-report
  set heading(numbering: "1.")
  show heading: set text(font: heading-font, fill: heading-color, weight: "bold")
  show heading: set par(justify: false)
  show heading.where(level: 1): it => v(2.5em, weak: true) + text(it) + v(0.8em)
  show heading.where(level: 2): it => v(1.5em) + text(it) + v(0.5em)
  show heading.where(level: 3): it => v(1.2em) + text(it) + v(0.4em)

  // 3. MỤC LỤC (CÙNG LỀ VÀ PHONG CÁCH)
  show outline.entry.where(level: 1): it => {
    set block(above: 1.6em)
    set text(font: heading-font, weight: "bold", size: 10pt)
    link(it.element.location(), it.indented(it.prefix(), it.body() + box(width: 1fr) + strong(it.page())))
  }
  show outline.entry.where(level: 2): it => {
    set block(above: 0.8em)
    set text(font: heading-font, size: 10pt)
    link(it.element.location(), it.indented(it.prefix(), it.body() + " " + box(width: 1fr, repeat([.], gap: 2pt)) + " " + it.page()))
  }

  counter(page).update(1)
  outline(
    title: text(font: heading-font, fill: heading-color)[MỤC LỤC],
    indent: auto,
  )

  pagebreak()

  // Định dạng trích dẫn theo dạng chỉ số trên (superscript) thanh thoát
  show cite: it => text(fill: heading-color, weight: "bold")[#super(it)]

  // Định dạng bảng toàn cục: Tiêu đề canh giữa, nội dung canh lề trái
  show table.cell: it => {
    if it.y == 0 {
      set text(weight: "bold")
      set align(center + horizon)
      it
    } else {
      set align(left + horizon)
      it
    }
  }

  body
}
