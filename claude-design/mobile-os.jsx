// ──────────────────────────────────────────────────────────────
// Mobile OS — iOS + Android frames envolvendo H1 + D1 reais
// H1 = HomeScreenV2 + H1_SearchFirst
// D1 = RepScreen + RepD1_DraftTop
// Ajuste: os frames mostram APENAS a chrome do sistema operacional;
//          o conteúdo é o mesmo das versões aprovadas.
// ──────────────────────────────────────────────────────────────

// ═══════════════════════════════════════════════════════════════
// OS CHROME WRAPPERS — substitui Phone mock pelo bezel real do OS
// ═══════════════════════════════════════════════════════════════

// iOS: status bar 54px · home indicator 34px · tab bar embutida (deixamos H1 renderizar a própria)
function IOSShell({ children, width = 440, height = 930 }) {
  return (
    <IOSDevice width={width} height={height} dark={false}>
      {/* Renderizamos direto o conteúdo (H1/D1 já trazem sua tab bar de pill) */}
      <div style={{ width: '100%', height: '100%', background: BRAND.bg, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
        {children}
      </div>
    </IOSDevice>
  );
}

// Android: status bar + nav bar gesto · mantém mesmo padrão
function AndroidShell({ children, width = 450, height = 930 }) {
  return (
    <AndroidDevice width={width} height={height} dark={false} title={undefined}>
      <div style={{ width: '100%', height: '100%', background: BRAND.bg, overflow: 'hidden', display: 'flex', flexDirection: 'column', marginTop: -1 }}>
        {children}
      </div>
    </AndroidDevice>
  );
}

// ═══════════════════════════════════════════════════════════════
// Patch: a Phone do HomeScreenV2 inclui uma status bar fake e nav bar.
// Nos frames de OS, precisamos de uma versão SEM a Phone wrapper, só o miolo.
// Vamos extrair o mesmo conteúdo chamando o componente Variant direto,
// e deixando a tab bar do app renderizar acima do home indicator do iOS
// ou acima da gesture bar do Android.
// ═══════════════════════════════════════════════════════════════

function HomeContentOnly({ Variant, Nav }) {
  // H1/H2 etc rendem o mesmo layout interno — os espaçadores de topo
  // já respeitam a status bar quando estamos fora de Phone, adicionamos padding.
  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: BRAND.bg, position: 'relative', overflow: 'hidden' }}>
      <div style={{ flex: 1, overflow: 'auto' }}>
        <Variant />
      </div>
      <Nav />
    </div>
  );
}

function RepContentOnly({ Variant, Nav }) {
  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: BRAND.bg, position: 'relative', overflow: 'hidden' }}>
      <div style={{ flex: 1, overflow: 'auto' }}>
        <Variant />
      </div>
      <Nav />
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// CIFRA MOBILE — componente pra ser usado dentro de iOS/Android
// Mesmo visual de desktop, adaptado pro tamanho mobile
// ═══════════════════════════════════════════════════════════════
function CifraContentOnly({ os = 'ios', defaultTwoCol = false }) {
  const [twoCol, setTwoCol] = React.useState(defaultTwoCol);
  const radius = os === 'ios' ? 14 : 10;

  const L = ({ chord, lyric, tag, chorus }) => {
    if (tag) {
      return (
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, margin: '14px 0 6px', breakInside: 'avoid' }}>
          <div style={{ width: chorus ? 3 : 2, height: 11, background: '#9a95a8', opacity: chorus ? 1 : 0.7, borderRadius: 1 }} />
          <span style={{ fontFamily: '"Fira Mono", ui-monospace, monospace', fontSize: 8, fontWeight: chorus ? 800 : 600, letterSpacing: 1.8, textTransform: 'uppercase', color: '#7a7289' }}>{tag}</span>
        </div>
      );
    }
    const fs = twoCol ? 11.5 : 13.5;
    return (
      <div style={{ marginBottom: 2, fontFamily: '"Fira Mono", ui-monospace, monospace', breakInside: 'avoid' }}>
        {chord && <div style={{ color: BRAND.primary, fontSize: fs, fontWeight: 900, lineHeight: 1.4, whiteSpace: 'pre' }}>{chord}</div>}
        {lyric && <div style={{ color: '#0f1419', fontSize: fs, fontWeight: 700, lineHeight: 1.4, whiteSpace: 'pre' }}>{lyric}</div>}
      </div>
    );
  };

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: '#fff', overflow: 'hidden' }}>
      {/* Title block */}
      <div style={{ padding: '10px 14px 8px', borderBottom: '1px solid #ebe8f0' }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: 9.5, fontWeight: 800, letterSpacing: 1.2, textTransform: 'uppercase', color: BRAND.muted }}>Fé e Conversão</div>
            <div style={{ fontSize: 17, fontWeight: 800, color: BRAND.text, letterSpacing: -0.3, lineHeight: 1.15, marginTop: 1 }}>Determinada Decisão</div>
            <div style={{ fontSize: 11, color: BRAND.muted, marginTop: 2 }}>Juninho Casimiro · 44 views</div>
          </div>
          <button title="Opções" style={{ width: 34, height: 34, borderRadius: 99, background: '#fef7e6', border: `1px solid ${BRAND.accentBorder}`, color: BRAND.accent, fontSize: 15, fontWeight: 900, cursor: 'pointer', flexShrink: 0 }}>⋯</button>
        </div>

        {/* Toolbar: transpose + tools */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 5, marginTop: 8, overflowX: 'auto' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 0, background: '#faf9fc', border: `1px solid ${BRAND.border}`, borderRadius: radius, padding: 2, flexShrink: 0 }}>
            <button style={{ width: 30, height: 30, border: 'none', background: 'transparent', fontSize: 16, fontWeight: 800, color: BRAND.text, cursor: 'pointer' }}>−</button>
            <span style={{ fontSize: 13, fontWeight: 800, color: BRAND.primary, padding: '0 6px', minWidth: 28, textAlign: 'center' }}>A#</span>
            <button style={{ width: 30, height: 30, border: 'none', background: 'transparent', fontSize: 16, fontWeight: 800, color: BRAND.text, cursor: 'pointer' }}>+</button>
          </div>
          <button style={{ flexShrink: 0, height: 34, padding: '0 9px', borderRadius: radius, background: '#faf9fc', border: `1px solid ${BRAND.border}`, color: BRAND.text, fontSize: 11, fontWeight: 700, cursor: 'pointer' }}>A−</button>
          <button style={{ flexShrink: 0, height: 34, padding: '0 9px', borderRadius: radius, background: '#faf9fc', border: `1px solid ${BRAND.border}`, color: BRAND.text, fontSize: 12.5, fontWeight: 700, cursor: 'pointer' }}>A+</button>
          <button onClick={() => setTwoCol(!twoCol)} style={{ flexShrink: 0, height: 34, padding: '0 10px', borderRadius: radius, background: twoCol ? BRAND.primary : '#faf9fc', border: twoCol ? 'none' : `1px solid ${BRAND.border}`, color: twoCol ? '#fff' : BRAND.text, fontSize: 10.5, fontWeight: 700, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4 }}>
            <svg width="12" height="10" viewBox="0 0 14 11" fill="currentColor"><rect x="0" y="0" width="6" height="11" rx="1.5"/><rect x="8" y="0" width="6" height="11" rx="1.5"/></svg>
            2 col
          </button>
          <button style={{ flexShrink: 0, height: 34, padding: '0 9px', borderRadius: radius, background: '#faf9fc', border: `1px solid ${BRAND.border}`, color: BRAND.text, fontSize: 10.5, fontWeight: 700, cursor: 'pointer' }}>⇅ Auto</button>
          <div style={{ flex: 1, minWidth: 4 }} />
          <button title="Apresentar" style={{ flexShrink: 0, width: 34, height: 34, borderRadius: radius, background: BRAND.primary, border: 'none', color: '#fff', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <svg width="11" height="13" viewBox="0 0 10 12" fill="currentColor"><path d="M0 0 L10 6 L0 12 Z"/></svg>
          </button>
        </div>

        {/* Owner row */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginTop: 7, padding: '5px 6px', background: '#fff9ec', border: `1px solid ${BRAND.accentBorder}`, borderRadius: radius - 2 }}>
          <span style={{ fontSize: 8.5, fontWeight: 800, letterSpacing: 1, textTransform: 'uppercase', color: BRAND.accent, padding: '2px 6px', background: '#fff', borderRadius: 99, border: `1px solid ${BRAND.accentBorder}` }}>owner</span>
          <button style={{ flex: 1, padding: '5px 4px', background: 'transparent', border: 'none', fontSize: 10.5, fontWeight: 700, color: BRAND.text, cursor: 'pointer' }}>ⓘ Metadados</button>
          <button style={{ flex: 1, padding: '5px 4px', background: 'transparent', border: 'none', fontSize: 10.5, fontWeight: 700, color: BRAND.text, cursor: 'pointer' }}>✎ Editar</button>
          <button style={{ flex: 1, padding: '5px 4px', background: 'transparent', border: 'none', fontSize: 10.5, fontWeight: 700, color: BRAND.text, cursor: 'pointer' }}>♪ Salvar tom</button>
        </div>
      </div>

      {/* Body (cifra) */}
      <div style={{ flex: 1, overflow: 'auto', padding: '10px 14px 80px', columnCount: twoCol ? 2 : 1, columnGap: 14 }}>
        <L tag="Intro" /><L chord="A#   D#   Fm" lyric="" />
        <L tag="1ª Parte" />
        <L chord="A#            D#" lyric="Tomei a decisão de te servir" />
        <L chord="Fm          A#" lyric="De entregar o que sou" />
        <L chord="D#         Cm" lyric="A Ti meu coração eu rendo" />
        <L tag="Refrão" chorus />
        <L chord="A#     D#" lyric="Determinada decisão" />
        <L chord="Fm        A#" lyric="É viver em Tua presença" />
        <L chord="D#      Cm" lyric="Seguir Teus passos, Senhor" />
        <L chord="Fm     A#" lyric="Com toda minha força" />
        <L tag="2ª Parte" />
        <L chord="A#            D#" lyric="Não importa o caminho a seguir" />
        <L chord="Fm        A#" lyric="Contigo quero andar" />
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// Screens exports
// ═══════════════════════════════════════════════════════════════
function IOSHomeH1() {
  return <IOSShell><HomeContentOnly Variant={H1_SearchFirst} Nav={NavPillIndicator} /></IOSShell>;
}
function IOSRepD1() {
  return <IOSShell><RepContentOnly Variant={RepD1_DraftTop} Nav={NavPillIndicator} /></IOSShell>;
}
function IOSCifra() {
  return (
    <IOSShell>
      {/* iOS back bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '2px 10px 4px', background: '#fff', borderBottom: '1px solid #ebe8f0', flexShrink: 0 }}>
        <button style={{ display: 'flex', alignItems: 'center', gap: 2, background: 'none', border: 'none', color: BRAND.primary, fontSize: 15, fontWeight: 600, cursor: 'pointer', padding: '6px 2px' }}>
          <svg width="14" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round"><path d="M15 18l-6-6 6-6"/></svg>
          Voltar
        </button>
        <div style={{ display: 'flex', gap: 4 }}>
          <button style={{ background: 'none', border: 'none', color: BRAND.primary, fontSize: 17, fontWeight: 700, cursor: 'pointer', padding: '4px 8px' }}>⇪</button>
          <button style={{ background: 'none', border: 'none', color: BRAND.primary, fontSize: 17, fontWeight: 700, cursor: 'pointer', padding: '4px 8px' }}>⋯</button>
        </div>
      </div>
      <CifraContentOnly os="ios" />
    </IOSShell>
  );
}
function AndroidHomeH1() {
  return <AndroidShell><HomeContentOnly Variant={H1_SearchFirst} Nav={NavPillIndicator} /></AndroidShell>;
}
function AndroidRepD1() {
  return <AndroidShell><RepContentOnly Variant={RepD1_DraftTop} Nav={NavPillIndicator} /></AndroidShell>;
}
function AndroidCifra() {
  return (
    <AndroidShell>
      {/* M3 top app bar */}
      <div style={{ height: 56, background: '#fff', display: 'flex', alignItems: 'center', padding: '0 4px 0 6px', gap: 2, borderBottom: '1px solid #ebe8f0', flexShrink: 0 }}>
        <button style={{ width: 40, height: 40, borderRadius: 99, border: 'none', background: 'transparent', fontSize: 20, color: BRAND.text, cursor: 'pointer' }}>←</button>
        <div style={{ flex: 1, fontSize: 15, fontWeight: 700, color: BRAND.text, letterSpacing: -0.1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>Determinada Decisão</div>
        <button style={{ width: 40, height: 40, borderRadius: 99, border: 'none', background: 'transparent', fontSize: 18, color: BRAND.text, cursor: 'pointer' }}>⇪</button>
        <button style={{ width: 40, height: 40, borderRadius: 99, border: 'none', background: 'transparent', fontSize: 20, color: BRAND.text, cursor: 'pointer' }}>⋮</button>
      </div>
      <CifraContentOnly os="android" defaultTwoCol />
    </AndroidShell>
  );
}

Object.assign(window, { IOSHomeH1, IOSRepD1, IOSCifra, AndroidHomeH1, AndroidRepD1, AndroidCifra });
