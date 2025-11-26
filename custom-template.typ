#set page(
  margin: (x: 1in, y: 1in),
)

#set text(
  font: "New Computer Modern",
  size: 11pt,
)

#set par(justify: true)

#set heading(numbering: "1.")

// Table styling with borders
#show table: it => {
  set table(
    stroke: (x, y) => (
      x: 0.5pt + black,
      y: 0.5pt + black,
    ),
    fill: (x, y) => if y == 0 { rgb("#3498db") } else if calc.rem(y, 2) == 0 { rgb("#f2f2f2") },
  )
  it
}

#show table.cell.where(y: 0): set text(fill: white, weight: "bold")

$body$


