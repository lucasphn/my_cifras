// ──────────────────────────────────────────────────────────────
// My Cifras — Mobile Home + Bottom nav variations
// Brand tokens: --primary #5b4b8a, --accent #d4af37, --text #1f2937
// Target device ~ 402x874 (iPhone 14 Pro viewport)
// ──────────────────────────────────────────────────────────────

const BRAND = {
  primary: '#5b4b8a',
  primaryHover: '#4a3a78',
  primaryLight: 'rgba(91,75,138,.09)',
  primaryLight2: 'rgba(91,75,138,.16)',
  accent: '#d4af37',
  accentBg: 'rgba(212,175,55,.12)',
  accentBorder: 'rgba(212,175,55,.28)',
  bg: '#f7f6fb',
  surface: '#ffffff',
  surface2: '#eeebf6',
  border: '#e6e1f0',
  text: '#1f2937',
  muted: '#6b7280',
  sidebar: '#a090c0',
};

// ── Icon set (stroke-based, 24px) ──────────────────────────────
const Icons = {
  home: (c, filled) => filled ? (
    <svg width="24" height="24" viewBox="0 0 24 24" fill={c}><path d="M12 3l9 8h-2v9h-5v-6h-4v6H5v-9H3l9-8z"/></svg>
  ) : (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 11l9-8 9 8v9a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1v-9z"/></svg>
  ),
  search: (c) => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>
  ),
  music: (c, filled) => filled ? (
    <svg width="24" height="24" viewBox="0 0 24 24" fill={c}><path d="M19 3v11.55A3.5 3.5 0 1 0 20.5 17V8l-10 2v7.55A3.5 3.5 0 1 0 12 20V5l7-2z"/></svg>
  ) : (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 18V6l12-2v12"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
  ),
  playlist: (c, filled) => filled ? (
    <svg width="24" height="24" viewBox="0 0 24 24" fill={c}><path d="M3 6h14v2H3zM3 11h14v2H3zM3 16h9v2H3zM20 14l4 3-4 3v-6z"/></svg>
  ) : (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M4 6h12M4 12h12M4 18h8"/><path d="M18 14l5 4-5 4z" fill={c}/></svg>
  ),
  plus: (c) => (
    <svg width="22" height="22" viewBox="0 0 22 22" fill="none" stroke={c} strokeWidth="2.4" strokeLinecap="round"><path d="M11 4v14M4 11h14"/></svg>
  ),
  play: (c) => (
    <svg width="14" height="14" viewBox="0 0 14 14" fill={c}><path d="M3 1.5v11l9-5.5z"/></svg>
  ),
  trash: (c) => (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke={c} strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><path d="M3 4h10M6.5 4V2.5h3V4M4.5 4l.5 9a1 1 0 0 0 1 1h4a1 1 0 0 0 1-1l.5-9"/></svg>
  ),
  doc: (c) => (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke={c} strokeWidth="1.5" strokeLinejoin="round"><path d="M3 1h5l3 3v9H3z"/><path d="M8 1v3h3"/></svg>
  ),
  pdf: (c) => (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke={c} strokeWidth="1.5" strokeLinejoin="round"><path d="M2 2h10v10H2z"/><path d="M5 5h4M5 8h4"/></svg>
  ),
  drag: (c) => (
    <svg width="14" height="14" viewBox="0 0 14 14" fill={c}><circle cx="5" cy="3" r="1.2"/><circle cx="9" cy="3" r="1.2"/><circle cx="5" cy="7" r="1.2"/><circle cx="9" cy="7" r="1.2"/><circle cx="5" cy="11" r="1.2"/><circle cx="9" cy="11" r="1.2"/></svg>
  ),
  more: (c) => (
    <svg width="18" height="4" viewBox="0 0 18 4" fill={c}><circle cx="2" cy="2" r="1.6"/><circle cx="9" cy="2" r="1.6"/><circle cx="16" cy="2" r="1.6"/></svg>
  ),
  close: (c) => (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke={c} strokeWidth="2" strokeLinecap="round"><path d="M3 3l8 8M11 3l-8 8"/></svg>
  ),
};

// ── Fake status bar (lightweight, no Dynamic Island needed inside canvas) ──
function MiniStatus() {
  return (
    <div style={{ height: 44, display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 22px', fontFamily: '-apple-system, system-ui', fontSize: 15, fontWeight: 600, color: '#000', flexShrink: 0 }}>
      <span>9:41</span>
      <span style={{ display: 'flex', gap: 5, alignItems: 'center' }}>
        <svg width="17" height="10" viewBox="0 0 17 10"><rect x="0" y="6" width="3" height="4" rx=".5" fill="#000"/><rect x="4" y="4" width="3" height="6" rx=".5" fill="#000"/><rect x="8" y="2" width="3" height="8" rx=".5" fill="#000"/><rect x="12" y="0" width="3" height="10" rx=".5" fill="#000"/></svg>
        <svg width="22" height="10" viewBox="0 0 22 10"><rect x="0.5" y="0.5" width="19" height="9" rx="2" stroke="#000" fill="none"/><rect x="2" y="2" width="14" height="6" rx="1" fill="#000"/></svg>
      </span>
    </div>
  );
}

// ── App header (shared) ─────────────────────────────────────────
function AppHeader() {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 16px 12px', borderBottom: `1px solid ${BRAND.border}`, background: BRAND.surface }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <div style={{ width: 30, height: 30, borderRadius: 8, background: BRAND.primary, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="#fff"><path d="M9 18V6l12-2v12"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
        </div>
        <span style={{ fontSize: 16.5, fontWeight: 800, color: BRAND.text, letterSpacing: -0.2 }}>My Cifras</span>
      </div>
      <div style={{ width: 32, height: 32, borderRadius: 99, background: BRAND.surface2, display: 'flex', alignItems: 'center', justifyContent: 'center', color: BRAND.primary, fontSize: 13, fontWeight: 700 }}>G</div>
    </div>
  );
}

// ── Stat card ───────────────────────────────────────────────────
function StatCard({ value, label, sub, wide, accent }) {
  return (
    <div style={{ flex: wide ? '1 1 100%' : 1, background: BRAND.surface, border: `1.5px solid ${BRAND.border}`, borderRadius: 14, padding: '14px 16px', boxShadow: '0 1px 3px rgba(60,40,100,.08)' }}>
      <div style={{ fontSize: 26, fontWeight: 800, color: BRAND.primary, letterSpacing: -0.8, lineHeight: 1 }}>{value}</div>
      <div style={{ fontSize: 10.5, fontWeight: 800, letterSpacing: 1.3, textTransform: 'uppercase', color: BRAND.muted, marginTop: 6 }}>{label}</div>
      {sub && <div style={{ fontSize: 11.5, color: BRAND.muted, marginTop: 2 }}>{sub}</div>}
    </div>
  );
}

// ── Song card (compact grid) ────────────────────────────────────
function SongCard({ rank, title, author, cat, tom, views }) {
  return (
    <div style={{ background: BRAND.surface, border: `1.5px solid ${BRAND.border}`, borderRadius: 12, padding: '11px 12px', boxShadow: '0 1px 3px rgba(60,40,100,.05)', position: 'relative' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 6 }}>
        <div style={{ fontSize: 13.5, fontWeight: 700, color: BRAND.text, lineHeight: 1.25, letterSpacing: -0.1 }}>{title}</div>
        <span style={{ fontSize: 10, fontWeight: 700, color: BRAND.accent, background: BRAND.accentBg, border: `1px solid ${BRAND.accentBorder}`, borderRadius: 99, padding: '1px 6px', flexShrink: 0 }}>#{rank}</span>
      </div>
      {author && <div style={{ fontSize: 11, color: BRAND.muted, marginTop: 4 }}>{author}</div>}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginTop: 7 }}>
        {cat && <span style={{ fontSize: 9.5, fontWeight: 700, color: BRAND.accent, background: BRAND.accentBg, border: `1px solid ${BRAND.accentBorder}`, borderRadius: 99, padding: '1px 6px' }}>{cat}</span>}
        {tom && <span style={{ fontSize: 9.5, fontWeight: 700, color: BRAND.accent, background: BRAND.primaryLight, borderRadius: 99, padding: '1px 6px' }}>Tom: {tom}</span>}
      </div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 8 }}>
        <span style={{ fontSize: 10, color: BRAND.muted }}>👁 {views}</span>
        <button style={{ background: BRAND.primary, color: '#fff', border: 'none', borderRadius: 99, padding: '4px 10px', fontSize: 10.5, fontWeight: 600 }}>+ Repertório</button>
      </div>
    </div>
  );
}

// ── Home body (shared content) ──────────────────────────────────
function HomeBody() {
  return (
    <div style={{ flex: 1, overflow: 'hidden', padding: '14px 14px 84px', background: BRAND.bg }}>
      {/* Quote banner */}
      <div style={{ background: BRAND.primary, borderRadius: 16, padding: '16px 18px', marginBottom: 14, color: '#fff' }}>
        <span style={{ display: 'inline-block', fontSize: 9, fontWeight: 700, letterSpacing: 1.2, textTransform: 'uppercase', color: BRAND.accent, background: 'rgba(212,175,55,.15)', border: `1px solid rgba(212,175,55,.3)`, borderRadius: 99, padding: '2px 8px' }}>Reflexão do dia</span>
        <div style={{ fontSize: 14, fontWeight: 600, lineHeight: 1.4, marginTop: 9, color: 'rgba(255,255,255,.95)' }}>"Cantar é orar duas vezes."</div>
        <div style={{ height: 2, width: 30, background: `linear-gradient(90deg, ${BRAND.accent}, transparent)`, marginTop: 10 }} />
        <div style={{ fontSize: 10.5, fontWeight: 700, color: 'rgba(255,255,255,.6)', marginTop: 8, letterSpacing: 0.3 }}>Santo Agostinho</div>
      </div>

      {/* Stats */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 14 }}>
        <StatCard wide value="473" label="Músicas" sub="no acervo" />
        <div style={{ display: 'flex', gap: 8 }}>
          <StatCard value="336" label="Ministração" sub="71% do acervo" />
          <StatCard value="137" label="Missa" sub="29% do acervo" />
        </div>
      </div>

      {/* Mais tocadas */}
      <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: 10 }}>
        <h3 style={{ margin: 0, fontSize: 15, fontWeight: 800, color: BRAND.text, letterSpacing: -0.2 }}>Mais tocadas</h3>
        <span style={{ fontSize: 11, fontWeight: 600, color: BRAND.primary }}>Ver todas →</span>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
        <SongCard rank="1" title="Determinada Decisão" author="Juninho Casimiro" cat="Fé e Conversão" tom="A#" views="44" />
        <SongCard rank="2" title="Estava com Saudade de Ti" cat="Adoração" tom="G" views="36" />
        <SongCard rank="3" title="Me faz novo" cat="Entrega" tom="C" views="19" />
        <SongCard rank="4" title="Converte-me" cat="Fé e Conversão" tom="A" views="18" />
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// NAV VARIATIONS
// ═══════════════════════════════════════════════════════════════

// N1 — Floating pill tab bar (liquid glass style)
function NavFloatingPill({ active = 'home' }) {
  const items = [
    { id: 'home', label: 'Início', icon: Icons.home },
    { id: 'search', label: 'Pesquisar', icon: Icons.search },
    { id: 'rep', label: 'Repertório', icon: Icons.playlist },
  ];
  return (
    <div style={{ position: 'absolute', left: 16, right: 16, bottom: 18, zIndex: 30 }}>
      <div style={{ background: 'rgba(255,255,255,0.85)', backdropFilter: 'blur(20px) saturate(180%)', WebkitBackdropFilter: 'blur(20px) saturate(180%)', borderRadius: 99, padding: '6px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', boxShadow: '0 8px 24px rgba(60,40,100,.18), 0 1px 3px rgba(60,40,100,.08)', border: '1px solid rgba(255,255,255,0.6)' }}>
        {items.map(it => {
          const on = it.id === active;
          return (
            <button key={it.id} style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, padding: '10px 8px', borderRadius: 99, background: on ? BRAND.primary : 'transparent', color: on ? '#fff' : BRAND.muted, border: 'none', cursor: 'pointer', transition: 'all .18s' }}>
              {it.icon(on ? '#fff' : BRAND.muted, on)}
              {on && <span style={{ fontSize: 12, fontWeight: 700 }}>{it.label}</span>}
            </button>
          );
        })}
      </div>
    </div>
  );
}

// N2 — Bottom bar with purple pill indicator
function NavPillIndicator({ active = 'home' }) {
  const items = [
    { id: 'home', label: 'Início', icon: Icons.home },
    { id: 'search', label: 'Pesquisar', icon: Icons.search },
    { id: 'rep', label: 'Repertório', icon: Icons.playlist },
  ];
  return (
    <div style={{ position: 'absolute', left: 0, right: 0, bottom: 0, zIndex: 30, background: BRAND.surface, borderTop: `1px solid ${BRAND.border}`, padding: '8px 12px 18px', display: 'flex', justifyContent: 'space-around' }}>
      {items.map(it => {
        const on = it.id === active;
        return (
          <div key={it.id} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4, flex: 1 }}>
            <div style={{ padding: '6px 18px', borderRadius: 99, background: on ? BRAND.primaryLight2 : 'transparent', transition: 'all .18s' }}>
              {it.icon(on ? BRAND.primary : BRAND.muted, on)}
            </div>
            <span style={{ fontSize: 10.5, fontWeight: on ? 700 : 500, color: on ? BRAND.primary : BRAND.muted }}>{it.label}</span>
          </div>
        );
      })}
    </div>
  );
}

// N3 — Minimal bar with top indicator line
function NavTopIndicator({ active = 'home' }) {
  const items = [
    { id: 'home', label: 'Início', icon: Icons.home },
    { id: 'search', label: 'Pesquisar', icon: Icons.search },
    { id: 'rep', label: 'Repertório', icon: Icons.playlist },
  ];
  return (
    <div style={{ position: 'absolute', left: 0, right: 0, bottom: 0, zIndex: 30, background: BRAND.surface, borderTop: `1px solid ${BRAND.border}`, paddingBottom: 14, display: 'flex' }}>
      {items.map(it => {
        const on = it.id === active;
        return (
          <div key={it.id} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4, flex: 1, padding: '10px 0 6px', position: 'relative' }}>
            {on && <div style={{ position: 'absolute', top: 0, left: '30%', right: '30%', height: 3, background: BRAND.primary, borderRadius: '0 0 3px 3px' }} />}
            {it.icon(on ? BRAND.primary : BRAND.muted, on)}
            <span style={{ fontSize: 10.5, fontWeight: on ? 700 : 500, color: on ? BRAND.primary : BRAND.muted, letterSpacing: -0.1 }}>{it.label}</span>
          </div>
        );
      })}
    </div>
  );
}

// N4 — Icons only, large, with purple dot indicator
function NavIconsOnly({ active = 'home' }) {
  const items = [
    { id: 'home', icon: Icons.home },
    { id: 'search', icon: Icons.search },
    { id: 'rep', icon: Icons.playlist },
  ];
  return (
    <div style={{ position: 'absolute', left: 0, right: 0, bottom: 0, zIndex: 30, background: BRAND.surface, borderTop: `1px solid ${BRAND.border}`, paddingBottom: 14, display: 'flex' }}>
      {items.map(it => {
        const on = it.id === active;
        return (
          <div key={it.id} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 5, flex: 1, padding: '14px 0 8px' }}>
            {it.icon(on ? BRAND.primary : BRAND.muted, on)}
            <div style={{ width: 4, height: 4, borderRadius: 2, background: on ? BRAND.primary : 'transparent' }} />
          </div>
        );
      })}
    </div>
  );
}

// ── Phone frame (mini) ──────────────────────────────────────────
function Phone({ children }) {
  return (
    <div style={{ width: 390, height: 720, borderRadius: 40, overflow: 'hidden', position: 'relative', background: BRAND.bg, boxShadow: '0 20px 50px rgba(60,40,100,.18), 0 0 0 10px #1a1529, 0 0 0 11px #000', border: 'none' }}>
      {/* Dynamic island */}
      <div style={{ position: 'absolute', top: 9, left: '50%', transform: 'translateX(-50%)', width: 110, height: 28, borderRadius: 18, background: '#000', zIndex: 50 }} />
      <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <MiniStatus />
        {children}
      </div>
    </div>
  );
}

// Home screen factory
function HomeScreen({ Nav }) {
  return (
    <Phone>
      <AppHeader />
      <HomeBody />
      <Nav active="home" />
    </Phone>
  );
}

Object.assign(window, {
  BRAND, Icons, Phone, HomeScreen, HomeBody, AppHeader,
  NavFloatingPill, NavPillIndicator, NavTopIndicator, NavIconsOnly,
});
