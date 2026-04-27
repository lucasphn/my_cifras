// Variations of section tag treatments.
// Each component renders the full song (header + chord/lyric block) with
// one treatment. Chord/lyric rendering is unified in <CifraBlock> so only
// the <Tag /> differs between variations.

const { useState } = React;

// ── Shared chord/lyric line renderer ────────────────────────────────────
function Line({ chords, lyric, fontSize = 13 }) {
  return (
    <div style={{ fontFamily: '"JetBrains Mono", "SF Mono", Menlo, Consolas, monospace', fontSize, lineHeight: 1.35, whiteSpace: 'pre' }}>
      {chords && <div style={{ color: '#6D51C6', fontWeight: 600, minHeight: fontSize * 1.35 }}>{chords}</div>}
      {lyric && <div style={{ color: '#1f1b2e' }}>{lyric}</div>}
    </div>
  );
}

function ChordHeader({ keyVal = 'C', variant = 'light', compact }) {
  const keys = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B'];
  const bg = variant === 'dark' ? '#1a1624' : '#f6f3fb';
  const border = variant === 'dark' ? '#2a2438' : '#ece6f6';
  const text = variant === 'dark' ? '#b8b0d0' : '#6b6384';
  const activeBg = '#D4A017';
  const activeText = '#1f1b2e';
  return (
    <div style={{ background: bg, borderBottom: `1px solid ${border}`, padding: compact ? '8px 16px' : '10px 20px', fontSize: 12, color: text, display: 'flex', alignItems: 'center', gap: 14, fontFamily: 'Inter, system-ui, sans-serif' }}>
      <span style={{ fontWeight: 500 }}>Tom:</span>
      <button style={{ width: 22, height: 22, border: `1px solid ${border}`, background: 'transparent', color: text, borderRadius: 6, cursor: 'pointer' }}>−</button>
      <span style={{ fontVariantNumeric: 'tabular-nums', color: variant === 'dark' ? '#d4c9ec' : '#4a4264', fontWeight: 600 }}>+0</span>
      <button style={{ width: 22, height: 22, border: `1px solid ${border}`, background: 'transparent', color: text, borderRadius: 6, cursor: 'pointer' }}>+</button>
      <span style={{ marginLeft: 8, fontWeight: 500 }}>Destino:</span>
      <div style={{ display: 'flex', gap: 2 }}>
        {keys.map(k => (
          <span key={k} style={{ padding: '3px 7px', fontSize: 11, borderRadius: 5, background: k === keyVal ? activeBg : 'transparent', color: k === keyVal ? activeText : text, fontWeight: k === keyVal ? 700 : 500, cursor: 'pointer' }}>{k}</span>
        ))}
      </div>
    </div>
  );
}

function SongTitle({ variant = 'light' }) {
  const textMain = variant === 'dark' ? '#f4f1fa' : '#1f1b2e';
  const textSub = variant === 'dark' ? '#9b92b5' : '#6b6384';
  const bg = variant === 'dark' ? '#120f1a' : '#fff';
  const border = variant === 'dark' ? '#2a2438' : '#ece6f6';
  return (
    <div style={{ background: bg, borderBottom: `1px solid ${border}`, padding: '14px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontFamily: 'Inter, system-ui, sans-serif' }}>
      <div>
        <div style={{ fontSize: 17, fontWeight: 700, color: textMain, letterSpacing: -0.2 }}>Terra Seca</div>
        <div style={{ fontSize: 12, color: textSub, marginTop: 1 }}>Fraternidade São João Paulo II</div>
      </div>
      <div style={{ display: 'flex', gap: 5 }}>
        {['A−','A+','⏸','■','×'].map((s, i) => (
          <span key={i} style={{ width: 28, height: 24, display: 'inline-flex', alignItems: 'center', justifyContent: 'center', border: `1px solid ${border}`, borderRadius: 6, fontSize: 11, color: textSub }}>{s}</span>
        ))}
      </div>
    </div>
  );
}

// ── Base frame used by every variation ────────────────────────────────
function Frame({ children, variant = 'light', chordKey = 'C' }) {
  const bg = variant === 'dark' ? '#0e0b16' : '#ffffff';
  return (
    <div style={{ background: bg, height: '100%', display: 'flex', flexDirection: 'column', fontFamily: 'Inter, system-ui, sans-serif' }}>
      <SongTitle variant={variant} />
      <ChordHeader keyVal={chordKey} variant={variant} compact />
      <div style={{ flex: 1, overflow: 'auto', padding: '18px 24px' }}>
        {children}
      </div>
    </div>
  );
}

// Render song sections using a supplied <Tag> component.
function SongBody({ Tag, variant = 'light', sectionGap = 18, lineGap = 10 }) {
  return (
    <div>
      {SONG.map((section, i) => (
        <div key={i} style={{ marginBottom: sectionGap }}>
          <Tag type={section.type} label={section.label} num={section.num} variant={variant} />
          <div style={{ marginTop: lineGap }}>
            {section.lines.map((ln, j) => (
              <div key={j} style={{ marginBottom: 2 }}>
                <Line chords={ln.chords} lyric={ln.lyric} />
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════
// VARIATION 1 — Texto puro minimalista
// Small-caps label + thin rule. Zero visual noise.
// ═══════════════════════════════════════════════════════════════════════
function V1_Minimal() {
  const Tag = ({ label, variant }) => {
    const c = variant === 'dark' ? '#8a82a8' : '#8b82a6';
    const rule = variant === 'dark' ? '#26213a' : '#eae4f2';
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6, marginTop: 4 }}>
        <span style={{ fontSize: 10.5, fontWeight: 700, letterSpacing: 1.4, textTransform: 'uppercase', color: c, fontFamily: 'Inter, system-ui, sans-serif' }}>
          {label}
        </span>
        <div style={{ flex: 1, height: 1, background: rule }} />
      </div>
    );
  };
  return <Frame><SongBody Tag={Tag} sectionGap={14} /></Frame>;
}

// ═══════════════════════════════════════════════════════════════════════
// VARIATION 2 — Margem lateral com acento vertical
// Label sits in the left gutter, accent bar distinguishes chorus.
// ═══════════════════════════════════════════════════════════════════════
function V2_Gutter() {
  const Tag = ({ label, type }) => {
    const isChorus = type === 'chorus';
    const accent = isChorus ? '#6D51C6' : '#d4cce4';
    return (
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, marginBottom: 6 }}>
        <div style={{ width: 3, alignSelf: 'stretch', minHeight: 14, background: accent, borderRadius: 2, marginTop: 4 }} />
        <span style={{ fontSize: 10.5, fontWeight: 600, letterSpacing: 1.2, textTransform: 'uppercase', color: isChorus ? '#6D51C6' : '#8b82a6', fontFamily: 'Inter, system-ui, sans-serif' }}>
          {label}
        </span>
      </div>
    );
  };
  return <Frame><SongBody Tag={Tag} sectionGap={14} /></Frame>;
}

// ═══════════════════════════════════════════════════════════════════════
// VARIATION 3 — Colchetes tipográficos (homenagem ao chord-pro)
// Plain bracketed label in purple. Zero chrome.
// ═══════════════════════════════════════════════════════════════════════
function V3_Bracket() {
  const Tag = ({ label, type }) => {
    const isChorus = type === 'chorus';
    return (
      <div style={{ marginBottom: 5, marginTop: 2 }}>
        <span style={{
          fontSize: 11.5,
          fontFamily: '"JetBrains Mono", "SF Mono", Menlo, monospace',
          fontWeight: isChorus ? 700 : 600,
          color: isChorus ? '#6D51C6' : '#9a92b5',
          letterSpacing: 0.2,
        }}>
          [{label}]
        </span>
      </div>
    );
  };
  return <Frame><SongBody Tag={Tag} sectionGap={14} /></Frame>;
}

// ═══════════════════════════════════════════════════════════════════════
// VARIATION 4 — Pílula ghost monocromática
// One-color pill, outlined. Chorus gets filled treatment.
// ═══════════════════════════════════════════════════════════════════════
function V4_GhostPill() {
  const Tag = ({ label, type }) => {
    const isChorus = type === 'chorus';
    const style = isChorus ? {
      background: '#6D51C6',
      color: '#fff',
      border: '1px solid #6D51C6',
    } : {
      background: 'transparent',
      color: '#6D51C6',
      border: '1px solid #d4cce4',
    };
    return (
      <div style={{ marginBottom: 6 }}>
        <span style={{
          ...style,
          display: 'inline-block',
          fontSize: 10,
          fontWeight: 700,
          letterSpacing: 1.1,
          textTransform: 'uppercase',
          padding: '3px 8px',
          borderRadius: 4,
          fontFamily: 'Inter, system-ui, sans-serif',
        }}>{label}</span>
      </div>
    );
  };
  return <Frame><SongBody Tag={Tag} sectionGap={14} /></Frame>;
}

// ═══════════════════════════════════════════════════════════════════════
// VARIATION 5 — Numerado (livro de cifra)
// Small numeric index + label. Refrão uses letter R.
// ═══════════════════════════════════════════════════════════════════════
function V5_Numbered() {
  let partCounter = 0;
  const iconFor = (type, num) => {
    if (type === 'intro') return '◦';
    if (type === 'chorus') return 'R';
    if (type === 'prechorus') return '•';
    if (type === 'bridge') return '✦';
    if (type === 'part') return String(num || ++partCounter);
    return '·';
  };
  const Tag = ({ label, type, num }) => {
    const mark = iconFor(type, num);
    const isChorus = type === 'chorus';
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
        <span style={{
          width: 18, height: 18, borderRadius: 9,
          display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 10, fontWeight: 700,
          background: isChorus ? '#6D51C6' : '#f0ebf9',
          color: isChorus ? '#fff' : '#6D51C6',
          fontFamily: 'Inter, system-ui, sans-serif',
        }}>{mark}</span>
        <span style={{ fontSize: 11, fontWeight: 600, color: isChorus ? '#6D51C6' : '#6b6384', letterSpacing: 0.3, textTransform: 'uppercase' }}>
          {label}
        </span>
      </div>
    );
  };
  return <Frame><SongBody Tag={Tag} sectionGap={14} /></Frame>;
}

// ═══════════════════════════════════════════════════════════════════════
// VARIATION 6 — Cabeçalho lateral fixo (marginalia)
// Section label lives in a narrow left column next to the content.
// ═══════════════════════════════════════════════════════════════════════
function V6_Marginalia() {
  return (
    <Frame>
      <div>
        {SONG.map((section, i) => {
          const isChorus = section.type === 'chorus';
          return (
            <div key={i} style={{ display: 'grid', gridTemplateColumns: '72px 1fr', gap: 12, marginBottom: 18, alignItems: 'start' }}>
              <div style={{ paddingTop: 2, textAlign: 'right' }}>
                <div style={{
                  fontSize: 9.5,
                  fontWeight: 700,
                  letterSpacing: 1.2,
                  textTransform: 'uppercase',
                  color: isChorus ? '#6D51C6' : '#a69bc0',
                  fontFamily: 'Inter, system-ui, sans-serif',
                  lineHeight: 1.3,
                }}>{section.label}</div>
              </div>
              <div style={{ borderLeft: isChorus ? '2px solid #6D51C6' : '1px solid #ece6f6', paddingLeft: 14 }}>
                {section.lines.map((ln, j) => (
                  <Line key={j} chords={ln.chords} lyric={ln.lyric} />
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </Frame>
  );
}

// ═══════════════════════════════════════════════════════════════════════
// VARIATION 7 — Sistema hierárquico (só o Refrão destaca)
// Refrão = pílula sólida; demais = caps pequeno quase invisível.
// ═══════════════════════════════════════════════════════════════════════
function V7_HierarchicalChorus() {
  const Tag = ({ label, type }) => {
    if (type === 'chorus') {
      return (
        <div style={{ marginBottom: 7, marginTop: 2 }}>
          <span style={{
            background: '#6D51C6',
            color: '#fff',
            fontSize: 10,
            fontWeight: 700,
            letterSpacing: 1.3,
            textTransform: 'uppercase',
            padding: '4px 10px',
            borderRadius: 3,
            fontFamily: 'Inter, system-ui, sans-serif',
          }}>{label}</span>
        </div>
      );
    }
    return (
      <div style={{ marginBottom: 5, marginTop: 2 }}>
        <span style={{
          fontSize: 10,
          fontWeight: 600,
          letterSpacing: 1.5,
          textTransform: 'uppercase',
          color: '#a69bc0',
          fontFamily: 'Inter, system-ui, sans-serif',
        }}>{label}</span>
      </div>
    );
  };
  return <Frame><SongBody Tag={Tag} sectionGap={13} /></Frame>;
}

// ═══════════════════════════════════════════════════════════════════════
// VARIATION 8 — Dark mode polido (baseado na favorita: V1)
// Proves the minimalist treatment works beautifully on dark too.
// ═══════════════════════════════════════════════════════════════════════
function V8_Dark() {
  const Tag = ({ label, type }) => {
    const isChorus = type === 'chorus';
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6, marginTop: 4 }}>
        <span style={{
          fontSize: 10.5,
          fontWeight: 700,
          letterSpacing: 1.4,
          textTransform: 'uppercase',
          color: isChorus ? '#b49dff' : '#6d6585',
          fontFamily: 'Inter, system-ui, sans-serif',
        }}>
          {label}
        </span>
        <div style={{ flex: 1, height: 1, background: isChorus ? '#3d3160' : '#1e1a2c' }} />
      </div>
    );
  };
  return (
    <div style={{ background: '#0e0b16', height: '100%', display: 'flex', flexDirection: 'column', fontFamily: 'Inter, system-ui, sans-serif' }}>
      <SongTitle variant="dark" />
      <ChordHeader variant="dark" compact />
      <div style={{ flex: 1, overflow: 'auto', padding: '18px 24px' }}>
        <div>
          {SONG.map((section, i) => (
            <div key={i} style={{ marginBottom: 14 }}>
              <Tag type={section.type} label={section.label} />
              <div style={{ marginTop: 8 }}>
                {section.lines.map((ln, j) => (
                  <div key={j} style={{ fontFamily: '"JetBrains Mono", "SF Mono", Menlo, monospace', fontSize: 13, lineHeight: 1.35, whiteSpace: 'pre' }}>
                    {ln.chords && <div style={{ color: '#b49dff', fontWeight: 600 }}>{ln.chords}</div>}
                    {ln.lyric && <div style={{ color: '#e8e2f5' }}>{ln.lyric}</div>}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════
// ORIGINAL — reference for comparison (rebuilt from screenshot)
// ═══════════════════════════════════════════════════════════════════════
function V0_Original() {
  const palette = {
    intro: { bg: 'transparent', color: '#4a4264' },
    part: { bg: '#f5e9b8', color: '#7a5a00', border: '#d4a017' },
    prechorus: { bg: '#e8dbff', color: '#5b2fc7', border: '#b89cf0' },
    chorus: { bg: '#6D51C6', color: '#fff', border: '#6D51C6' },
    bridge: { bg: '#d4f0e8', color: '#1a7a5e', border: '#7dc8b3' },
  };
  const Tag = ({ label, type }) => {
    if (type === 'intro') {
      return (
        <div style={{ marginBottom: 6, marginTop: 2 }}>
          <span style={{ fontFamily: '"JetBrains Mono", monospace', fontSize: 13, color: '#1f1b2e', fontWeight: 600 }}>
            [{label}]
          </span>
        </div>
      );
    }
    const p = palette[type] || palette.part;
    return (
      <div style={{ marginBottom: 7, marginTop: 4 }}>
        <span style={{
          display: 'inline-block',
          background: p.bg,
          color: p.color,
          border: `1px solid ${p.border}`,
          fontFamily: '"JetBrains Mono", monospace',
          fontSize: 11,
          fontWeight: 700,
          letterSpacing: 0.5,
          textTransform: 'uppercase',
          padding: '3px 9px',
          borderRadius: 5,
        }}>[{label}]</span>
      </div>
    );
  };
  return <Frame><SongBody Tag={Tag} sectionGap={15} /></Frame>;
}

Object.assign(window, {
  V0_Original, V1_Minimal, V2_Gutter, V3_Bracket, V4_GhostPill,
  V5_Numbered, V6_Marginalia, V7_HierarchicalChorus, V8_Dark,
});
