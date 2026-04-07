import { useEffect } from 'react'
import { Link } from 'react-router-dom'

export default function Landing() {
  useEffect(() => {
    const io = new IntersectionObserver(
      entries => entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('in') }),
      { threshold: 0.07, rootMargin: '0px 0px -28px 0px' }
    )
    document.querySelectorAll('.reveal').forEach(el => io.observe(el))
    return () => io.disconnect()
  }, [])

  return (
    <>
      <div className="wm" aria-hidden="true">
        <span>練</span>
        <span>習</span>
        <span>語</span>
      </div>

      <div className="wrap">
        <header>
          <nav className="nav" aria-label="Site navigation">
            <a href="#/" className="nav-brand"><span className="jp">日本語</span>Practice</a>
            <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
              <Link to="/vocabulary-builder" className="gh-btn">Vocabulary Builder</Link>
              <a href="https://github.com/featurequest/practice-japanese" className="gh-btn" target="_blank" rel="noopener noreferrer" aria-label="GitHub repository (opens in new tab)">
                <svg viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>
                GitHub
              </a>
            </div>
          </nav>
        </header>
        <main>

        <section className="hero">
          <p className="eyebrow">Open source · Free to download</p>
          <h1>Japanese<br />Practice</h1>
          <p className="hero-sub">日本語の練習</p>
          <p className="hero-desc">
            Printable flash cards, handwriting practice sheets, stroke order guides, JLPT vocabulary PDFs and Anki decks for hiragana, katakana and N5–N1 vocabulary — generated from open-licensed sources and free to use.
          </p>
          <div className="stats">
            <div className="stat"><div className="stat-n">214</div><div className="stat-l">Kana cards</div></div>
            <div className="stat"><div className="stat-n">7,500+</div><div className="stat-l">JLPT words</div></div>
            <div className="stat"><div className="stat-n">N5–N1</div><div className="stat-l">All levels</div></div>
            <div className="stat"><div className="stat-n">PDF+apkg</div><div className="stat-l">Formats</div></div>
          </div>
        </section>

        <div className="preview" aria-hidden="true">
          <div className="pv-wrap">
            <div className="pv-img">
              <img src="https://raw.githubusercontent.com/featurequest/practice-japanese/main/docs/example_flashcards_front.jpg" alt="Hiragana flash card front side" loading="eager" />
            </div>
            <p className="pv-cap">Flash cards</p>
          </div>
          <div className="pv-wrap">
            <div className="pv-img">
              <img src="https://raw.githubusercontent.com/featurequest/practice-japanese/main/docs/example_vocabulary.jpg" alt="JLPT N5 vocabulary reference sheet" loading="lazy" />
            </div>
            <p className="pv-cap">Vocabulary PDF</p>
          </div>
          <div className="pv-wrap">
            <div className="pv-img">
              <img src="https://raw.githubusercontent.com/featurequest/practice-japanese/main/docs/example_stroke_order.jpg" alt="Kana stroke order diagram guide" loading="lazy" />
            </div>
            <p className="pv-cap">Stroke order</p>
          </div>
        </div>

        <section className="section reveal vb-feature-section" aria-label="Vocabulary Builder tool">
          <div className="vb-feature-inner">
            <div className="vb-feature-content">
              <p className="eyebrow">Online Tool · Free</p>
              <h2 className="vb-feature-title">Custom Vocabulary PDFs</h2>
              <p className="vb-feature-desc">
                Search 7,500+ JLPT words across all levels. Filter by N5–N1, search by meaning or reading, pick exactly the words you need, and download a custom-generated PDF — instantly in your browser.
              </p>
              <Link to="/vocabulary-builder" className="vb-cta">
                Open Vocabulary Builder
                <svg viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M2 7h10M8 3l4 4-4 4"/></svg>
              </Link>
            </div>
            <div className="vb-feature-glyph" aria-hidden="true">選</div>
          </div>
        </section>

        <section className="section reveal" id="kana" aria-labelledby="kana-heading">
          <div className="sec-head">
            <div className="sec-glyph" aria-hidden="true">あ</div>
            <div>
              <h2 id="kana-heading" className="sec-title">Kana Flash Cards &amp; Practice</h2>
              <p className="sec-desc">208 double-sided cards — 104 hiragana + 104 katakana. Print duplex on A4 and cut. Character on the front, romaji and stroke order on the back.</p>
            </div>
          </div>
          <div className="dl-group">
            <p className="dl-label">Flash Cards — choose your size</p>
            <div className="dl-grid dl-3">
              {[['55 × 82 mm','Standard playing card','flashcards-55x82.pdf'],['63 × 88 mm','Euro / sleeve size','flashcards-63x88.pdf'],['74 × 105 mm','A7 / pocket size','flashcards-74x105.pdf']].map(([name, hint, file]) => (
                <a key={file} className="dli" href={`https://github.com/featurequest/practice-japanese/releases/latest/download/${file}`} download>
                  <div className="dli-text"><div className="dli-name">{name}</div><div className="dli-hint">{hint}</div></div>
                  <span className="dli-badge">PDF</span>
                  <span className="dli-arr" aria-hidden="true"><svg viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M7 2v8M4 7l3 3 3-3M2 12h10"/></svg></span>
                </a>
              ))}
            </div>
          </div>
          <div className="dl-group">
            <p className="dl-label">Practice Sheets — 2 cm grid boxes with dashed guides</p>
            <div className="dl-grid dl-2">
              {[['Hiragana Practice','Landscape A4, all 104 characters','practice-hiragana.pdf'],['Katakana Practice','Landscape A4, all 104 characters','practice-katakana.pdf']].map(([name, hint, file]) => (
                <a key={file} className="dli" href={`https://github.com/featurequest/practice-japanese/releases/latest/download/${file}`} download>
                  <div className="dli-text"><div className="dli-name">{name}</div><div className="dli-hint">{hint}</div></div>
                  <span className="dli-badge">PDF</span>
                  <span className="dli-arr" aria-hidden="true"><svg viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M7 2v8M4 7l3 3 3-3M2 12h10"/></svg></span>
                </a>
              ))}
            </div>
          </div>
          <div className="dl-group">
            <p className="dl-label">Reference Charts — gojūon table layout</p>
            <div className="dl-grid dl-3">
              {[['Full Chart','Hiragana + katakana','chart.pdf'],['Hiragana Chart','Hiragana only','chart-hiragana.pdf'],['Katakana Chart','Katakana only','chart-katakana.pdf']].map(([name, hint, file]) => (
                <a key={file} className="dli" href={`https://github.com/featurequest/practice-japanese/releases/latest/download/${file}`} download>
                  <div className="dli-text"><div className="dli-name">{name}</div><div className="dli-hint">{hint}</div></div>
                  <span className="dli-badge">PDF</span>
                  <span className="dli-arr" aria-hidden="true"><svg viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M7 2v8M4 7l3 3 3-3M2 12h10"/></svg></span>
                </a>
              ))}
            </div>
          </div>
          <div className="dl-group">
            <p className="dl-label">Stroke Order Guides — KanjiVG diagrams with numbered strokes</p>
            <div className="dl-grid dl-3">
              {[['Full Stroke Order','All kana','stroke-order.pdf'],['Hiragana Strokes','Hiragana only','stroke-order-hiragana.pdf'],['Katakana Strokes','Katakana only','stroke-order-katakana.pdf']].map(([name, hint, file]) => (
                <a key={file} className="dli" href={`https://github.com/featurequest/practice-japanese/releases/latest/download/${file}`} download>
                  <div className="dli-text"><div className="dli-name">{name}</div><div className="dli-hint">{hint}</div></div>
                  <span className="dli-badge">PDF</span>
                  <span className="dli-arr" aria-hidden="true"><svg viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M7 2v8M4 7l3 3 3-3M2 12h10"/></svg></span>
                </a>
              ))}
            </div>
          </div>
        </section>

        <section className="section reveal" id="vocabulary" aria-labelledby="vocabulary-heading">
          <div className="sec-head">
            <div className="sec-glyph" aria-hidden="true">語</div>
            <div>
              <h2 id="vocabulary-heading" className="sec-title">JLPT Vocabulary PDFs</h2>
              <p className="sec-desc">Per-level reference sheets with meanings, part of speech, register tags and antonyms. Sourced from JMdict and Jonathan Waller's JLPT lists. English and Swedish.</p>
            </div>
          </div>
          <div className="vocab-grid">
            {['N5','N4','N3','N2','N1'].map(level => (
              <div key={level} className="vc">
                <div className="vc-top"><div className="vc-level">{level}</div></div>
                <div className="vc-body">
                  <a className="vc-link" href={`https://github.com/featurequest/practice-japanese/releases/latest/download/vocabulary_${level.toLowerCase()}.pdf`} download aria-label={`Download ${level} vocabulary PDF in English`}><span className="flag">🇬🇧</span> English</a>
                  <a className="vc-link" href={`https://github.com/featurequest/practice-japanese/releases/latest/download/vocabulary_sv_${level.toLowerCase()}.pdf`} download aria-label={`Download ${level} vocabulary PDF in Swedish`}><span className="flag">🇸🇪</span> Swedish</a>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="section reveal" id="anki" aria-labelledby="anki-heading">
          <div className="sec-head">
            <div className="sec-glyph" aria-hidden="true">習</div>
            <div>
              <h2 id="anki-heading" className="sec-title">Anki Decks</h2>
              <p className="sec-desc">Bidirectional cards — Japanese → English and English → Japanese. One deck per JLPT level, or download everything in a single bundle. Import directly into Anki.</p>
            </div>
          </div>
          <div className="anki-row">
            {['N5','N4','N3','N2','N1'].map(level => (
              <a key={level} className="ak" href={`https://github.com/featurequest/practice-japanese/releases/latest/download/anki_${level.toLowerCase()}.apkg`} download>
                <div className="ak-top"><div className="ak-lvl">{level}</div></div>
                <div className="ak-body"><div className="ak-sub">Vocabulary</div><div className="ak-format">.apkg</div></div>
              </a>
            ))}
          </div>
          <a className="ak-all" href="https://github.com/featurequest/practice-japanese/releases/latest/download/anki_all.apkg" download>
            <div>
              <div className="ak-all-title">All Levels Bundle</div>
              <div className="ak-all-sub">N5–N1 in a single file — import once, get everything</div>
            </div>
            <span className="ak-all-badge">anki_all.apkg</span>
          </a>
        </section>

        </main>
        <footer>
          <div className="footer-grid">
            <div>
              <p className="ft-title">About</p>
              <p className="ft-p">All materials are generated from open-licensed sources. PDFs and Anki decks are rebuilt automatically on every release. The source code is MIT-licensed and available on GitHub.</p>
            </div>
            <div>
              <p className="ft-title">Data Sources</p>
              <ul className="ft-ul">
                <li><a href="https://www.edrdg.org/" target="_blank" rel="noopener">JMdict</a> — CC BY-SA 3.0</li>
                <li><a href="https://www.tanos.co.uk/jlpt/" target="_blank" rel="noopener">Jonathan Waller JLPT lists</a></li>
                <li><a href="https://kanjivg.tagaini.net/" target="_blank" rel="noopener">KanjiVG</a> — CC BY-SA 3.0</li>
                <li><a href="https://github.com/fontworks-fonts/Klee" target="_blank" rel="noopener">Klee One font</a> — SIL OFL 1.1</li>
              </ul>
            </div>
            <div>
              <p className="ft-title">Project</p>
              <ul className="ft-ul">
                <li><a href="https://github.com/featurequest/practice-japanese" target="_blank" rel="noopener">Source code</a></li>
                <li><a href="https://github.com/featurequest/practice-japanese/releases" target="_blank" rel="noopener">All releases</a></li>
                <li><a href="https://github.com/featurequest/practice-japanese/issues" target="_blank" rel="noopener">Report an issue</a></li>
              </ul>
            </div>
          </div>
          <div className="footer-bottom">
            <p className="ft-disclaimer">For educational use only. Content is sourced from community-maintained dictionaries and may contain errors. Verify with authoritative references when accuracy matters.</p>
            <p className="ft-copy">Code &copy; 2025 featurequest — <a href="https://github.com/featurequest/practice-japanese/blob/main/LICENSE" target="_blank" rel="noopener">MIT License</a>. Vocabulary data CC BY-SA 3.0.</p>
            <p className="ft-copy">Generated from <a href="https://github.com/featurequest/practice-japanese" target="_blank" rel="noopener">featurequest/practice-japanese</a></p>
          </div>
        </footer>
      </div>
    </>
  )
}
