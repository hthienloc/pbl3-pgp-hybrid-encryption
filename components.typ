#let info-box(title: "Gợi ý trình bày", content) = {
  rect(
    width: 100%,
    fill: rgb("#f1f5f9"),
    stroke: (left: 3pt + rgb("#2563eb")),
    inset: 10pt,
    radius: (right: 4pt),
  )[
    #text(weight: "bold", fill: rgb("#1e40af"))[#title:] \
    #content
  ]
}

#let code-box(body) = {
  rect(
    width: 100%,
    fill: rgb("#f8fafc"),
    stroke: 0.5pt + rgb("#cbd5e1"),
    inset: 10pt,
    radius: 4pt,
    body
  )
}
