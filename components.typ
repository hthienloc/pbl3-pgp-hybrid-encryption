#import "theme.typ": color-primary, color-accent, color-surface-tint, color-surface-subtle, color-border

#let info-box(title: "Gợi ý trình bày", content) = {
  rect(
    width: 100%,
    fill: color-surface-tint,
    stroke: (left: 3pt + color-accent),
    inset: 10pt,
    radius: (right: 4pt),
  )[
    #text(weight: "bold", fill: color-primary)[#title:] \
    #content
  ]
}

#let code-box(body) = {
  rect(
    width: 100%,
    fill: color-surface-subtle,
    stroke: 0.5pt + color-border,
    inset: 10pt,
    radius: 4pt,
    body
  )
}
