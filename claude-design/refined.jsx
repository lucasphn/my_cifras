// Refined monochromatic variations based on user feedback:
// - Loved V2 (gutter bar) but wants it fully monochromatic
// - Accent color: #b1abc3
// - Using real brand tokens from DESIGN.md (Fira Mono, --primary #5b4b8a, etc)

const MONO = '#b1abc3';

// ── Shared with real brand typography ─────────────────────────────────
function RLine({ chords, lyric, variant = 'light' }) {
  const chordColor = variant === 'dark' ? '#b49dff' : '#5b4b8a'; // --primary
  const lyricColor = variant === 'dark' ? '#e8e2f5' : '#1f2937'; // --text
  return (
    <div style={{ fontFamily: '"Fira Mono", Consolas, "Courier New", monospace', fontSize: 13, lineHeight: 1.65, whiteSpace: 'pre' }}>
      {chords && <div style={{ color: chordColor, fontWeight: 800, minHeight: 13 * 1.65 }}>{chords}</div>}
      {lyric && <div style={{ color: lyricColor, fontWeight: 600 }}>{lyric}</div>}
    </div>
  );
}

function RSongTitle() {
  return (
    <div style={{ background: '#fff', borderBottom: '1px solid #e6e1f0', padding: '14px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontFamily: 'Inter, system-ui, sans-serif' }}>
      <div>
        <div style={{ fontSize: 17, fontWeight: 700, color: '#1f2937', letterSpacing: -0.2 }}>Terra Seca</div>
        <div style={{ fontSize: 12, color: '#6b7280', marginTop: 1 }}>Fraternidade São João Paulo II</div>
      </div>
      <div style={{ display: 'flex', gap: 5 }}>
        {['A−','A+','⏸','■','×'].map((s, i) => (
          <span key={i} style={{ width: 28, height: 24, display: 'inline-flex', alignItems: 'center', justifyContent: 'center', border: '1px solid #e6e1f0', borderRadius: 99, fontSize: 11, color: '#6b7280' }}>{s}</span>
        ))}
      </div>
    </div>
  );
}

function RChordHeader() {
  const keys = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B'];
  return (
    <div style={{ background: '#f7f6fb', borderBottom: '1px solid #e6e1f0', padding: '8px 16px', fontSize: 12, color: '#6b7280', display: 'flex', alignItems: 'center', gap: 14, fontFamily: 'Inter, system-ui, sans-serif' }}>
      <span style={{ fontWeight: 500 }}>Tom:</span>
      <button style={{ width: 22, height: 22, border: '1px solid #e6e1f0', background: 'transparent', color: '#6b7280', borderRadius: 99, cursor: 'pointer' }}>−</button>
      <span style={{ fontVariantNumeric: 'tabular-nums', color: '#5b4b8a', fontWeight: 700 }}>+0</span>
      <button style={{ width: 22, height: 22, border: '1px solid #e6e1f0', background: 'transparent', color: '#6b7280', borderRadius: 99, cursor: 'pointer' }}>+</button>
      <span style={{ marginLeft: 8, fontWeight: 500 }}>Destino:</span>
      <div style={{ display: 'flex', gap: 2 }}>
        {keys.map(k => (
          <span key={k} style={{ padding: '3px 7px', fontSize: 11, borderRadius: 99, background: k === 'C' ? 'rgba(212,175,55,.12)' : 'transparent', color: k === 'C' ? '#d4af37' : '#6b7280', fontWeight: k === 'C' ? 700 : 500, border: k === 'C' ? '1px solid rgba(212,175,55,.28)' : '1px solid transparent', cursor: 'pointer' }}>{k}</span>
        ))}
      </div>
    </div>
  );
}

function RFrame({ children }) {
  return (
    <div style={{ background: '#ffffff', height: '100%', display: 'flex', flexDirection: 'column', fontFamily: 'Inter, system-ui, sans-serif' }}>
      <RSongTitle />
      <RChordHeader />
      <div style={{ flex: 1, overflow: 'auto', padding: '18px 24px' }}>
        {children}
      </div>
    </div>
  );
}

function RBody({ Tag, sectionGap = 16 }) {
  return (
    <div>
      {SONG.map((section, i) => (
        <div key={i} style={{ marginBottom: sectionGap }}>
          <Tag type={section.type} label={section.label} num={section.num} />
          <div style={{ marginTop: 6 }}>
            {section.lines.map((ln, j) => (
              <RLine key={j} chords={ln.chords} lyric={ln.lyric} />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════
// R1 — Barra lateral monocromática (V2 refinada)
// Same structure as V2 but everything is #b1abc3, no chorus accent.
// ═══════════════════════════════════════════════════════════════════════
function R1_GutterMono() {
  const Tag = ({ label }) => (
    <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, marginBottom: 4 }}>
      <div style={{ width: 3, alignSelf: 'stretch', minHeight: 14, background: MONO, borderRadius: 2, marginTop: 4 }} />
      <span style={{ fontSize: 10.5, fontWeight: 700, letterSpacing: 0.13 * 10.5, textTransform: 'uppercase', color: MONO, fontFamily: 'Inter, system-ui, sans-serif' }}>
        {label}
      </span>
    </div>
  );
  return <RFrame><RBody Tag={Tag} /></RFrame>;
}

// ═══════════════════════════════════════════════════════════════════════
// R2 — Barra lateral mono + peso no refrão por tipografia (sem cor)
// Chorus gets slightly heavier text, not a color change. Still mono.
// ═══════════════════════════════════════════════════════════════════════
function R2_GutterMonoWeight({ fontSize = 9 }) {
  const Tag = ({ label, type }) => {
    const isChorus = type === 'chorus';
    return (
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, marginBottom: 3 }}>
        <div style={{ width: isChorus ? 3 : 2, alignSelf: 'stretch', minHeight: 12, background: MONO, borderRadius: 2, marginTop: 3, opacity: isChorus ? 1 : 0.7 }} />
        <span style={{ fontSize, fontWeight: isChorus ? 800 : 700, letterSpacing: 0.13 * fontSize, textTransform: 'uppercase', color: MONO, fontFamily: 'Inter, system-ui, sans-serif' }}>
          {label}
        </span>
      </div>
    );
  };
  return <RFrame><RBody Tag={Tag} /></RFrame>;
}

function R2_GutterMonoWeight_XS() { return <R2_GutterMonoWeight fontSize={8} />; }
function R2_GutterMonoWeight_S()  { return <R2_GutterMonoWeight fontSize={9} />; }
function R2_GutterMonoWeight_M()  { return <R2_GutterMonoWeight fontSize={10} />; }

// ═══════════════════════════════════════════════════════════════════════
// R3 — Barra mono + linha de extensão (fecha a tag com a cifra visualmente)
// Vertical bar + thin horizontal rule extending to the right.
// ═══════════════════════════════════════════════════════════════════════
function R3_GutterMonoRule() {
  const Tag = ({ label }) => (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
      <div style={{ width: 3, height: 14, background: MONO, borderRadius: 2 }} />
      <span style={{ fontSize: 10.5, fontWeight: 700, letterSpacing: 0.13 * 10.5, textTransform: 'uppercase', color: MONO, fontFamily: 'Inter, system-ui, sans-serif' }}>
        {label}
      </span>
      <div style={{ flex: 1, height: 1, background: MONO, opacity: 0.25 }} />
    </div>
  );
  return <RFrame><RBody Tag={Tag} /></RFrame>;
}

// ═══════════════════════════════════════════════════════════════════════
// R4 — Indent (conteúdo da seção fica recuado, barra percorre todo o bloco)
// Most distinctive: the gutter bar runs the full height of the section.
// ═══════════════════════════════════════════════════════════════════════
function R4_FullGutter() {
  return (
    <RFrame>
      <div>
        {SONG.map((section, i) => (
          <div key={i} style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
            <div style={{ width: 2, background: MONO, borderRadius: 2, flexShrink: 0, opacity: 0.6 }} />
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ marginBottom: 4 }}>
                <span style={{ fontSize: 10.5, fontWeight: 700, letterSpacing: 0.13 * 10.5, textTransform: 'uppercase', color: MONO, fontFamily: 'Inter, system-ui, sans-serif' }}>
                  {section.label}
                </span>
              </div>
              {section.lines.map((ln, j) => (
                <RLine key={j} chords={ln.chords} lyric={ln.lyric} />
              ))}
            </div>
          </div>
        ))}
      </div>
    </RFrame>
  );
}

Object.assign(window, { R1_GutterMono, R2_GutterMonoWeight, R3_GutterMonoRule, R4_FullGutter });
