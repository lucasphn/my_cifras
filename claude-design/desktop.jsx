// ──────────────────────────────────────────────────────────────
// My Cifras — DESKTOP
// Reaproveita: BRAND, Icons, Icons2, LITURGY, LiturgyDot,
//              SongHCard, CatChip, EventCard, LiturgyCompact
// Viewport alvo: 1920 × 1080
// ──────────────────────────────────────────────────────────────

// ═══════════════════════════════════════════════════════════════
// Frame desktop (chrome básico com barra de janela sutil)
// ═══════════════════════════════════════════════════════════════
function DesktopFrame({ children, w = 1920, h = 1080 }) {
  return (
    <div style={{ width: w, height: h, background: BRAND.bg, borderRadius: 12, overflow: 'hidden', boxShadow: '0 30px 80px rgba(60,40,100,.18), 0 0 0 1px rgba(60,40,100,.08)', position: 'relative', display: 'flex', flexDirection: 'column', fontFamily: 'Inter, system-ui, sans-serif' }}>
      {children}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// TOP BAR desktop (header)
// ═══════════════════════════════════════════════════════════════
function DesktopTopBar({ showSearch = true }) {
  return (
    <div style={{ height: 62, background: BRAND.surface, borderBottom: `1px solid ${BRAND.border}`, display: 'flex', alignItems: 'center', padding: '0 24px', gap: 20, flexShrink: 0 }}>
      {/* Logo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, minWidth: 240 }}>
        <div style={{ width: 34, height: 34, borderRadius: 9, background: BRAND.primary, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M9 18V6l12-2v12"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
        </div>
        <div>
          <div style={{ fontSize: 16, fontWeight: 800, color: BRAND.text, letterSpacing: -0.3, lineHeight: 1 }}>My Cifras</div>
          <div style={{ fontSize: 10.5, fontWeight: 600, color: BRAND.muted, marginTop: 2 }}>473 músicas · 3 repertórios</div>
        </div>
      </div>

      {/* Search (central, protagonista) */}
      {showSearch && (
        <div style={{ flex: 1, maxWidth: 720, margin: '0 auto', position: 'relative' }}>
          <div style={{ position: 'absolute', left: 16, top: '50%', transform: 'translateY(-50%)', color: BRAND.muted, display: 'flex' }}>{Icons.search(BRAND.muted)}</div>
          <input placeholder="Buscar música, artista ou trecho da letra..." style={{ width: '100%', padding: '11px 130px 11px 46px', borderRadius: 99, border: `1.5px solid ${BRAND.border}`, background: BRAND.bg, fontSize: 14, fontWeight: 500, color: BRAND.text, outline: 'none', fontFamily: 'inherit', boxSizing: 'border-box' }} />
          <div style={{ position: 'absolute', right: 6, top: '50%', transform: 'translateY(-50%)', display: 'flex', background: BRAND.surface2, borderRadius: 99, padding: 2 }}>
            <button style={{ padding: '5px 12px', borderRadius: 99, border: 'none', background: BRAND.primary, color: '#fff', fontSize: 11.5, fontWeight: 700, cursor: 'pointer' }}>Nome</button>
            <button style={{ padding: '5px 12px', borderRadius: 99, border: 'none', background: 'transparent', color: BRAND.muted, fontSize: 11.5, fontWeight: 600, cursor: 'pointer' }}>Letra</button>
          </div>
        </div>
      )}

      {/* Right: actions + avatar */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, minWidth: 240, justifyContent: 'flex-end' }}>
        <button style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '8px 14px', borderRadius: 99, border: `1.5px solid ${BRAND.border}`, background: BRAND.surface, color: BRAND.text, fontSize: 12.5, fontWeight: 700, cursor: 'pointer' }}>
          {Icons2.plusBold(BRAND.primary)} Importar cifra
        </button>
        <button style={{ width: 38, height: 38, borderRadius: 99, border: 'none', background: BRAND.surface2, display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', position: 'relative' }}>
          {Icons2.bell(BRAND.text)}
          <span style={{ position: 'absolute', top: 8, right: 8, width: 8, height: 8, borderRadius: 99, background: BRAND.accent, border: `2px solid ${BRAND.surface2}` }} />
        </button>
        <div style={{ width: 38, height: 38, borderRadius: 99, background: BRAND.primary, color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, fontWeight: 700 }}>L</div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// SIDEBAR ESQUERDA (categorias)
// ═══════════════════════════════════════════════════════════════
function DesktopLeftSidebar({ activeCat = 'Fé e Conversão' }) {
  const CAT_MIN = [
    { label: 'Acolhida', count: 35 },
    { label: 'Adoração', count: 31 },
    { label: 'Amor de Deus', count: 21 },
    { label: 'Animação', count: 33 },
    { label: 'Comunidade e Vocação', count: 19 },
    { label: 'Cura e Libertação', count: 10 },
    { label: 'Entrega', count: 30 },
    { label: 'Espírito Santo', count: 24 },
    { label: 'Fé e Conversão', count: 20 },
    { label: 'Louvor', count: 7 },
    { label: 'Maria', count: 18 },
    { label: 'Pecado e Salvação', count: 21 },
    { label: 'Vida em Santidade', count: 20 },
  ];
  const CAT_MIS = [
    { label: 'Tempo Comum', count: 79 },
    { label: 'Advento', count: 16 },
    { label: 'Páscoa', count: 6 },
    { label: 'Quaresma', count: 4 },
  ];
  const Row = ({ c, color = BRAND.primary }) => {
    const active = c.label === activeCat;
    return (
      <div style={{ position: 'relative', display: 'flex', alignItems: 'center', gap: 2, marginBottom: 1 }}>
        <button style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 10, padding: '8px 12px', background: active ? BRAND.primaryLight : 'transparent', borderRadius: 8, border: 'none', cursor: 'pointer', textAlign: 'left' }}>
          <div style={{ width: 3, height: 14, borderRadius: 2, background: active ? color : 'transparent', flexShrink: 0 }} />
          <span style={{ flex: 1, fontSize: 12.5, fontWeight: active ? 700 : 500, color: active ? BRAND.primary : BRAND.text, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{c.label}</span>
          <span style={{ fontSize: 10, fontWeight: 700, color: active ? BRAND.primary : BRAND.muted, background: active ? BRAND.surface : BRAND.surface2, padding: '1px 7px', borderRadius: 99 }}>{c.count}</span>
        </button>
        {active && (
          <button title="Renomear · Excluir (owner)" style={{ width: 22, height: 22, borderRadius: 6, background: BRAND.surface, border: `1px solid ${BRAND.border}`, color: BRAND.muted, fontSize: 11, fontWeight: 800, cursor: 'pointer', marginRight: 4 }}>⋯</button>
        )}
      </div>
    );
  };
  return (
    <div style={{ width: 260, background: BRAND.surface, borderRight: `1px solid ${BRAND.border}`, overflow: 'auto', flexShrink: 0, padding: '16px 10px' }}>
      <button style={{ width: '100%', display: 'flex', alignItems: 'center', gap: 10, padding: '9px 12px', background: 'transparent', border: 'none', cursor: 'pointer', textAlign: 'left', borderRadius: 8, marginBottom: 6 }}>
        {Icons.home(BRAND.text, false)}
        <span style={{ fontSize: 13, fontWeight: 700, color: BRAND.text }}>Início</span>
      </button>

      <div style={{ fontSize: 10, fontWeight: 800, letterSpacing: 1.3, textTransform: 'uppercase', color: BRAND.muted, margin: '14px 12px 6px' }}>Ministração · 336</div>
      {CAT_MIN.map((c, i) => <Row key={i} c={c} />)}

      <div style={{ fontSize: 10, fontWeight: 800, letterSpacing: 1.3, textTransform: 'uppercase', color: BRAND.muted, margin: '14px 12px 6px' }}>Missa · 137</div>
      {CAT_MIS.map((c, i) => <Row key={i} c={c} color={BRAND.accent} />)}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// PAINEL REPERTÓRIO (direita) — modelo D1 adaptado p/ desktop
// ═══════════════════════════════════════════════════════════════
const DT_DRAFT = [
  { title: 'Determinada Decisão', tom: 'A#', cat: 'Fé e Conversão' },
  { title: 'Estava com Saudade de Ti', tom: 'G', cat: 'Adoração' },
  { title: 'Me faz novo', tom: 'C', cat: 'Entrega' },
];
const DT_SAVED = [
  { id: 1, name: 'Missa 19-04-26', count: 13, last: 'Há 2 dias', color: '#5b4b8a' },
  { id: 2, name: 'Teste', count: 3, last: 'Há 5 dias', color: '#8b7bca' },
  { id: 3, name: 'Cenáculo', count: 8, last: 'Semana passada', color: '#a090c0' },
];

function DesktopRightRep() {
  return (
    <div style={{ width: 360, background: BRAND.surface, borderLeft: `1px solid ${BRAND.border}`, overflow: 'auto', flexShrink: 0, padding: '16px 14px 20px' }}>
      {/* Draft header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
          <span style={{ width: 8, height: 8, borderRadius: 99, background: BRAND.accent, boxShadow: `0 0 0 3px ${BRAND.accentBg}` }} />
          <span style={{ fontSize: 10.5, fontWeight: 800, letterSpacing: 1.4, textTransform: 'uppercase', color: BRAND.muted }}>Em montagem</span>
        </div>
        <span style={{ fontSize: 11, fontWeight: 700, color: BRAND.muted }}>{DT_DRAFT.length} músicas</span>
      </div>

      {/* Draft card */}
      <div style={{ background: BRAND.bg, border: `1.5px solid ${BRAND.primary}`, borderRadius: 14, padding: 12, boxShadow: '0 4px 16px rgba(91,75,138,.12)', marginBottom: 20 }}>
        <input placeholder="Dê um nome ao repertório..." style={{ width: '100%', padding: '10px 12px', border: `1.5px solid ${BRAND.border}`, borderRadius: 10, background: BRAND.surface, fontSize: 13, fontWeight: 600, color: BRAND.text, outline: 'none', boxSizing: 'border-box', fontFamily: 'inherit', marginBottom: 10 }} />
        {DT_DRAFT.map((s, i) => (
          <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '7px 4px', borderBottom: i < DT_DRAFT.length - 1 ? `1px solid ${BRAND.border}` : 'none' }}>
            {Icons.drag(BRAND.muted)}
            <span style={{ fontSize: 11, fontWeight: 700, color: BRAND.primary, width: 14 }}>{i + 1}</span>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: 12.5, fontWeight: 700, color: BRAND.text, letterSpacing: -0.1, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{s.title}</div>
              <div style={{ fontSize: 10.5, color: BRAND.muted, marginTop: 1 }}>{s.cat}</div>
            </div>
            <span style={{ fontSize: 10, fontWeight: 700, color: BRAND.accent, background: BRAND.accentBg, border: `1px solid ${BRAND.accentBorder}`, borderRadius: 99, padding: '1px 7px' }}>{s.tom}</span>
          </div>
        ))}
        <div style={{ display: 'flex', gap: 6, marginTop: 10 }}>
          <button style={{ flex: 1, background: BRAND.primary, color: '#fff', border: 'none', borderRadius: 99, padding: '9px', fontSize: 12, fontWeight: 800, cursor: 'pointer' }}>Salvar repertório</button>
          <button style={{ background: 'transparent', color: BRAND.muted, border: `1.5px solid ${BRAND.border}`, borderRadius: 99, padding: '9px 12px', fontSize: 11, fontWeight: 600, cursor: 'pointer' }}>Limpar</button>
        </div>
      </div>

      {/* Saved reps */}
      <div style={{ fontSize: 10, fontWeight: 800, letterSpacing: 1.3, textTransform: 'uppercase', color: BRAND.muted, marginBottom: 10 }}>Salvos · {DT_SAVED.length}</div>
      {DT_SAVED.map(r => (
        <div key={r.id} style={{ background: BRAND.bg, border: `1px solid ${BRAND.border}`, borderRadius: 12, padding: '10px 11px', marginBottom: 7, display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ width: 34, height: 34, borderRadius: 9, background: r.color, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
            {Icons.music('#fff', true)}
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: 12.5, fontWeight: 700, color: BRAND.text, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{r.name}</div>
            <div style={{ fontSize: 10.5, color: BRAND.muted, marginTop: 1 }}>{r.count} músicas · {r.last}</div>
          </div>
          <button style={{ width: 30, height: 30, borderRadius: 99, background: BRAND.primaryLight, border: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>{Icons.play(BRAND.primary)}</button>
        </div>
      ))}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// HOME DESKTOP — conteúdo central
// Busca no top bar · liturgia ampla · continue de onde parou
// · próximos eventos · 4 categorias rápidas
// ═══════════════════════════════════════════════════════════════
function DesktopHomeContent() {
  return (
    <div style={{ flex: 1, overflow: 'auto', padding: '28px 36px 40px', background: BRAND.bg }}>
      {/* Greeting */}
      <div style={{ marginBottom: 22 }}>
        <div style={{ fontSize: 28, fontWeight: 800, color: BRAND.text, letterSpacing: -0.6, lineHeight: 1.1 }}>Bom dia, Lucas</div>
        <div style={{ fontSize: 13.5, color: BRAND.muted, marginTop: 5, display: 'flex', alignItems: 'center', gap: 6 }}>
          {Icons2.sparkle(BRAND.accent)}
          <span style={{ fontStyle: 'italic' }}>"Cantar é orar duas vezes." — Santo Agostinho</span>
        </div>
      </div>

      {/* Two-column: Liturgia (larger) + Continue de onde parou */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.1fr 1fr', gap: 18, marginBottom: 24 }}>
        {/* Liturgia card grande */}
        <div style={{ background: `linear-gradient(160deg, ${LITURGY.branco.bg}, #fff 70%)`, border: `1px solid ${LITURGY.branco.border}`, borderRadius: 18, padding: '20px 22px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <LiturgyDot kind="branco" size={14} />
              <span style={{ fontSize: 11, fontWeight: 800, letterSpacing: 1.4, textTransform: 'uppercase', color: LITURGY.branco.text }}>Branco · Tempo Pascal</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 4, background: BRAND.surface, borderRadius: 99, padding: 3, border: `1px solid ${BRAND.border}` }}>
              <button style={{ padding: '4px 10px', borderRadius: 99, border: 'none', background: BRAND.primary, color: '#fff', fontSize: 11, fontWeight: 700, cursor: 'pointer' }}>Hoje</button>
              <button style={{ padding: '4px 10px', borderRadius: 99, border: 'none', background: 'transparent', color: BRAND.muted, fontSize: 11, fontWeight: 600, cursor: 'pointer' }}>Sáb</button>
              <button style={{ padding: '4px 10px', borderRadius: 99, border: 'none', background: 'transparent', color: BRAND.muted, fontSize: 11, fontWeight: 600, cursor: 'pointer' }}>Dom</button>
              <div style={{ width: 1, height: 14, background: BRAND.border, margin: '0 2px' }} />
              <button title="Escolher data" style={{ display: 'flex', alignItems: 'center', gap: 4, padding: '4px 10px', borderRadius: 99, border: 'none', background: 'transparent', color: BRAND.muted, fontSize: 11, fontWeight: 600, cursor: 'pointer' }}>
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>
                Data
              </button>
            </div>
          </div>
          <div style={{ fontSize: 22, fontWeight: 800, color: BRAND.text, letterSpacing: -0.4, lineHeight: 1.15 }}>2ª feira da 3ª Semana da Páscoa</div>
          <div style={{ fontSize: 13, color: BRAND.muted, marginTop: 4 }}>Segunda, 20 de abril de 2026</div>

          {/* Leituras */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8, marginTop: 16 }}>
            {[
              { label: '1ª Leitura', ref: 'At 6, 8-15' },
              { label: 'Salmo', ref: 'Sl 118 (119)' },
              { label: 'Evangelho', ref: 'Jo 6, 22-29' },
            ].map((l, i) => (
              <button key={i} style={{ background: BRAND.surface, border: `1px solid ${BRAND.border}`, borderRadius: 10, padding: '8px 11px', textAlign: 'left', cursor: 'pointer' }}>
                <div style={{ fontSize: 9.5, fontWeight: 800, letterSpacing: 1.2, textTransform: 'uppercase', color: BRAND.muted }}>{l.label}</div>
                <div style={{ fontSize: 12, fontWeight: 700, color: BRAND.text, marginTop: 2 }}>{l.ref}</div>
              </button>
            ))}
          </div>

          <div style={{ marginTop: 14, display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 10 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: BRAND.primary, fontSize: 12, fontWeight: 700, cursor: 'pointer' }}>
              {Icons2.book(BRAND.primary)} Ler textos completos →
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 5, color: BRAND.muted, fontSize: 11.5, fontWeight: 600, cursor: 'pointer' }}>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>
              Calendário completo
            </div>
          </div>
        </div>

        {/* Próximo evento + agenda */}
        <div style={{ background: BRAND.surface, border: `1.5px solid ${BRAND.border}`, borderRadius: 18, padding: '18px 20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
            <span style={{ fontSize: 11, fontWeight: 800, letterSpacing: 1.4, textTransform: 'uppercase', color: BRAND.muted }}>Próximos eventos</span>
            <button style={{ background: 'none', border: 'none', fontSize: 12, fontWeight: 700, color: BRAND.primary, cursor: 'pointer', padding: 0 }}>+ Novo</button>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <EventCard day="20" month="ABR" title="Missa Dominical 10h — São José" time="10:00 · Hoje" type="Missa" liturgy="branco" />
            <EventCard day="22" month="ABR" title="Ensaio grupo de louvor" time="19:30 — 21:30" type="Ensaio" />
            <EventCard day="26" month="ABR" title="Missa da Divina Misericórdia" time="08:30" type="Missa" liturgy="branco" />
          </div>
        </div>
      </div>

      {/* Continue de onde parou */}
      <div style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: 12 }}>
          <h3 style={{ margin: 0, fontSize: 16, fontWeight: 800, color: BRAND.text, letterSpacing: -0.3 }}>Continue de onde parou</h3>
          <span style={{ fontSize: 12, fontWeight: 700, color: BRAND.primary, cursor: 'pointer' }}>Ver todas →</span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 10 }}>
          <SongHCard title="Determinada Decisão" cat="Fé e Conversão" tom="A#" rank="1" />
          <SongHCard title="Estava com Saudade" cat="Adoração" tom="G" rank="2" color="#7b6ca8" />
          <SongHCard title="Me faz novo" cat="Entrega" tom="C" rank="3" color="#8a77b5" />
          <SongHCard title="Converte-me" cat="Fé e Conversão" tom="A" rank="4" color="#9a85c5" />
          <SongHCard title="Glória a Deus" cat="Glória" tom="D" rank="5" color="#a090c0" />
          <SongHCard title="Tu és Santo" cat="Santo" tom="E" rank="6" />
        </div>
      </div>

      {/* Categorias rápidas */}
      <div>
        <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: 12 }}>
          <h3 style={{ margin: 0, fontSize: 16, fontWeight: 800, color: BRAND.text, letterSpacing: -0.3 }}>Explorar por categoria</h3>
        </div>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <CatChip label="Adoração" count="31" active />
          <CatChip label="Entrada" count="22" />
          <CatChip label="Comunhão" count="28" />
          <CatChip label="Entrega" count="30" />
          <CatChip label="Maria" count="18" />
          <CatChip label="Acolhida" count="35" />
          <CatChip label="Glória" count="12" />
          <CatChip label="Tempo Comum" count="79" />
          <CatChip label="Advento" count="16" />
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// CATEGORIA ABERTA — grid denso com filtros
// ═══════════════════════════════════════════════════════════════
const CAT_SONGS = [
  { title: 'Determinada Decisão', author: 'Juninho Casimiro', tom: 'A#', views: 44 },
  { title: 'Converte-me', author: 'Fernanda Brum', tom: 'A', views: 18 },
  { title: 'Caminho, Verdade e Vida', author: 'Comunidade Canção Nova', tom: 'G', views: 15 },
  { title: 'Deixa-te transformar', author: 'Juninho Casimiro', tom: 'C', views: 12 },
  { title: 'Quero te ver', author: 'Gabriel Guedes', tom: 'D', views: 11 },
  { title: 'Renova-me', author: 'Aline Barros', tom: 'F', views: 10 },
  { title: 'Coração de Cristo', author: 'Comunidade Shalom', tom: 'E', views: 9 },
  { title: 'Águas Profundas', author: 'Fernanda Brum', tom: 'A', views: 8 },
  { title: 'Nada além de Ti', author: 'Adriana Arydes', tom: 'G', views: 7 },
  { title: 'Me faz novo', author: 'Gabriel Guedes', tom: 'C', views: 19 },
  { title: 'Estou aqui', author: 'Adhemar de Campos', tom: 'B', views: 6 },
  { title: 'Tomar a cruz', author: 'Comunidade Shalom', tom: 'D', views: 5 },
];

function CatSongRow({ s, rank, myTom }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '40px 1fr 180px 90px 90px 220px', gap: 14, alignItems: 'center', padding: '11px 16px', background: BRAND.surface, border: `1px solid ${BRAND.border}`, borderRadius: 10, marginBottom: 4, cursor: 'pointer' }}>
      <span style={{ fontSize: 12, fontWeight: 700, color: BRAND.muted, textAlign: 'center' }}>{rank}</span>
      <div>
        <div style={{ fontSize: 13.5, fontWeight: 700, color: BRAND.text, letterSpacing: -0.1 }}>{s.title}</div>
      </div>
      <div style={{ fontSize: 12, color: BRAND.muted, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{s.author}</div>
      <span style={{ fontSize: 10.5, fontWeight: 800, color: BRAND.accent, background: BRAND.accentBg, border: `1px solid ${BRAND.accentBorder}`, borderRadius: 99, padding: '3px 9px', justifySelf: 'start' }}>{s.tom}</span>
      <div style={{ display: 'flex', alignItems: 'center', gap: 4, color: BRAND.muted, fontSize: 11 }}>
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke={BRAND.muted} strokeWidth="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
        <span>{s.views}</span>
      </div>
      <div style={{ display: 'flex', gap: 6, justifySelf: 'end', alignItems: 'center' }}>
        <button style={{ padding: '6px 11px', borderRadius: 99, background: BRAND.primaryLight, border: 'none', color: BRAND.primary, fontSize: 11.5, fontWeight: 700, cursor: 'pointer' }}>+ Repertório</button>
        <button style={{ width: 30, height: 30, borderRadius: 99, background: BRAND.primary, border: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>{Icons.play('#fff')}</button>
        <button title="Renomear · Copiar · Mover · Excluir (owner)" style={{ width: 30, height: 30, borderRadius: 99, background: 'transparent', border: `1px solid ${BRAND.border}`, color: BRAND.muted, fontSize: 14, fontWeight: 800, cursor: 'pointer' }}>⋯</button>
      </div>
    </div>
  );
}

function DesktopCategoryContent() {
  return (
    <div style={{ flex: 1, overflow: 'auto', padding: '28px 36px 40px', background: BRAND.bg }}>
      {/* Breadcrumb + title */}
      <div style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11.5, color: BRAND.muted, marginBottom: 6 }}>
          <span style={{ cursor: 'pointer' }}>Início</span>
          {Icons2.chevronRight(BRAND.muted)}
          <span style={{ cursor: 'pointer' }}>Ministração</span>
          {Icons2.chevronRight(BRAND.muted)}
          <span style={{ fontWeight: 700, color: BRAND.primary }}>Fé e Conversão</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between' }}>
          <div>
            <h1 style={{ margin: 0, fontSize: 30, fontWeight: 800, color: BRAND.text, letterSpacing: -0.6, lineHeight: 1.1 }}>Fé e Conversão</h1>
            <div style={{ fontSize: 13.5, color: BRAND.muted, marginTop: 6 }}><b style={{ color: BRAND.primary }}>{CAT_SONGS.length}</b> músicas · última atualização há 3 dias</div>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <button style={{ padding: '8px 14px', borderRadius: 99, background: BRAND.surface, border: `1.5px solid ${BRAND.border}`, color: BRAND.text, fontSize: 12.5, fontWeight: 700, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}>
              {Icons2.plusBold(BRAND.primary)} Nova música
            </button>
          </div>
        </div>
      </div>

      {/* Filters row */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16, padding: '12px 16px', background: BRAND.surface, border: `1px solid ${BRAND.border}`, borderRadius: 12 }}>
        <span style={{ fontSize: 11, fontWeight: 800, letterSpacing: 1.2, textTransform: 'uppercase', color: BRAND.muted }}>Filtrar</span>
        <div style={{ width: 1, height: 16, background: BRAND.border }} />
        <button style={{ padding: '5px 12px', borderRadius: 99, background: BRAND.primary, color: '#fff', border: 'none', fontSize: 11.5, fontWeight: 700, cursor: 'pointer' }}>Todas</button>
        <button style={{ padding: '5px 12px', borderRadius: 99, background: 'transparent', color: BRAND.muted, border: `1px solid ${BRAND.border}`, fontSize: 11.5, fontWeight: 600, cursor: 'pointer' }}>Meu tom</button>
        <button style={{ padding: '5px 12px', borderRadius: 99, background: 'transparent', color: BRAND.muted, border: `1px solid ${BRAND.border}`, fontSize: 11.5, fontWeight: 600, cursor: 'pointer' }}>Recentes</button>
        <div style={{ flex: 1 }} />
        <span style={{ fontSize: 11, fontWeight: 600, color: BRAND.muted }}>Ordenar:</span>
        <select style={{ padding: '5px 10px', borderRadius: 99, background: BRAND.surface, border: `1px solid ${BRAND.border}`, color: BRAND.text, fontSize: 11.5, fontWeight: 600, fontFamily: 'inherit', cursor: 'pointer', outline: 'none' }}>
          <option>Mais tocadas</option>
          <option>A - Z</option>
          <option>Recém-adicionadas</option>
        </select>
      </div>

      {/* Column header */}
      <div style={{ display: 'grid', gridTemplateColumns: '40px 1fr 180px 90px 90px 180px', gap: 14, padding: '0 16px 8px', fontSize: 10, fontWeight: 800, letterSpacing: 1.3, textTransform: 'uppercase', color: BRAND.muted }}>
        <span style={{ textAlign: 'center' }}>#</span>
        <span>Título</span>
        <span>Artista</span>
        <span>Tom</span>
        <span>Views</span>
        <span style={{ textAlign: 'right' }}>Ações</span>
      </div>

      {/* Song rows */}
      <div>
        {CAT_SONGS.map((s, i) => <CatSongRow key={i} s={s} rank={String(i + 1).padStart(2, '0')} />)}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// CIFRA ABERTA — modal/view refinada
// ═══════════════════════════════════════════════════════════════
function CifraLine({ chord, lyric, tag, chorus }) {
  if (tag) {
    const bold = chorus ? 800 : 600;
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, margin: '24px 0 10px' }}>
        <div style={{ width: chorus ? 3 : 2, height: 14, background: '#9a95a8', opacity: chorus ? 1 : 0.7, borderRadius: 1 }} />
        <span style={{ fontFamily: '"Fira Mono", ui-monospace, monospace', fontSize: 9, fontWeight: bold, letterSpacing: 2, textTransform: 'uppercase', color: '#7a7289' }}>{tag}</span>
      </div>
    );
  }
  return (
    <div style={{ marginBottom: 3, fontFamily: '"Fira Mono", ui-monospace, monospace' }}>
      {chord && <div style={{ color: BRAND.primary, fontSize: 16, fontWeight: 900, lineHeight: 1.45, letterSpacing: 0.3, whiteSpace: 'pre' }}>{chord}</div>}
      {lyric && <div style={{ color: '#0f1419', fontSize: 16, fontWeight: 700, lineHeight: 1.45, whiteSpace: 'pre' }}>{lyric}</div>}
    </div>
  );
}

function DesktopCifraContent() {
  return (
    <div style={{ flex: 1, overflow: 'hidden', background: '#fff', display: 'flex', flexDirection: 'column' }}>
      {/* Breadcrumb + title bar */}
      <div style={{ padding: '20px 36px 12px', borderBottom: `1px solid #ebe8f0`, background: '#fff', flexShrink: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, color: BRAND.muted, marginBottom: 6 }}>
          <span>Ministração</span>{Icons2.chevronRight(BRAND.muted)}
          <span>Fé e Conversão</span>{Icons2.chevronRight(BRAND.muted)}
          <span style={{ fontWeight: 700, color: BRAND.primary }}>Determinada Decisão</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 24 }}>
          <div>
            <h1 style={{ margin: 0, fontSize: 28, fontWeight: 800, color: BRAND.text, letterSpacing: -0.5, lineHeight: 1.1 }}>Determinada Decisão</h1>
            <div style={{ fontSize: 13, color: BRAND.muted, marginTop: 4 }}>Juninho Casimiro · 44 visualizações</div>
          </div>

          {/* Top action row */}
          <div style={{ display: 'flex', gap: 8, flexShrink: 0, alignItems: 'center' }}>
            <button style={{ padding: '8px 14px', borderRadius: 99, background: BRAND.surface, border: `1.5px solid ${BRAND.border}`, color: BRAND.text, fontSize: 12, fontWeight: 700, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}>
              {Icons.plus(BRAND.primary)} Repertório
            </button>
            <button style={{ padding: '8px 14px', borderRadius: 99, background: BRAND.surface, border: `1.5px solid ${BRAND.border}`, color: BRAND.text, fontSize: 12, fontWeight: 700, cursor: 'pointer' }}>PDF</button>
            <button style={{ padding: '8px 14px', borderRadius: 99, background: BRAND.surface, border: `1.5px solid ${BRAND.border}`, color: BRAND.text, fontSize: 12, fontWeight: 700, cursor: 'pointer' }}>Doc</button>
            <button style={{ padding: '8px 16px', borderRadius: 99, background: BRAND.primary, border: 'none', color: '#fff', fontSize: 12, fontWeight: 800, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6, boxShadow: '0 2px 8px rgba(91,75,138,.28)' }}>
              {Icons.play('#fff')} Apresentar
            </button>

            {/* Owner-only cluster */}
            <div style={{ width: 1, height: 22, background: BRAND.border, margin: '0 4px' }} />
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '3px 8px 3px 6px', borderRadius: 99, background: '#fef7e6', border: `1px solid ${BRAND.accentBorder}` }}>
              <span style={{ fontSize: 9, fontWeight: 800, letterSpacing: 1.2, textTransform: 'uppercase', color: BRAND.accent, padding: '2px 7px', background: '#fff', borderRadius: 99, border: `1px solid ${BRAND.accentBorder}` }}>owner</span>
              <button title="Editar metadados" style={{ padding: '6px 10px', borderRadius: 99, background: 'transparent', border: 'none', color: BRAND.text, fontSize: 11.5, fontWeight: 700, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4 }}>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>
                Metadados
              </button>
              <button title="Editar cifra" style={{ padding: '6px 10px', borderRadius: 99, background: 'transparent', border: 'none', color: BRAND.text, fontSize: 11.5, fontWeight: 700, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4 }}>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>
                Editar
              </button>
              <button title="Salvar tom atual como canônico" style={{ padding: '6px 10px', borderRadius: 99, background: 'transparent', border: 'none', color: BRAND.text, fontSize: 11.5, fontWeight: 700, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4 }}>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 18V6l12-2v12"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
                Salvar tom
              </button>
            </div>
            <button title="Mais opções" style={{ width: 34, height: 34, borderRadius: 99, background: BRAND.surface, border: `1.5px solid ${BRAND.border}`, color: BRAND.muted, fontSize: 16, fontWeight: 800, cursor: 'pointer' }}>⋯</button>
          </div>
        </div>

        {/* Transposição bar */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginTop: 16, padding: '11px 14px', background: '#faf9fc', border: `1px solid #ebe8f0`, borderRadius: 12 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 10.5, fontWeight: 800, letterSpacing: 1.3, textTransform: 'uppercase', color: BRAND.muted }}>Tom</span>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, background: BRAND.surface, border: `1px solid ${BRAND.border}`, borderRadius: 99, padding: '3px 4px' }}>
              <button style={{ width: 24, height: 24, borderRadius: 99, border: 'none', background: 'transparent', color: BRAND.text, fontSize: 14, fontWeight: 800, cursor: 'pointer' }}>−</button>
              <span style={{ fontSize: 13, fontWeight: 800, color: BRAND.primary, minWidth: 24, textAlign: 'center' }}>A#</span>
              <button style={{ width: 24, height: 24, borderRadius: 99, border: 'none', background: 'transparent', color: BRAND.text, fontSize: 14, fontWeight: 800, cursor: 'pointer' }}>+</button>
            </div>
            <span style={{ fontSize: 11, color: BRAND.muted }}>original</span>
          </div>
          <div style={{ width: 1, height: 20, background: BRAND.border }} />
          <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            {['C', 'D', 'E', 'F', 'G', 'A', 'B'].map(n => (
              <button key={n} style={{ width: 30, height: 30, borderRadius: 99, border: n === 'A' ? `1.5px solid ${BRAND.primary}` : `1px solid ${BRAND.border}`, background: n === 'A' ? BRAND.primaryLight : BRAND.surface, color: n === 'A' ? BRAND.primary : BRAND.text, fontSize: 11.5, fontWeight: 700, cursor: 'pointer' }}>{n}</button>
            ))}
          </div>
          <div style={{ flex: 1 }} />
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ fontSize: 10.5, fontWeight: 800, letterSpacing: 1.3, textTransform: 'uppercase', color: BRAND.muted }}>Zoom</span>
            <button style={{ width: 28, height: 28, borderRadius: 8, border: `1px solid ${BRAND.border}`, background: BRAND.surface, color: BRAND.text, fontSize: 12, fontWeight: 800, cursor: 'pointer' }}>A−</button>
            <button style={{ width: 28, height: 28, borderRadius: 8, border: `1px solid ${BRAND.border}`, background: BRAND.surface, color: BRAND.text, fontSize: 13, fontWeight: 800, cursor: 'pointer' }}>A+</button>
          </div>
          <button style={{ padding: '6px 12px', borderRadius: 99, border: `1px solid ${BRAND.border}`, background: BRAND.surface, color: BRAND.muted, fontSize: 11, fontWeight: 700, cursor: 'pointer' }}>Meu tom</button>
          <div style={{ width: 1, height: 20, background: BRAND.border }} />
          <button title="Alternar 2 colunas" style={{ padding: '6px 10px', borderRadius: 8, border: `1px solid ${BRAND.border}`, background: BRAND.surface, color: BRAND.text, fontSize: 11.5, fontWeight: 700, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 5 }}>
            <svg width="14" height="11" viewBox="0 0 14 11" fill="currentColor"><rect x="0" y="0" width="6" height="11" rx="1.5"/><rect x="8" y="0" width="6" height="11" rx="1.5"/></svg>
            2 col
          </button>
          <button title="Rolagem automática" style={{ padding: '6px 10px', borderRadius: 8, border: `1px solid ${BRAND.border}`, background: BRAND.surface, color: BRAND.text, fontSize: 11.5, fontWeight: 700, cursor: 'pointer' }}>⇅ Auto</button>
        </div>
      </div>

      {/* Cifra body */}
      <div style={{ flex: 1, overflow: 'auto', padding: '28px 36px 40px', display: 'flex', justifyContent: 'center' }}>
        <div style={{ maxWidth: 880, width: '100%' }}>
          <CifraLine tag="Intro" />
          <CifraLine chord="A#        D#        Fm" lyric="" />

          <CifraLine tag="1ª Parte" />
          <CifraLine chord="A#                        D#" lyric="Tomei a decisão de te servir" />
          <CifraLine chord="Fm                      A#" lyric="De entregar o que sou, o que tenho" />
          <CifraLine chord="D#                      Cm" lyric="A Ti meu coração eu rendo" />
          <CifraLine chord="Fm                     A#" lyric="E sei que a Ti pertenço" />

          <CifraLine tag="Pré-Refrão" />
          <CifraLine chord="D#              Fm" lyric="Por Teu amor tão grande" />
          <CifraLine chord="A#            Cm" lyric="Escolho caminhar" />

          <CifraLine tag="Refrão" chorus />
          <CifraLine chord="A#          D#" lyric="Determinada decisão" />
          <CifraLine chord="Fm              A#" lyric="É viver em Tua presença" />
          <CifraLine chord="D#            Cm" lyric="Seguir Teus passos, Senhor" />
          <CifraLine chord="Fm           A#" lyric="Com toda minha força" />

          <CifraLine tag="2ª Parte" />
          <CifraLine chord="A#                      D#" lyric="Não importa o caminho a seguir" />
          <CifraLine chord="Fm                    A#" lyric="Contigo quero andar" />
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// Screens wrappers
// ═══════════════════════════════════════════════════════════════
function DesktopHomeScreen() {
  return (
    <DesktopFrame>
      <DesktopTopBar />
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        <DesktopLeftSidebar activeCat={null} />
        <DesktopHomeContent />
        <DesktopRightRep />
      </div>
    </DesktopFrame>
  );
}

function DesktopCategoryScreen() {
  return (
    <DesktopFrame>
      <DesktopTopBar />
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        <DesktopLeftSidebar />
        <DesktopCategoryContent />
        <DesktopRightRep />
      </div>
    </DesktopFrame>
  );
}

function DesktopCifraScreen() {
  return (
    <DesktopFrame>
      <DesktopTopBar />
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        <DesktopLeftSidebar />
        <DesktopCifraContent />
        <DesktopRightRep />
      </div>
    </DesktopFrame>
  );
}

Object.assign(window, { DesktopHomeScreen, DesktopCategoryScreen, DesktopCifraScreen, DesktopFrame });
