#import "@preview/basic-report:0.5.0": *
#import "@preview/hydra:0.6.2": hydra
#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.8": codly-languages
#import "theme.typ": (
  font-body,
  font-heading,
  font-mono,
  color-primary,
  color-text-dark,
  color-text-muted,
  color-surface-tint,
  color-surface-subtle,
  color-border,
  color-border-light,
)

#let project(
  institution: "TRƯỜNG ĐẠI HỌC BÁCH KHOA – ĐẠI HỌC ĐÀ NẴNG\nKHOA ĐIỆN TỬ VÀ TRÍ TUỆ NHÂN TẠO",
  doc-category: "BÁO CÁO TIẾN ĐỘ – NHÓM 7",
  main-title: "PGP",
  sub-title: "Nguyên lý RSA và mô hình mã hóa lai RSA – AES",
  author-str: "Vũ Duy Dương (106230007), Huỳnh Thiện Lộc (106230052), Phan Vĩnh Sơn (106230059)",
  affiliation-str: "PBL3: Mạng máy tính | GVHD: TS. Trần Thị Minh Hạnh | Đà Nẵng, 2026",
  language: "vi",
  heading-color: color-primary,
  heading-font: font-heading,
  body-font: font-body,
  body,
) = {
  // Đồng bộ cấu hình lề 2.54cm (1 inch) & cỡ chữ 13pt, giãn dòng ~1.3 theo mẫu
  let page-margin = (top: 2.54cm, bottom: 2.54cm, left: 2.54cm, right: 2.54cm)

  set document(title: main-title + " - " + sub-title, author: author-str)
  set text(lang: language, font: body-font, size: 13pt)
  set par(justify: true, leading: 0.65em, spacing: 1.0em, first-line-indent: (amount: 1cm, all: true))
  set math.equation(numbering: "(1)")

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
    set text(font: heading-font, size: 12pt, fill: color-text-dark)

    v(0.6cm)

    // Khối 1: Đơn vị đào tạo
    align(center)[
      #set par(leading: 0.65em)
      #text(weight: "bold")[ĐẠI HỌC ĐÀ NẴNG] \
      #text(weight: "bold", fill: heading-color)[TRƯỜNG ĐẠI HỌC BÁCH KHOA] \
      #text(weight: "bold")[KHOA ĐIỆN TỬ VÀ TRÍ TUỆ NHÂN TẠO]
      #v(0.3em)
      #line(length: 40%, stroke: 0.8pt + heading-color)
    ]

    v(0.8fr)

    // Khối 2: Logo trường
    align(center)[
      #image("logo_bachkhoa.png", width: 3.2cm)
    ]

    v(0.9fr)

    // Khối 3: Tên báo cáo & Đề tài
    align(center)[
      #text(size: 14pt, weight: "bold")[
        #doc-category
      ] \
      #v(0.2em)
      #text(size: 12pt, weight: "bold")[
        PBL3: MẠNG MÁY TÍNH
      ]

      #v(1.2em)

      #block(
        width: 90%,
        inset: (x: 12pt, y: 14pt),
        stroke: (top: 1.2pt + heading-color, bottom: 1.2pt + heading-color),
        fill: color-surface-subtle,
      )[
        #set par(leading: 0.65em)
        #text(size: 12pt, weight: "bold")[ĐỀ TÀI] \
        #v(0.4em)
        #text(size: 22pt, weight: "bold", fill: heading-color)[#upper(main-title)] \
        #v(0.4em)
        #text(size: 13pt, weight: "bold")[#upper(sub-title)]
      ]
    ]

    v(1.2fr)

    // Khối 4: Bảng thông tin GVHD & Sinh viên thực hiện
    align(center)[
      #block(width: 88%)[
        #set align(left)
        #set text(size: 12pt)
        #table(
          columns: (38pt, 1fr, 100pt),
          stroke: 0.5pt + color-border,
          inset: (x: 10pt, y: 7pt),
          fill: (x, y) => if y <= 2 { color-surface-subtle } else { none },
          table.cell(colspan: 3)[
            *Giảng viên hướng dẫn:* TS. Trần Thị Minh Hạnh
          ],
          table.cell(colspan: 3)[
            *Sinh viên thực hiện (Nhóm 7):*
          ],
          align(center)[*STT*], [*Họ và tên*], align(center)[*MSSV*],
          align(center)[1], [Vũ Duy Dương], align(center)[`106230007`],
          align(center)[2], [Huỳnh Thiện Lộc], align(center)[`106230052`],
          align(center)[3], [Phan Vĩnh Sơn], align(center)[`106230059`],
        )
      ]
    ]

    v(1fr)

    // Khối 5: Địa điểm & Thời gian ở chân trang
    align(center)[
      #line(length: 25%, stroke: 0.6pt + color-border)
      #v(0.3em)
      #text(size: 12pt, weight: "bold")[Đà Nẵng, năm 2026]
    ]
    v(0.4cm)
  }

  pagebreak()

  // 2. CẤU HÌNH TRANG NỘI DUNG, HEADER & FOOTER (SỐ TRANG Ở GIỮA CHÂN TRANG)
  set page(
    paper: "a4",
    margin: page-margin,
    header: context {
      grid(
        columns: (1fr,),
        align: left,
        row-gutter: 0.5em,
        text(font: heading-font, size: 10pt, fill: color-text-muted,
          context { hydra(1, use-last: false, skip-starting: false) }
        ),
        line(length: 100%, stroke: 0.5pt + color-border),
      )
    },
    header-ascent: 1.5em,
    footer: context {
      align(center)[
        #text(font: heading-font, size: 11pt, number-type: "lining")[
          #counter(page).display("1")
        ]
      ]
    },
  )

  // Định dạng tiêu đề
  set heading(numbering: "1.")
  show heading: set text(font: heading-font, fill: heading-color, weight: "bold")
  show heading: set par(justify: false)
  show heading.where(level: 1): it => v(1.5em, weak: true) + it + v(0.6em, weak: true)
  show heading.where(level: 2): it => v(1.2em, weak: true) + it + v(0.4em, weak: true)
  show heading.where(level: 3): it => v(1em, weak: true) + it + v(0.3em, weak: true)

  // Định dạng chú thích Hình (dưới) và Bảng (trên) theo mẫu: "Hình 1. ...", "Bảng 1. ..."
  set figure.caption(separator: [. ])
  show figure.where(kind: table): set figure.caption(position: top)
  show figure.caption: set text(size: 12pt)

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

  // Trích dẫn chuẩn IEEE đặt ngang hàng với văn bản ([1], [2])

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
  show raw.where(block: true): set text(size: 9pt, font: font-mono)
  show: codly-init.with()
  codly(
    languages: codly-languages,
    zebra-fill: color-surface-subtle,
    stroke: 0.5pt + color-border-light,
    radius: 4pt,
  )

  // Định dạng inline code
  show raw.where(block: false): it => {
    box(
      fill: color-surface-tint,
      inset: (x: 3.5pt, y: 1.5pt),
      baseline: 0%,
      radius: 3pt,
      text(size: 9pt, font: font-mono, fill: color-text-dark)[#it]
    )
  }

  body
}
