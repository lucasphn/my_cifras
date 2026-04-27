// My Cifras — Repertório panel variations
// Uses BRAND tokens from mobile-home.jsx

// Sample data
const REPS = [
  { id: 1, name: 'Missa 19-04-26', count: 13, last: 'Há 2 dias', color: '#5b4b8a' },
  { id: 2, name: 'Teste', count: 3, last: 'Há 5 dias', color: '#8b7bca' },
  { id: 3, name: 'Cenáculo', count: 8, last: 'Semana passada', color: '#a090c0' },
];

const CURR_SONGS = [
  { title: 'Determinada Decisão', tom: 'A#', cat: 'Fé' },
  { title: 'Estava com Saudade de Ti', tom: 'G', cat: 'Adoração' },
  { title: 'Me faz novo', tom: 'C', cat: 'Entrega' },
];

// ═══════════════════════════════════════════════════════════════
// R1 — Lista em cards com swipe-to-delete + CTA destacado
// ═══════════════════════════════════════════════════════════════
function RepV1_Cards() {
  return (
    <div style={{ flex: 1, overflow: 'hidden', padding: '12px 14px 100px', background: BRAND.bg }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
        <h2 style={{ margin: 0, fontSize: 18, fontWeight: 800, color: BRAND.text, letterSpacing: -0.3 }}>Repertórios</h2>
        <button style={{ background: BRAND.primary, color: '#fff', border: 'none', borderRadius: 99, padding: '7px 14px', fontSize: 12, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 5, boxShadow: '0 2px 8px rgba(91,75,138,.28)' }}>
          {Icons.plus('#fff')} Novo
        </button>
      </div>

      {REPS.map(r => (
        <div key={r.id} style={{ background: BRAND.surface, border: `1.5px solid ${BRAND.border}`, borderRadius: 14, padding: '12px 14px', marginBottom: 10, display: 'flex', alignItems: 'center', gap: 12, boxShadow: '0 1px 3px rgba(60,40,100,.06)' }}>
          <div style={{ width: 42, height: 42, borderRadius: 10, background: r.color, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
            {Icons.music('#fff', true)}
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: 14, fontWeight: 700, color: BRAND.text, letterSpacing: -0.1 }}>{r.name}</div>
            <div style={{ fontSize: 11.5, color: BRAND.muted, marginTop: 2 }}>{r.count} músicas · {r.last}</div>
          </div>
          <button style={{ width: 36, height: 36, borderRadius: 99, background: BRAND.primary, border: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 2px 6px rgba(91,75,138,.3)' }}>
            {Icons.play('#fff')}
          </button>
          <button style={{ width: 28, height: 28, borderRadius: 99, background: 'transparent', border: 'none', color: BRAND.muted }}>
            {Icons.more(BRAND.muted)}
          </button>
        </div>
      ))}

      <div style={{ marginTop: 20, padding: '14px 14px 12px', background: BRAND.surface, border: `1.5px dashed ${BRAND.border}`, borderRadius: 14 }}>
        <div style={{ fontSize: 10.5, fontWeight: 800, letterSpacing: 1.2, textTransform: 'uppercase', color: BRAND.muted, marginBottom: 8 }}>Criar novo</div>
        <input placeholder="Nome do repertório..." style={{ width: '100%', padding: '10px 14px', border: `1.5px solid ${BRAND.border}`, borderRadius: 99, background: BRAND.bg, fontSize: 13, color: BRAND.text, outline: 'none', boxSizing: 'border-box' }} />
        <button style={{ marginTop: 8, width: '100%', padding: '10px', background: BRAND.primary, color: '#fff', border: 'none', borderRadius: 99, fontSize: 13, fontWeight: 700 }}>Criar repertório</button>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// R2 — Repertório ativo em destaque no topo
// ═══════════════════════════════════════════════════════════════
function RepV2_ActiveFocus() {
  return (
    <div style={{ flex: 1, overflow: 'hidden', padding: '0 0 100px', background: BRAND.bg }}>
      {/* Active rep hero */}
      <div style={{ background: `linear-gradient(145deg, ${BRAND.primary} 0%, #4a3a78 100%)`, padding: '16px 18px 18px', color: '#fff' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ fontSize: 9.5, fontWeight: 800, letterSpacing: 1.4, textTransform: 'uppercase', color: BRAND.accent }}>Ativo agora</div>
          <button style={{ background: 'rgba(255,255,255,.12)', color: '#fff', border: 'none', borderRadius: 99, padding: '4px 10px', fontSize: 11, fontWeight: 600 }}>Trocar</button>
        </div>
        <div style={{ fontSize: 20, fontWeight: 800, marginTop: 6, letterSpacing: -0.3 }}>Missa 19-04-26</div>
        <div style={{ fontSize: 12, color: 'rgba(255,255,255,.7)', marginTop: 2 }}>13 músicas · ~52 min</div>

        <div style={{ display: 'flex', gap: 7, marginTop: 14 }}>
          <button style={{ flex: 1, background: BRAND.accent, color: '#1f1b2e', border: 'none', borderRadius: 99, padding: '9px', fontSize: 12, fontWeight: 800, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 5 }}>
            {Icons.play('#1f1b2e')} Apresentar
          </button>
          <button style={{ background: 'rgba(255,255,255,.14)', color: '#fff', border: 'none', borderRadius: 99, padding: '9px 14px', fontSize: 12, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 5 }}>
            {Icons.pdf('#fff')} PDF
          </button>
          <button style={{ background: 'rgba(255,255,255,.14)', color: '#fff', border: 'none', borderRadius: 99, padding: '9px 14px', fontSize: 12, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 5 }}>
            {Icons.doc('#fff')} Doc
          </button>
        </div>
      </div>

      {/* Current rep song list */}
      <div style={{ padding: '14px 14px 0' }}>
        <div style={{ fontSize: 10.5, fontWeight: 800, letterSpacing: 1.2, textTransform: 'uppercase', color: BRAND.muted, marginBottom: 8 }}>Músicas</div>
        {CURR_SONGS.map((s, i) => (
          <div key={i} style={{ background: BRAND.surface, border: `1px solid ${BRAND.border}`, borderRadius: 10, padding: '10px 12px', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ color: BRAND.muted, cursor: 'grab' }}>{Icons.drag(BRAND.muted)}</div>
            <span style={{ fontSize: 11.5, fontWeight: 700, color: BRAND.primary, width: 20 }}>{i + 1}.</span>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: 13, fontWeight: 700, color: BRAND.text, letterSpacing: -0.1 }}>{s.title}</div>
              <div style={{ fontSize: 10.5, color: BRAND.muted, marginTop: 1 }}>{s.cat}</div>
            </div>
            <span style={{ fontSize: 10, fontWeight: 700, color: BRAND.accent, background: BRAND.accentBg, border: `1px solid ${BRAND.accentBorder}`, borderRadius: 99, padding: '1px 7px' }}>Tom: {s.tom}</span>
          </div>
        ))}
      </div>

      {/* Other reps */}
      <div style={{ padding: '18px 14px 0' }}>
        <div style={{ fontSize: 10.5, fontWeight: 800, letterSpacing: 1.2, textTransform: 'uppercase', color: BRAND.muted, marginBottom: 8, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>Outros repertórios</span>
          <span style={{ color: BRAND.primary, fontSize: 11, fontWeight: 700 }}>+ Novo</span>
        </div>
        {REPS.slice(1).map(r => (
          <div key={r.id} style={{ background: BRAND.surface, border: `1px solid ${BRAND.border}`, borderRadius: 10, padding: '10px 12px', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ width: 32, height: 32, borderRadius: 8, background: r.color, opacity: 0.85, flexShrink: 0 }} />
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 13, fontWeight: 700, color: BRAND.text }}>{r.name}</div>
              <div style={{ fontSize: 10.5, color: BRAND.muted, marginTop: 1 }}>{r.count} músicas · {r.last}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// R3 — Criação inline expansível + empty state acolhedor
// ═══════════════════════════════════════════════════════════════
function RepV3_InlineCreate() {
  return (
    <div style={{ flex: 1, overflow: 'hidden', padding: '12px 14px 100px', background: BRAND.bg }}>
      <h2 style={{ margin: '0 0 14px', fontSize: 22, fontWeight: 800, color: BRAND.text, letterSpacing: -0.4 }}>Meus Repertórios</h2>

      {/* New rep — large tappable */}
      <button style={{ width: '100%', display: 'flex', alignItems: 'center', gap: 10, padding: '14px 14px', background: BRAND.primary, border: 'none', borderRadius: 14, color: '#fff', marginBottom: 14, boxShadow: '0 4px 14px rgba(91,75,138,.28)' }}>
        <div style={{ width: 32, height: 32, borderRadius: 99, background: 'rgba(255,255,255,.18)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          {Icons.plus('#fff')}
        </div>
        <div style={{ textAlign: 'left', flex: 1 }}>
          <div style={{ fontSize: 14, fontWeight: 800 }}>Criar novo repertório</div>
          <div style={{ fontSize: 11, color: 'rgba(255,255,255,.7)', marginTop: 1 }}>Monte sua lista pra ensaio ou missa</div>
        </div>
      </button>

      {REPS.map(r => (
        <div key={r.id} style={{ background: BRAND.surface, border: `1.5px solid ${BRAND.border}`, borderRadius: 14, padding: '12px 12px 12px 14px', marginBottom: 10, display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ width: 40, height: 40, borderRadius: 10, background: r.color, opacity: 0.9, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
            {Icons.playlist('#fff', true)}
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: 14, fontWeight: 700, color: BRAND.text }}>{r.name}</div>
            <div style={{ display: 'flex', gap: 8, fontSize: 11, color: BRAND.muted, marginTop: 3 }}>
              <span>{r.count} músicas</span>
              <span>·</span>
              <span>{r.last}</span>
            </div>
          </div>
          <div style={{ display: 'flex', gap: 6 }}>
            <button style={{ width: 34, height: 34, borderRadius: 99, background: BRAND.primaryLight, border: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {Icons.play(BRAND.primary)}
            </button>
            <button style={{ width: 34, height: 34, borderRadius: 99, background: BRAND.surface2, border: 'none', color: BRAND.muted, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {Icons.more(BRAND.muted)}
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// R4 — Detail view (inside a repertório) — scroll with sticky actions
// ═══════════════════════════════════════════════════════════════
function RepV4_DetailView() {
  return (
    <div style={{ flex: 1, overflow: 'hidden', background: BRAND.bg, display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <div style={{ padding: '10px 14px 14px', background: BRAND.surface, borderBottom: `1px solid ${BRAND.border}` }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
          <button style={{ background: 'none', border: 'none', color: BRAND.primary, fontSize: 14, fontWeight: 700, padding: 0 }}>← Voltar</button>
          <div style={{ flex: 1 }} />
          <button style={{ background: 'none', border: 'none', color: BRAND.muted }}>{Icons.more(BRAND.muted)}</button>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ width: 56, height: 56, borderRadius: 14, background: `linear-gradient(135deg, ${BRAND.primary}, #8b7bca)`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            {Icons.playlist('#fff', true)}
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: 20, fontWeight: 800, color: BRAND.text, letterSpacing: -0.3 }}>Missa 19-04-26</div>
            <div style={{ fontSize: 12, color: BRAND.muted, marginTop: 2 }}>13 músicas · ~52 min</div>
          </div>
        </div>
      </div>

      {/* Song list */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '12px 14px 120px' }}>
        {CURR_SONGS.concat(CURR_SONGS).map((s, i) => (
          <div key={i} style={{ background: BRAND.surface, border: `1px solid ${BRAND.border}`, borderRadius: 10, padding: '11px 12px', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ color: BRAND.muted, cursor: 'grab' }}>{Icons.drag(BRAND.muted)}</div>
            <span style={{ fontSize: 12, fontWeight: 700, color: BRAND.primary, width: 18 }}>{i + 1}</span>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: 13, fontWeight: 700, color: BRAND.text }}>{s.title}</div>
              <div style={{ fontSize: 10.5, color: BRAND.muted, marginTop: 1 }}>Tom: {s.tom} · {s.cat}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Sticky action bar */}
      <div style={{ position: 'absolute', left: 14, right: 14, bottom: 78, zIndex: 20, background: BRAND.surface, borderRadius: 14, padding: '10px', display: 'flex', gap: 6, boxShadow: '0 12px 40px rgba(60,40,100,.18), 0 2px 8px rgba(60,40,100,.08)', border: `1px solid ${BRAND.border}` }}>
        <button style={{ flex: 1, background: BRAND.primary, color: '#fff', border: 'none', borderRadius: 10, padding: '11px', fontSize: 13, fontWeight: 800, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}>
          {Icons.play('#fff')} Apresentar
        </button>
        <button style={{ background: BRAND.surface2, color: BRAND.text, border: 'none', borderRadius: 10, padding: '11px 14px', fontSize: 12, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 6 }}>
          {Icons.pdf(BRAND.primary)} PDF
        </button>
        <button style={{ background: BRAND.surface2, color: BRAND.text, border: 'none', borderRadius: 10, padding: '11px 14px', fontSize: 12, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 6 }}>
          {Icons.doc(BRAND.primary)}
        </button>
      </div>
    </div>
  );
}

// Wrapper phone for repertório variations (uses same bottom nav)
function RepScreen({ Variant, Nav }) {
  return (
    <Phone>
      <AppHeader />
      <Variant />
      <Nav active="rep" />
    </Phone>
  );
}

Object.assign(window, { RepV1_Cards, RepV2_ActiveFocus, RepV3_InlineCreate, RepV4_DetailView, RepScreen });
