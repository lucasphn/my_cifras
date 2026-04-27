// ──────────────────────────────────────────────────────────────
// My Cifras — Home Mobile · REFINAMENTO
// Diretrizes:
//   · Busca é protagonista (usuário abre pra buscar)
//   · Liturgia é secundária — compacta
//   · Eventos: visualizar + criar (CTA claro)
//   · Sanduíche: várias direções exploradas
//   · Citação: versões compactas e versões ausentes
// ──────────────────────────────────────────────────────────────

// ── Extra icons ──
const Icons2 = {
  menu: (c) => (
    <svg width="22" height="22" viewBox="0 0 22 22" fill="none" stroke={c} strokeWidth="2" strokeLinecap="round"><path d="M3 6h16M3 11h16M3 16h16"/></svg>
  ),
  bell: (c) => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 16v-5a6 6 0 0 0-12 0v5l-2 2v1h16v-1z"/><path d="M10 20a2 2 0 0 0 4 0"/></svg>
  ),
  calendar: (c) => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 9h18M8 3v4M16 3v4"/></svg>
  ),
  sparkle: (c) => (
    <svg width="16" height="16" viewBox="0 0 16 16" fill={c}><path d="M8 1l1.5 4.5L14 7l-4.5 1.5L8 13l-1.5-4.5L2 7l4.5-1.5z"/></svg>
  ),
  arrow: (c) => (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke={c} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 7h8M8 3l4 4-4 4"/></svg>
  ),
  book: (c) => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M4 4h6a3 3 0 0 1 3 3v13a2 2 0 0 0-2-2H4zM20 4h-6a3 3 0 0 0-3 3v13a2 2 0 0 1 2-2h7z"/></svg>
  ),
  plusBold: (c) => (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke={c} strokeWidth="2.5" strokeLinecap="round"><path d="M7 2v10M2 7h10"/></svg>
  ),
  clock: (c) => (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>
  ),
  chevronRight: (c) => (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke={c} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 3l4 4-4 4"/></svg>
  ),
  settings: (c) => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
  ),
  xCircle: (c) => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="9"/><path d="M9 9l6 6M15 9l-6 6"/></svg>
  ),
};

// Tag tom litúrgico
const LITURGY = {
  branco: { bg: '#f8f6ee', border: '#e8dfb3', dot: '#f4e9b8', text: '#8a7a3a', label: 'Branco' },
  roxo:   { bg: '#f0ecf5', border: '#d5c7e4', dot: '#9c7fc7', text: '#5b4b8a', label: 'Roxo' },
  verde:  { bg: '#eff5ec', border: '#c9dcc0', dot: '#7ba968', text: '#3f6930', label: 'Verde' },
  vermelho: { bg: '#f7ecec', border: '#e2c0c0', dot: '#c45b5b', text: '#8a3a3a', label: 'Vermelho' },
  rosa:   { bg: '#f7eef2', border: '#e4c8d3', dot: '#d99ab5', text: '#8a4a65', label: 'Rosa' },
};

function LiturgyDot({ kind = 'branco', size = 10 }) {
  const l = LITURGY[kind];
  return <span style={{ display: 'inline-block', width: size, height: size, borderRadius: 99, background: l.dot, border: `1px solid ${l.border}`, flexShrink: 0 }} />;
}

// ═══════════════════════════════════════════════════════════════
// Header v2 — Busca em destaque + avatar à direita
// Variantes: com ou sem sanduíche; com ou sem toggle
// ═══════════════════════════════════════════════════════════════
function HeaderSearch({ variant = 'menu' }) {
  // variant: 'menu' (hamburger à esquerda + avatar), 'logo' (logo à esquerda + menu à direita)
  const showMenu = variant === 'menu';
  return (
    <div style={{ padding: '8px 12px 12px', background: BRAND.surface, borderBottom: `1px solid ${BRAND.border}`, flexShrink: 0 }}>
      {/* Top row: menu + brand + avatar */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
        {showMenu && (
          <button style={{ width: 38, height: 38, borderRadius: 10, border: 'none', background: 'transparent', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 0 }}>
            {Icons2.menu(BRAND.text)}
          </button>
        )}
        <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{ width: 26, height: 26, borderRadius: 7, background: BRAND.primary, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M9 18V6l12-2v12"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
          </div>
          <span style={{ fontSize: 15, fontWeight: 800, color: BRAND.text, letterSpacing: -0.2 }}>My Cifras</span>
        </div>
        <button style={{ width: 34, height: 34, borderRadius: 99, border: 'none', background: BRAND.surface2, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 0, position: 'relative' }}>
          {Icons2.bell(BRAND.text)}
          <span style={{ position: 'absolute', top: 6, right: 6, width: 8, height: 8, borderRadius: 99, background: BRAND.accent, border: `2px solid ${BRAND.surface2}` }} />
        </button>
        <div style={{ width: 34, height: 34, borderRadius: 99, background: BRAND.primary, color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 13, fontWeight: 700 }}>L</div>
      </div>

      {/* Search bar */}
      <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
        <div style={{ position: 'absolute', left: 14, color: BRAND.muted, display: 'flex' }}>{Icons.search(BRAND.muted)}</div>
        <input placeholder="Buscar música, artista ou trecho..." style={{ flex: 1, padding: '12px 100px 12px 44px', borderRadius: 99, border: `1.5px solid ${BRAND.border}`, background: BRAND.bg, fontSize: 13.5, fontWeight: 500, color: BRAND.text, outline: 'none', fontFamily: 'inherit' }} />
        {/* Segmented toggle inside search */}
        <div style={{ position: 'absolute', right: 6, display: 'flex', background: BRAND.surface2, borderRadius: 99, padding: 2 }}>
          <button style={{ padding: '5px 10px', borderRadius: 99, border: 'none', background: BRAND.primary, color: '#fff', fontSize: 11, fontWeight: 700 }}>Nome</button>
          <button style={{ padding: '5px 10px', borderRadius: 99, border: 'none', background: 'transparent', color: BRAND.muted, fontSize: 11, fontWeight: 600 }}>Letra</button>
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// Compact Liturgy row — uma linha com dot + data + festa
// ═══════════════════════════════════════════════════════════════
function LiturgyCompact({ kind = 'branco', festa = '2ª feira da 3ª Semana da Páscoa', dataStr = 'Seg, 20 abr' }) {
  const l = LITURGY[kind];
  return (
    <button style={{ width: '100%', display: 'flex', alignItems: 'center', gap: 10, padding: '10px 14px', background: l.bg, border: `1px solid ${l.border}`, borderRadius: 12, textAlign: 'left', cursor: 'pointer' }}>
      <LiturgyDot kind={kind} size={12} />
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 6 }}>
          <span style={{ fontSize: 10.5, fontWeight: 800, letterSpacing: 1.2, textTransform: 'uppercase', color: l.text }}>{l.label}</span>
          <span style={{ fontSize: 10.5, color: BRAND.muted }}>· {dataStr}</span>
        </div>
        <div style={{ fontSize: 12, fontWeight: 600, color: BRAND.text, marginTop: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{festa}</div>
      </div>
      {Icons2.chevronRight(BRAND.muted)}
    </button>
  );
}

// ═══════════════════════════════════════════════════════════════
// Section header compacto
// ═══════════════════════════════════════════════════════════════
function SectionHeader({ title, cta, ctaLabel = 'Ver tudo' }) {
  return (
    <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: 10 }}>
      <h3 style={{ margin: 0, fontSize: 14, fontWeight: 800, color: BRAND.text, letterSpacing: -0.2 }}>{title}</h3>
      {cta && <span style={{ fontSize: 11.5, fontWeight: 700, color: BRAND.primary, display: 'flex', alignItems: 'center', gap: 3 }}>{ctaLabel} →</span>}
    </div>
  );
}

// Horizontal scrolling song row (card pequeno quadrado)
// Hierarquia: título > artista/banda (opcional) > categoria · tom (pílula pequena)
function SongHCard({ title, cat, tom, rank, author, color = BRAND.primary }) {
  return (
    <div style={{ width: 148, flexShrink: 0, background: BRAND.surface, border: `1.5px solid ${BRAND.border}`, borderRadius: 12, padding: 11, boxShadow: '0 1px 3px rgba(60,40,100,.05)', display: 'flex', flexDirection: 'column', minHeight: 132 }}>
      {/* Thumb compacto com símbolo musical + rank sutil */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 9 }}>
        <div style={{ width: 28, height: 28, borderRadius: 8, background: `linear-gradient(135deg, ${color}, ${BRAND.primaryHover})`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M9 18V6l12-2v12"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
        </div>
        {rank && <span style={{ fontSize: 9.5, fontWeight: 800, color: BRAND.muted, letterSpacing: 0.3 }}>#{rank}</span>}
      </div>

      {/* Título (protagonista) */}
      <div style={{ fontSize: 13, fontWeight: 700, color: BRAND.text, lineHeight: 1.2, letterSpacing: -0.15, flex: 1, overflow: 'hidden', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>{title}</div>

      {/* Artista (opcional) */}
      {author && <div style={{ fontSize: 10, color: BRAND.muted, marginTop: 3, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{author}</div>}

      {/* Meta bar: categoria + pílula de tom (pequena, como metadado) */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 7, gap: 6 }}>
        <span style={{ fontSize: 9.5, color: BRAND.muted, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', flex: 1, minWidth: 0 }}>{cat}</span>
        <span style={{ fontSize: 9.5, fontWeight: 800, color: BRAND.accent, background: BRAND.accentBg, border: `1px solid ${BRAND.accentBorder}`, borderRadius: 99, padding: '1px 7px', flexShrink: 0 }}>{tom}</span>
      </div>
    </div>
  );
}

// Categoria chip (horizontal scroll)
function CatChip({ label, count, active, color = BRAND.primary }) {
  return (
    <button style={{ flexShrink: 0, padding: '8px 12px', borderRadius: 99, background: active ? color : BRAND.surface, border: `1.5px solid ${active ? color : BRAND.border}`, color: active ? '#fff' : BRAND.text, fontSize: 12, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
      {label}
      <span style={{ fontSize: 10, fontWeight: 700, color: active ? 'rgba(255,255,255,.8)' : BRAND.muted, background: active ? 'rgba(255,255,255,.18)' : BRAND.surface2, padding: '1px 6px', borderRadius: 99 }}>{count}</span>
    </button>
  );
}

// Evento
function EventCard({ day, month, title, time, type, liturgy }) {
  return (
    <div style={{ display: 'flex', gap: 11, padding: '11px 12px', background: BRAND.surface, border: `1.5px solid ${BRAND.border}`, borderRadius: 12, alignItems: 'center' }}>
      <div style={{ width: 44, borderRadius: 10, background: BRAND.primaryLight, display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '7px 0', flexShrink: 0 }}>
        <span style={{ fontSize: 17, fontWeight: 800, color: BRAND.primary, letterSpacing: -0.5, lineHeight: 1 }}>{day}</span>
        <span style={{ fontSize: 9, fontWeight: 700, letterSpacing: 0.8, textTransform: 'uppercase', color: BRAND.primary, marginTop: 2 }}>{month}</span>
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 5, marginBottom: 2 }}>
          {liturgy && <LiturgyDot kind={liturgy} size={7} />}
          <span style={{ fontSize: 9.5, fontWeight: 800, letterSpacing: 1.2, textTransform: 'uppercase', color: BRAND.muted }}>{type}</span>
        </div>
        <div style={{ fontSize: 13, fontWeight: 700, color: BRAND.text, letterSpacing: -0.1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{title}</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginTop: 3, color: BRAND.muted }}>
          {Icons2.clock(BRAND.muted)}
          <span style={{ fontSize: 10.5 }}>{time}</span>
        </div>
      </div>
    </div>
  );
}

function EventEmptyCompact() {
  return (
    <button style={{ width: '100%', display: 'flex', alignItems: 'center', gap: 11, padding: '12px 13px', background: BRAND.surface, border: `1.5px dashed ${BRAND.border}`, borderRadius: 12, cursor: 'pointer', textAlign: 'left' }}>
      <div style={{ width: 40, height: 40, borderRadius: 10, background: BRAND.primaryLight, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
        {Icons2.plusBold(BRAND.primary)}
      </div>
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: 12.5, fontWeight: 700, color: BRAND.text }}>Nenhum evento próximo</div>
        <div style={{ fontSize: 11, color: BRAND.muted, marginTop: 1 }}>Toque para adicionar um ensaio ou missa</div>
      </div>
    </button>
  );
}

// ═══════════════════════════════════════════════════════════════
// H1 — BUSCA PROTAGONISTA
// Header alto e generoso · liturgia em 1 linha compacta
// · "Recentes" (continuar de onde parou) · agenda em 1-2 cards
// · Mais tocadas abaixo
// ═══════════════════════════════════════════════════════════════
function H1_SearchFirst() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', background: BRAND.bg }}>
      <HeaderSearch variant="menu" />
      <div style={{ flex: 1, overflow: 'auto', padding: '12px 14px 90px' }}>
        {/* Liturgia compacta */}
        <LiturgyCompact kind="branco" />

        {/* Recentes (1ª prioridade depois da busca) */}
        <div style={{ marginTop: 18 }}>
          <SectionHeader title="Continue de onde parou" cta />
          <div style={{ display: 'flex', gap: 8, overflowX: 'auto', paddingBottom: 4, margin: '0 -14px', padding: '0 14px 4px' }}>
            <SongHCard title="Determinada Decisão" cat="Fé e Conversão" tom="A#" rank="1" author="Juninho Casimiro" />
            <SongHCard title="Estava com Saudade de Ti" cat="Adoração" tom="G" rank="2" author="Diante do Trono" />
            <SongHCard title="Me faz novo" cat="Entrega" tom="C" rank="3" color="#7b6ca8" author="Gabriel Guedes" />
          </div>
        </div>

        {/* Próximos eventos */}
        <div style={{ marginTop: 20 }}>
          <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: 10 }}>
            <h3 style={{ margin: 0, fontSize: 14, fontWeight: 800, color: BRAND.text, letterSpacing: -0.2 }}>Próximos eventos</h3>
            <button style={{ background: 'none', border: 'none', fontSize: 11.5, fontWeight: 700, color: BRAND.primary, padding: 0, display: 'flex', alignItems: 'center', gap: 3 }}>+ Novo</button>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            <EventCard day="20" month="ABR" title="Missa Dominical 10h" time="10:00 · Dia todo" type="Missa" liturgy="branco" />
            <EventCard day="22" month="ABR" title="Ensaio grupo de louvor" time="19:30 — 21:30" type="Ensaio" />
          </div>
        </div>

        {/* Categorias rápidas */}
        <div style={{ marginTop: 20 }}>
          <SectionHeader title="Navegar por categoria" cta ctaLabel="Todas" />
          <div style={{ display: 'flex', gap: 6, overflowX: 'auto', margin: '0 -14px', padding: '0 14px 4px' }}>
            <CatChip label="Adoração" count="31" active />
            <CatChip label="Entrada" count="22" />
            <CatChip label="Comunhão" count="28" />
            <CatChip label="Entrega" count="30" />
            <CatChip label="Maria" count="18" />
          </div>
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// H2 — PRIMEIRA DOBRA COMPLETA
// Tudo essencial cabe sem scroll: busca + liturgia compacta
// + agenda compacta + ações rápidas + 2 mais tocadas
// Citação aparece PEQUENA no final como easter egg
// ═══════════════════════════════════════════════════════════════
function H2_DenseAboveFold() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', background: BRAND.bg }}>
      <HeaderSearch variant="menu" />
      <div style={{ flex: 1, overflow: 'auto', padding: '10px 14px 90px' }}>
        {/* Top row: liturgia compacta */}
        <LiturgyCompact kind="branco" />

        {/* Quick actions 4-up */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 6, marginTop: 10 }}>
          {[
            { label: 'Abrir\nrepertório', icon: Icons.playlist, color: BRAND.primary },
            { label: 'Apresentar', icon: Icons.play, color: '#6d5ba5' },
            { label: 'Importar\ncifra', icon: Icons2.plusBold, color: '#8270b8' },
            { label: 'Agenda', icon: Icons2.calendar, color: '#9a85c5' },
          ].map((a, i) => (
            <button key={i} style={{ background: BRAND.surface, border: `1.5px solid ${BRAND.border}`, borderRadius: 12, padding: '10px 6px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 5, cursor: 'pointer' }}>
              <div style={{ width: 30, height: 30, borderRadius: 8, background: a.color, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                {a.icon('#fff', true)}
              </div>
              <span style={{ fontSize: 9.5, fontWeight: 700, color: BRAND.text, lineHeight: 1.2, textAlign: 'center', whiteSpace: 'pre-line' }}>{a.label}</span>
            </button>
          ))}
        </div>

        {/* Próximo evento (1 card grande) */}
        <div style={{ marginTop: 14 }}>
          <SectionHeader title="Próximo evento" cta ctaLabel="Agenda" />
          <EventCard day="20" month="ABR" title="Missa Dominical — Paróquia São José" time="10:00 · Hoje" type="Missa" liturgy="branco" />
        </div>

        {/* Mais tocadas grid 2x1 compacto */}
        <div style={{ marginTop: 14 }}>
          <SectionHeader title="Recentes" cta />
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 7 }}>
            <SongHCard title="Determinada Decisão" cat="Fé e Conversão" tom="A#" rank="1" />
            <SongHCard title="Estava com Saudade" cat="Adoração" tom="G" rank="2" color="#7b6ca8" />
          </div>
        </div>

        {/* Tiny quote footer */}
        <div style={{ marginTop: 16, padding: '11px 13px', background: 'transparent', borderLeft: `2px solid ${BRAND.accent}`, display: 'flex', gap: 8, alignItems: 'flex-start' }}>
          <div style={{ marginTop: 2 }}>{Icons2.sparkle(BRAND.accent)}</div>
          <div>
            <div style={{ fontSize: 11.5, color: BRAND.text, fontStyle: 'italic', lineHeight: 1.4 }}>"O canto exige, acima de tudo, uma profunda vida espiritual"</div>
            <div style={{ fontSize: 9.5, fontWeight: 700, letterSpacing: 0.8, color: BRAND.muted, marginTop: 3, textTransform: 'uppercase' }}>Papa Leão XIV</div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// H3 — CATEGORIAS NA HOME (sanduíche vira menu de conta)
// Chips horizontais de categoria como 1ª coisa depois da busca
// · sanduíche agora abre perfil/config/logout (não categorias)
// · Sem citação
// ═══════════════════════════════════════════════════════════════
function H3_CategoryChipsHome() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', background: BRAND.bg }}>
      <HeaderSearch variant="menu" />
      <div style={{ flex: 1, overflow: 'auto', padding: '12px 0 90px' }}>
        {/* Horizontal chips */}
        <div style={{ padding: '0 14px' }}>
          <div style={{ fontSize: 10.5, fontWeight: 800, letterSpacing: 1.3, textTransform: 'uppercase', color: BRAND.muted, marginBottom: 8 }}>Categorias</div>
        </div>
        <div style={{ display: 'flex', gap: 6, overflowX: 'auto', padding: '0 14px 4px' }}>
          <CatChip label="Todas" count="473" active />
          <CatChip label="Adoração" count="31" />
          <CatChip label="Entrada" count="22" />
          <CatChip label="Comunhão" count="28" />
          <CatChip label="Entrega" count="30" />
          <CatChip label="Fé" count="20" />
          <CatChip label="Maria" count="18" />
        </div>

        {/* Ministração header + grid */}
        <div style={{ padding: '14px 14px 0' }}>
          <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: 10 }}>
            <div>
              <h3 style={{ margin: 0, fontSize: 14, fontWeight: 800, color: BRAND.text, letterSpacing: -0.2 }}>Sugeridas pra você</h3>
              <div style={{ fontSize: 11, color: BRAND.muted, marginTop: 2 }}>Baseado em Adoração · seu uso mais recente</div>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
            <SongHCard title="Determinada Decisão" cat="Fé e Conversão" tom="A#" rank="1" />
            <SongHCard title="Estava com Saudade" cat="Adoração" tom="G" rank="2" color="#7b6ca8" />
            <SongHCard title="Me faz novo" cat="Entrega" tom="C" rank="3" color="#8a77b5" />
            <SongHCard title="Converte-me" cat="Fé" tom="A" rank="4" color="#9a85c5" />
          </div>
        </div>

        {/* Liturgia + próximo evento em grid de 2 */}
        <div style={{ padding: '18px 14px 0', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
          <button style={{ background: LITURGY.branco.bg, border: `1px solid ${LITURGY.branco.border}`, borderRadius: 12, padding: '11px 12px', textAlign: 'left', cursor: 'pointer' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 5, marginBottom: 6 }}>
              <LiturgyDot kind="branco" size={9} />
              <span style={{ fontSize: 9.5, fontWeight: 800, letterSpacing: 1.2, textTransform: 'uppercase', color: LITURGY.branco.text }}>Liturgia · Branco</span>
            </div>
            <div style={{ fontSize: 12, fontWeight: 700, color: BRAND.text, lineHeight: 1.3, letterSpacing: -0.1 }}>2ª feira, 3ª sem. da Páscoa</div>
            <div style={{ fontSize: 10.5, color: BRAND.muted, marginTop: 4, display: 'flex', alignItems: 'center', gap: 4 }}>
              {Icons2.book(BRAND.muted)} Textos do dia
            </div>
          </button>
          <button style={{ background: BRAND.surface, border: `1.5px solid ${BRAND.border}`, borderRadius: 12, padding: '11px 12px', textAlign: 'left', cursor: 'pointer' }}>
            <div style={{ fontSize: 9.5, fontWeight: 800, letterSpacing: 1.2, textTransform: 'uppercase', color: BRAND.muted, marginBottom: 6 }}>Próx. Evento</div>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 6 }}>
              <span style={{ fontSize: 17, fontWeight: 800, color: BRAND.primary, letterSpacing: -0.5, lineHeight: 1 }}>22</span>
              <span style={{ fontSize: 9, fontWeight: 700, letterSpacing: 0.8, color: BRAND.primary }}>ABR</span>
            </div>
            <div style={{ fontSize: 12, fontWeight: 700, color: BRAND.text, marginTop: 4, letterSpacing: -0.1 }}>Ensaio louvor</div>
            <div style={{ fontSize: 10.5, color: BRAND.muted, marginTop: 2 }}>19:30 — 21:30</div>
          </button>
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// H4 — EDITORIAL / WIDGETS
// Design mais card-first, com dois widgets (liturgia grande +
// próximo evento grande) lado a lado, estilo app de produtividade
// Citação compacta no topo com ilustração discreta
// ═══════════════════════════════════════════════════════════════
function H4_EditorialWidgets() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', background: BRAND.bg }}>
      <HeaderSearch variant="menu" />
      <div style={{ flex: 1, overflow: 'auto', padding: '14px 14px 90px' }}>
        {/* Greeting + quote bar */}
        <div style={{ marginBottom: 14 }}>
          <div style={{ fontSize: 18, fontWeight: 800, color: BRAND.text, letterSpacing: -0.4, lineHeight: 1.2 }}>Bom dia, Lucas</div>
          <div style={{ fontSize: 12, color: BRAND.muted, marginTop: 3, display: 'flex', alignItems: 'center', gap: 4 }}>
            {Icons2.sparkle(BRAND.accent)}
            <span style={{ fontStyle: 'italic' }}>"Cantar é orar duas vezes." — S. Agostinho</span>
          </div>
        </div>

        {/* Widget grid 2x */}
        <div style={{ display: 'grid', gridTemplateColumns: '1.1fr 1fr', gap: 8, marginBottom: 14 }}>
          {/* Liturgia widget */}
          <div style={{ background: `linear-gradient(155deg, ${LITURGY.branco.bg}, #fff)`, border: `1px solid ${LITURGY.branco.border}`, borderRadius: 16, padding: '12px 13px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
              <LiturgyDot kind="branco" size={11} />
              <span style={{ fontSize: 9.5, fontWeight: 800, letterSpacing: 1.3, textTransform: 'uppercase', color: LITURGY.branco.text }}>Branco</span>
            </div>
            <div style={{ fontSize: 12.5, fontWeight: 700, color: BRAND.text, lineHeight: 1.3, letterSpacing: -0.1 }}>2ª feira da 3ª Semana da Páscoa</div>
            <div style={{ fontSize: 10.5, color: BRAND.muted, marginTop: 6 }}>Seg, 20 abr · Tempo Pascal</div>
            <div style={{ marginTop: 10, display: 'flex', alignItems: 'center', gap: 5, color: BRAND.primary, fontSize: 11, fontWeight: 700 }}>
              {Icons2.book(BRAND.primary)}
              <span>Ler textos</span>
            </div>
          </div>

          {/* Próximo evento widget */}
          <div style={{ background: BRAND.surface, border: `1.5px solid ${BRAND.border}`, borderRadius: 16, padding: '12px 13px', display: 'flex', flexDirection: 'column' }}>
            <div style={{ fontSize: 9.5, fontWeight: 800, letterSpacing: 1.3, textTransform: 'uppercase', color: BRAND.muted, marginBottom: 8 }}>Próximo</div>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 6 }}>
              <span style={{ fontSize: 28, fontWeight: 800, color: BRAND.primary, letterSpacing: -1, lineHeight: 1 }}>22</span>
              <span style={{ fontSize: 10, fontWeight: 800, letterSpacing: 1, color: BRAND.primary }}>ABR</span>
            </div>
            <div style={{ fontSize: 12.5, fontWeight: 700, color: BRAND.text, marginTop: 6, letterSpacing: -0.1 }}>Ensaio Louvor</div>
            <div style={{ fontSize: 10.5, color: BRAND.muted, marginTop: 3, display: 'flex', alignItems: 'center', gap: 3 }}>
              {Icons2.clock(BRAND.muted)} 19:30
            </div>
            <div style={{ flex: 1 }} />
            <button style={{ marginTop: 10, background: 'transparent', border: 'none', color: BRAND.primary, fontSize: 11, fontWeight: 700, textAlign: 'left', padding: 0, display: 'flex', alignItems: 'center', gap: 3 }}>
              + Adicionar evento
            </button>
          </div>
        </div>

        {/* Recentes — horizontal */}
        <SectionHeader title="Tocadas recentemente" cta />
        <div style={{ display: 'flex', gap: 8, overflowX: 'auto', paddingBottom: 4, margin: '0 -14px 14px', padding: '0 14px 4px' }}>
          <SongHCard title="Determinada Decisão" cat="Fé e Conversão" tom="A#" rank="1" />
          <SongHCard title="Estava com Saudade" cat="Adoração" tom="G" rank="2" color="#7b6ca8" />
          <SongHCard title="Me faz novo" cat="Entrega" tom="C" rank="3" color="#8a77b5" />
          <SongHCard title="Converte-me" cat="Fé" tom="A" rank="4" color="#9a85c5" />
        </div>

        {/* Categorias estilo lista grande */}
        <SectionHeader title="Categorias" cta ctaLabel="Ver todas" />
        <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
          {[
            { label: 'Adoração', count: 31, sec: 'Ministração' },
            { label: 'Entrega', count: 30, sec: 'Ministração' },
            { label: 'Tempo Comum', count: 79, sec: 'Missa' },
          ].map((c, i) => (
            <button key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '10px 12px', background: BRAND.surface, border: `1px solid ${BRAND.border}`, borderRadius: 10, cursor: 'pointer', textAlign: 'left' }}>
              <div style={{ width: 6, height: 32, borderRadius: 3, background: BRAND.primary, flexShrink: 0 }} />
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 12.5, fontWeight: 700, color: BRAND.text }}>{c.label}</div>
                <div style={{ fontSize: 10, color: BRAND.muted, marginTop: 1 }}>{c.sec}</div>
              </div>
              <span style={{ fontSize: 11, fontWeight: 700, color: BRAND.muted, background: BRAND.surface2, padding: '2px 8px', borderRadius: 99 }}>{c.count}</span>
              {Icons2.chevronRight(BRAND.muted)}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// Categorias drawer refinado (abre do sanduíche H1/H2)
// ═══════════════════════════════════════════════════════════════
function DrawerCategorias() {
  const CAT_MIN = [
    { label: 'Acolhida', count: 35 },
    { label: 'Adoração', count: 31 },
    { label: 'Amor de Deus', count: 21 },
    { label: 'Animação', count: 33 },
    { label: 'Comunidade e Vocação', count: 19 },
    { label: 'Cura e Libertação', count: 10 },
    { label: 'Entrega', count: 30 },
    { label: 'Espírito Santo', count: 24 },
    { label: 'Fé e Conversão', count: 20, active: true },
    { label: 'Louvor', count: 7 },
    { label: 'Maria', count: 18 },
    { label: 'Pecado e Salvação', count: 21 },
    { label: 'Vida em Santidade', count: 20 },
  ];
  const CAT_MISSA = [
    { label: 'Tempo Comum', count: 79 },
    { label: 'Quaresma', count: 4 },
    { label: 'Páscoa', count: 6 },
    { label: 'Advento', count: 16 },
  ];
  const CatRow = ({ c, color = BRAND.primary }) => (
    <button style={{ width: '100%', display: 'flex', alignItems: 'center', gap: 10, padding: '8px 4px', background: c.active ? BRAND.primaryLight : 'transparent', borderRadius: 8, border: 'none', cursor: 'pointer', textAlign: 'left' }}>
      <div style={{ width: 3, height: 14, borderRadius: 2, background: c.active ? color : 'transparent', flexShrink: 0 }} />
      <span style={{ flex: 1, fontSize: 12.5, fontWeight: c.active ? 700 : 500, color: c.active ? BRAND.primary : BRAND.text }}>{c.label}</span>
      <span style={{ fontSize: 10, fontWeight: 700, color: c.active ? BRAND.primary : BRAND.muted, background: c.active ? BRAND.surface : BRAND.surface2, padding: '1px 7px', borderRadius: 99, minWidth: 20, textAlign: 'center' }}>{c.count}</span>
    </button>
  );
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', background: BRAND.surface }}>
      {/* Drawer header */}
      <div style={{ padding: '14px 16px', borderBottom: `1px solid ${BRAND.border}`, display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexShrink: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ width: 34, height: 34, borderRadius: 99, background: BRAND.primary, color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 13, fontWeight: 700 }}>L</div>
          <div>
            <div style={{ fontSize: 13, fontWeight: 700, color: BRAND.text, letterSpacing: -0.1 }}>Lucas Almeida</div>
            <div style={{ fontSize: 10.5, color: BRAND.muted }}>473 músicas · 3 repertórios</div>
          </div>
        </div>
        <button style={{ background: 'none', border: 'none', color: BRAND.muted, padding: 4 }}>{Icons2.xCircle(BRAND.muted)}</button>
      </div>

      <div style={{ flex: 1, overflow: 'auto', padding: '10px 14px 20px' }}>
        {/* Home / Início */}
        <button style={{ width: '100%', display: 'flex', alignItems: 'center', gap: 10, padding: '9px 4px', background: 'transparent', border: 'none', cursor: 'pointer', textAlign: 'left', marginBottom: 4 }}>
          {Icons.home(BRAND.text, false)}
          <span style={{ fontSize: 13, fontWeight: 700, color: BRAND.text }}>Início</span>
        </button>

        {/* Ministração */}
        <div style={{ fontSize: 10, fontWeight: 800, letterSpacing: 1.4, textTransform: 'uppercase', color: BRAND.muted, margin: '14px 4px 6px' }}>Ministração</div>
        {CAT_MIN.map((c, i) => <CatRow key={i} c={c} />)}

        {/* Missa */}
        <div style={{ fontSize: 10, fontWeight: 800, letterSpacing: 1.4, textTransform: 'uppercase', color: BRAND.muted, margin: '14px 4px 6px' }}>Missa</div>
        {CAT_MISSA.map((c, i) => <CatRow key={i} c={c} color={BRAND.accent} />)}

        {/* Footer actions */}
        <div style={{ marginTop: 18, paddingTop: 14, borderTop: `1px solid ${BRAND.border}` }}>
          <button style={{ width: '100%', display: 'flex', alignItems: 'center', gap: 10, padding: '9px 4px', background: 'transparent', border: 'none', cursor: 'pointer', textAlign: 'left' }}>
            {Icons2.settings(BRAND.muted)}
            <span style={{ fontSize: 12.5, fontWeight: 600, color: BRAND.text }}>Configurações</span>
          </button>
        </div>
      </div>
    </div>
  );
}

// Home Screen factory v2
function HomeScreenV2({ Variant, Nav, drawerOpen }) {
  return (
    <Phone>
      <div style={{ position: 'relative', flex: 1, display: 'flex', overflow: 'hidden' }}>
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <Variant />
        </div>
        {drawerOpen && (
          <>
            <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,.35)', zIndex: 40 }} />
            <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: '84%', zIndex: 50, boxShadow: '2px 0 20px rgba(0,0,0,.15)' }}>
              <DrawerCategorias />
            </div>
          </>
        )}
      </div>
      <Nav active="home" />
    </Phone>
  );
}

Object.assign(window, {
  H1_SearchFirst, H2_DenseAboveFold, H3_CategoryChipsHome, H4_EditorialWidgets,
  DrawerCategorias, HomeScreenV2, LiturgyCompact, HeaderSearch, LITURGY, Icons2,
});
