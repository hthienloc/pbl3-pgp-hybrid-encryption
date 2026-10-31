#import "@preview/basic-report:0.5.0": *
#import "@preview/hydra:0.6.2": hydra
#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.8": codly-languages

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

  // 1. TRANG BÌA (CHUẨN BÌA ĐẠI HỌC VIỆT NAM – KHUNG VIỀN ĐÔI & LOGO)
  {
    set page(
      paper: "a4",
      margin: (top: 2cm, bottom: 2cm, left: 2.5cm, right: 2cm),
      header: none,
      footer: none,
      background: pad(
        top: 1.5cm,
        bottom: 1.5cm,
        left: 2cm,
        right: 1.5cm,
        rect(
          width: 100%,
          height: 100%,
          stroke: 2pt + heading-color,
          inset: 3pt,
          rect(
            width: 100%,
            height: 100%,
            stroke: 0.6pt + heading-color,
          ),
        ),
      ),
    )
    set text(font: heading-font)

    v(0.6cm)

    // Khối 1: Đơn vị đào tạo
    align(center)[
      #set par(leading: 0.65em)
      #text(size: 13pt, weight: "bold", fill: rgb("#0f172a"))[ĐẠI HỌC ĐÀ NẴNG] \
      #text(size: 13.5pt, weight: "bold", fill: heading-color)[TRƯỜNG ĐẠI HỌC BÁCH KHOA] \
      #text(size: 12pt, weight: "bold", fill: rgb("#334155"))[KHOA ĐIỆN TỬ VÀ TRÍ TUỆ NHÂN TẠO]
      #v(0.3em)
      #line(length: 45%, stroke: 1pt + rgb("#94a3b8"))
    ]

    v(0.8fr)

    // Khối 2: Logo trường
    align(center)[
      #image("logo_bachkhoa.png", width: 3.4cm)
    ]

    v(0.9fr)

    // Khối 3: Tên báo cáo & Đề tài
    align(center)[
      #text(size: 14pt, weight: "bold", tracking: 0.5pt, fill: rgb("#1e293b"))[
        BÁO CÁO ĐỒ ÁN HỌC PHẦN
      ] \
      #v(0.2em)
      #text(size: 12.5pt, weight: "bold", fill: rgb("#475569"))[
        PBL3: MẠNG MÁY TÍNH – NHÓM 7
      ]

      #v(1.2em)

      #block(
        width: 90%,
        inset: (x: 10pt, y: 12pt),
        stroke: (top: 1.2pt + heading-color, bottom: 1.2pt + heading-color),
        fill: rgb("#f8fafc"),
      )[
        #set par(leading: 0.6em)
        #text(size: 11pt, weight: "bold", fill: rgb("#475569"))[ĐỀ TÀI:] \
        #v(0.3em)
        #text(size: 26pt, weight: "bold", fill: heading-color)[#upper(main-title)] \
        #v(0.4em)
        #text(size: 14pt, weight: "bold", fill: rgb("#1e293b"))[#upper(sub-title)]
      ]
    ]

    v(1.3fr)

    // Khối 4: Bảng thông tin GVHD & Sinh viên thực hiện
    align(center)[
      #block(width: 88%)[
        #set align(left)
        #table(
          columns: (38pt, 1fr, 110pt),
          stroke: 0.5pt + rgb("#cbd5e1"),
          inset: (x: 10pt, y: 8pt),
          fill: (x, y) => if y == 0 or y == 1 { rgb("#f1f5f9") } else if y == 2 { rgb("#f8fafc") } else { none },
          table.cell(colspan: 3)[
            #text(weight: "bold", fill: rgb("#0f172a"))[Giảng viên hướng dẫn:] TS. Trần Thị Minh Hạnh
          ],
          table.cell(colspan: 3)[
            #text(weight: "bold", fill: rgb("#0f172a"))[Sinh viên thực hiện (Nhóm 7):]
          ],
          align(center)[*STT*], [*Họ và tên*], align(center)[*MSSV*],
          align(center)[1], [Vũ Duy Dương], align(center)[`106230007`],
          align(center)[2], [Huỳnh Thiện Lộc], align(center)[`106230052`],
          align(center)[3], [Phan Vinh Sơn], align(center)[`106230059`],
        )
      ]
    ]

    v(1fr)

    // Khối 5: Địa điểm & Thời gian ở chân trang
    align(center)[
      #line(length: 25%, stroke: 0.6pt + rgb("#cbd5e1"))
      #v(0.3em)
      #text(size: 11.5pt, fill: rgb("#1e293b"), weight: "bold")[Đà Nẵng, năm 2026]
    ]
    v(0.4cm)
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
  // Mỗi section (heading cấp 1) bắt đầu ở trang mới; weak tránh tạo trang trống
  show heading.where(level: 1): it => pagebreak(weak: true) + v(2.5em, weak: true) + it + v(0.8em, weak: true)
  show heading.where(level: 2): it => v(1.5em, weak: true) + it + v(0.5em, weak: true)
  show heading.where(level: 3): it => v(1.2em, weak: true) + it + v(0.4em, weak: true)

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

  // Tích hợp codly cho code blocks chuyên nghiệp, tự động ngắt trang mượt mà
  // JetBrains Mono hiển thị dấu tiếng Việt đúng vị trí (DejaVu Sans Mono bị lệch dấu);
  // tắt ligature (calt) để giữ nguyên toán tử như `!=`, `==`
  show raw: set text(ligatures: false, features: (calt: 0))
  show raw.where(block: true): set text(size: 8.5pt, font: ("JetBrains Mono", "Noto Sans Mono", "Liberation Mono"))
  show: codly-init.with()
  codly(
    languages: codly-languages,
    zebra-fill: rgb("#f8fafc"),
    stroke: 0.5pt + rgb("#e2e8f0"),
    radius: 4pt,
  )

  // Định dạng inline code
  show raw.where(block: false): it => {
    box(
      fill: rgb("#f1f5f9"),
      inset: (x: 3.5pt, y: 1.5pt),
      baseline: 0%,
      radius: 3pt,
      text(size: 9pt, font: ("JetBrains Mono", "Noto Sans Mono", "Liberation Mono"), fill: rgb("#0f172a"))[#it]
    )
  }

  body
}
