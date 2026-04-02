import { jsPDF } from 'jspdf'
import autoTable from 'jspdf-autotable'

// Page color palette — matches CSS variables in index.css
const INK      = [26, 24, 21]    // --ink
const INK_3    = [154, 149, 143] // --ink-3
const RED      = [192, 56, 42]   // --red
const WHITE    = [255, 254, 249] // --white
const PAPER    = [245, 241, 232] // --paper

let cachedFontBase64 = null

export async function generatePdf(words, language) {
  if (!cachedFontBase64) {
    const fontResp = await fetch(import.meta.env.BASE_URL + 'fonts/klee-one.ttf')
    if (!fontResp.ok) throw new Error(`Failed to load font: ${fontResp.status}`)
    const fontBuffer = await fontResp.arrayBuffer()
    cachedFontBase64 = btoa(
      new Uint8Array(fontBuffer).reduce((data, byte) => data + String.fromCharCode(byte), '')
    )
  }

  const doc = new jsPDF({ format: 'a4', unit: 'pt' })
  doc.addFileToVFS('KleeOne.ttf', cachedFontBase64)
  doc.addFont('KleeOne.ttf', 'KleeOne', 'normal')
  doc.setFont('KleeOne')

  // ── First-page header ──────────────────────────────────────────────────
  const pageWidth  = doc.internal.pageSize.width
  const pageHeight = doc.internal.pageSize.height
  const marginLeft = 40
  const marginRight = 40
  const headerY = 34

  doc.setFontSize(18)
  doc.setTextColor(...RED)
  doc.text('日本語', marginLeft, headerY)
  const jpWidth = doc.getTextWidth('日本語')
  doc.setTextColor(...INK)
  doc.text('Practice', marginLeft + jpWidth + 3, headerY)

  doc.setDrawColor(...INK)
  doc.setLineWidth(0.3)
  doc.line(marginLeft, headerY + 7, pageWidth - marginRight, headerY + 7)

  // ── Vocabulary table ───────────────────────────────────────────────────
  const CIRCLE = ['①','②','③','④','⑤','⑥','⑦','⑧','⑨','⑩']

  const rows = words.map(w => {
    const primary = w.kanji ? `${w.kanji}\n${w.kana}` : w.kana
    const reading = w.romaji
    const cell = w.meanings.map((m, i) => {
      const prefix = w.meanings.length > 1 ? `${CIRCLE[i] ?? `(${i+1})`} ` : ''
      const text = language === 'sv' && m.sv ? m.sv : m.en
      return m.note ? `${prefix}${text}\n${m.note}` : `${prefix}${text}`
    }).join('\n')
    return [primary, reading, cell]
  })

  const footerY = pageHeight - 18

  autoTable(doc, {
    head: [['Word', 'Reading', 'Meaning(s)']],
    body: rows,
    startY: headerY + 16,
    styles: { font: 'KleeOne', fontSize: 10, textColor: INK },
    headStyles: { font: 'KleeOne', fontStyle: 'normal', fillColor: INK, textColor: WHITE },
    alternateRowStyles: { fillColor: PAPER },
    columnStyles: {
      0: { cellWidth: 80, valign: 'top' },
      1: { cellWidth: 80 },
      2: { cellWidth: 'auto', valign: 'top' },
    },
    margin: { top: 40, left: marginLeft, right: marginRight, bottom: 30 },
    // Suppress default text for cells we render manually in didDrawCell
    willDrawCell: (data) => {
      if (data.section !== 'body') return
      const word = words[data.row.index]
      if (!word) return
      if (data.column.index === 0 && word.kanji) data.cell.text = []
      if (data.column.index === 2 && word.meanings.some(m => m.note)) data.cell.text = []
    },
    // Draw custom-colored text after the cell background has been painted
    didDrawCell: (data) => {
      if (data.section !== 'body') return
      const word = words[data.row.index]
      if (!word) return

      // getTextPos().y with valign:'top' = top of content area.
      // doc.text() expects the text baseline, which sits fontSize*0.85 below that top.
      const BASELINE_OFFSET = 10 * 0.85  // 8.5pt for 10pt font
      const lineH = 10 * 1.15            // 11.5pt line height

      if (data.column.index === 0 && word.kanji) {
        // Render kanji in INK and kana in lighter INK_3
        const { x } = data.cell.getTextPos()
        const y = data.cell.getTextPos().y + BASELINE_OFFSET

        doc.setFont('KleeOne')
        doc.setFontSize(10)
        doc.setTextColor(...INK)
        doc.text(word.kanji, x, y)

        doc.setFontSize(8)
        doc.setTextColor(...INK_3)
        doc.text(word.kana, x, y + lineH)

        doc.setFontSize(10)
        doc.setTextColor(...INK)
      } else if (data.column.index === 2 && word.meanings.some(m => m.note)) {
        // Render meaning text in INK and notes in lighter, smaller INK_3
        const { x } = data.cell.getTextPos()
        let y = data.cell.getTextPos().y + BASELINE_OFFSET
        const contentWidth = data.cell.width - data.cell.padding('horizontal')

        word.meanings.forEach((m, i) => {
          const prefix = word.meanings.length > 1 ? `${CIRCLE[i] ?? `(${i+1})`} ` : ''
          const text = language === 'sv' && m.sv ? m.sv : m.en
          doc.setFont('KleeOne')
          doc.setFontSize(10)
          doc.setTextColor(...INK)
          doc.splitTextToSize(`${prefix}${text}`, contentWidth).forEach(line => {
            doc.text(line, x, y)
            y += lineH
          })

          if (m.note) {
            doc.setFontSize(8.5)
            doc.setTextColor(...INK_3)
            doc.splitTextToSize(m.note, contentWidth).forEach(line => {
              doc.text(line, x, y)
              y += lineH
            })
          }
        })

        doc.setFontSize(10)
        doc.setTextColor(...INK)
      }
    },
    didDrawPage: ({ settings }) => {
      doc.setFont('KleeOne')
      doc.setFontSize(7)
      doc.setTextColor(...INK_3)
      doc.text(
        'Vocabulary: JMdict/EDRDG (CC BY-SA 3.0), Jonathan Waller JLPT lists  \u00b7  Font: Klee One (SIL OFL 1.1)  \u00b7  github.com/featurequest/practice-japanese',
        settings.margin.left,
        footerY
      )
      doc.setTextColor(...INK)
    },
  })

  // ── Page numbers ───────────────────────────────────────────────────────
  const totalPages = doc.internal.getNumberOfPages()
  for (let p = 1; p <= totalPages; p++) {
    doc.setPage(p)
    doc.setFont('KleeOne')
    doc.setFontSize(7)
    doc.setTextColor(...INK_3)
    doc.text(`${p} / ${totalPages}`, pageWidth - marginRight, footerY, { align: 'right' })
  }
  doc.setTextColor(...INK)

  doc.save('vocabulary-custom.pdf')
}
