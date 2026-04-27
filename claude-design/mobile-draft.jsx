// My Cifras — Repertório com fluxo de rascunho "Em montagem"
// Premissas:
// - Sempre existe um rascunho "Em montagem"
// - Adicionar música (de qualquer lugar) cai direto nele
// - Usuário nomeia + salva → vira repert. nomeado + novo rascunho limpo nasce
// - "Limpar" esvazia o rascunho

const DRAFT_SONGS = [
  { title: 'Determinada Decisão', tom: 'A#', cat: 'Fé e Conversão' },
  { title: 'Estava com Saudade de Ti', tom: 'G', cat: 'Adoração' },
  { title: 'Me faz novo', tom: 'C', cat: 'Entrega' },
];

const SAVED_REPS = [
  { id: 1, name: 'Missa 19-04-26', count: 13, last: 'Há 2 dias', color: '#5b4b8a' },
  { id: 2, name: 'Teste', count: 3, last: 'Há 5 dias', color: '#8b7bca' },
  { id: 3, name: 'Cenáculo', count: 8, last: 'Semana passada', color: '#a090c0' },
];

// ═══════════════════════════════════════════════════════════════
// D1 — RASCUNHO NO TOPO ★ (recomendada)
// Drafting block is a card with dashed-ish accent, input inline,
// song list below, actions at the bottom. Saved reps below.
// ═══════════════════════════════════════════════════════════════
function RepD1_DraftTop() {
  return (
    <div style={{ flex: 1, overflow: 'auto', padding: '12px 14px 100px', background: BRAND.bg }}>
      {/* Draft header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
          <span style={{ width: 8, height: 8, borderRadius: 99, background: BRAND.accent, boxShadow: `0 0 0 3px ${BRAND.accentBg}` }} />
          <span style={{ fontSize: 10.5, fontWeight: 800, letterSpacing: 1.4, textTransform: 'uppercase', color: BRAND.muted }}>Em montagem</span>
        </div>
        <span style={{ fontSize: 11, fontWeight: 700, color: BRAND.muted }}>{DRAFT_SONGS.length} músicas</span>
      </div>

      {/* Draft card */}
      <div style={{ background: BRAND.surface, border: `1.5px solid ${BRAND.primary}`, borderRadius: 14, padding: '12px', boxShadow: '0 4px 16px rgba(91,75,138,.12)', marginBottom: 18 }}>
        {/* Name input */}
        <div style={{ position: 'relative', marginBottom: 10 }}>
          <input placeholder="Dê um nome ao repertório..." style={{ width: '100%', padding: '11px 14px', paddingRight: 14, border: `1.5px solid ${BRAND.border}`, borderRadius: 10, background: BRAND.bg, fontSize: 14, fontWeight: 600, color: BRAND.text, outline: 'none', boxSizing: 'border-box', fontFamily: 'inherit' }} />
        </div>

        {/* Songs in draft */}
        {DRAFT_SONGS.length > 0 ? (
          <div style={{ marginBottom: 10 }}>
            {DRAFT_SONGS.map((s, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '9px 4px', borderBottom: i < DRAFT_SONGS.length - 1 ? `1px solid ${BRAND.border}` : 'none' }}>
                <span style={{ color: BRAND.muted }}>{Icons.drag(BRAND.muted)}</span>
                <span style={{ fontSize: 11.5, fontWeight: 700, color: BRAND.primary, width: 16 }}>{i + 1}</span>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 13, fontWeight: 700, color: BRAND.text, letterSpacing: -0.1 }}>{s.title}</div>
                  <div style={{ fontSize: 10.5, color: BRAND.muted, marginTop: 1 }}>{s.cat}</div>
                </div>
                <span style={{ fontSize: 10, fontWeight: 700, color: BRAND.accent, background: BRAND.accentBg, border: `1px solid ${BRAND.accentBorder}`, borderRadius: 99, padding: '1px 7px' }}>{s.tom}</span>
                <button style={{ width: 22, height: 22, borderRadius: 99, background: 'transparent', border: 'none', color: BRAND.muted, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 0 }}>{Icons.close(BRAND.muted)}</button>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ padding: '24px 8px', textAlign: 'center', color: BRAND.muted, fontSize: 12, lineHeight: 1.5 }}>
            Adicione músicas pelo botão<br/><b style={{ color: BRAND.primary }}>+ Repertório</b> nos cards.
          </div>
        )}

        {/* Draft actions */}
        <div style={{ display: 'flex', gap: 6, marginTop: 8 }}>
          <button style={{ flex: 1, background: BRAND.primary, color: '#fff', border: 'none', borderRadius: 99, padding: '10px', fontSize: 13, fontWeight: 800, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, boxShadow: '0 2px 8px rgba(91,75,138,.28)' }}>
            {Icons.plus('#fff')} Salvar repertório
          </button>
          <button style={{ background: 'transparent', color: BRAND.muted, border: `1.5px solid ${BRAND.border}`, borderRadius: 99, padding: '10px 14px', fontSize: 12, fontWeight: 600 }}>Limpar</button>
        </div>
      </div>

      {/* Saved reps */}
      <div style={{ fontSize: 10.5, fontWeight: 800, letterSpacing: 1.4, textTransform: 'uppercase', color: BRAND.muted, marginBottom: 10 }}>Salvos · {SAVED_REPS.length}</div>
      {SAVED_REPS.map(r => (
        <div key={r.id} style={{ background: BRAND.surface, border: `1.5px solid ${BRAND.border}`, borderRadius: 12, padding: '11px 12px', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 11 }}>
          <div style={{ width: 38, height: 38, borderRadius: 10, background: r.color, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
            {Icons.music('#fff', true)}
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: 13.5, fontWeight: 700, color: BRAND.text, letterSpacing: -0.1 }}>{r.name}</div>
            <div style={{ fontSize: 11, color: BRAND.muted, marginTop: 2 }}>{r.count} músicas · {r.last}</div>
          </div>
          <button style={{ width: 34, height: 34, borderRadius: 99, background: BRAND.primaryLight, border: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>{Icons.play(BRAND.primary)}</button>
          <button style={{ width: 28, height: 28, borderRadius: 99, background: 'transparent', border: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>{Icons.more(BRAND.muted)}</button>
        </div>
      ))}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// D2 — HERO ATIVO + RASCUNHO SEPARADO
// Shows active saved rep at top; draft is a compact bar below.
// ═══════════════════════════════════════════════════════════════
function RepD2_ActiveAndDraft() {
  return (
    <div style={{ flex: 1, overflow: 'auto', padding: '0 0 100px', background: BRAND.bg }}>
      {/* Active rep hero */}
      <div style={{ background: `linear-gradient(145deg, ${BRAND.primary} 0%, #4a3a78 100%)`, padding: '14px 16px 16px', color: '#fff' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ fontSize: 9.5, fontWeight: 800, letterSpacing: 1.4, textTransform: 'uppercase', color: BRAND.accent }}>Ativo agora</div>
          <button style={{ background: 'rgba(255,255,255,.12)', color: '#fff', border: 'none', borderRadius: 99, padding: '3px 10px', fontSize: 11, fontWeight: 600 }}>Trocar</button>
        </div>
        <div style={{ fontSize: 19, fontWeight: 800, marginTop: 5, letterSpacing: -0.3 }}>Missa 19-04-26</div>
        <div style={{ fontSize: 11.5, color: 'rgba(255,255,255,.7)', marginTop: 1 }}>13 músicas · ~52 min</div>
        <div style={{ display: 'flex', gap: 6, marginTop: 12 }}>
          <button style={{ flex: 1, background: BRAND.accent, color: '#1f1b2e', border: 'none', borderRadius: 99, padding: '9px', fontSize: 12, fontWeight: 800, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 5 }}>{Icons.play('#1f1b2e')} Apresentar</button>
          <button style={{ background: 'rgba(255,255,255,.14)', color: '#fff', border: 'none', borderRadius: 99, padding: '9px 12px', fontSize: 11.5, fontWeight: 700 }}>PDF</button>
          <button style={{ background: 'rgba(255,255,255,.14)', color: '#fff', border: 'none', borderRadius: 99, padding: '9px 12px', fontSize: 11.5, fontWeight: 700 }}>Doc</button>
        </div>
      </div>

      {/* Draft row */}
      <div style={{ padding: '12px 14px 0' }}>
        <div style={{ background: BRAND.surface, border: `1.5px dashed ${BRAND.primary}`, borderRadius: 12, padding: '10px 12px', display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ width: 36, height: 36, borderRadius: 10, background: BRAND.primaryLight, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
            <span style={{ fontSize: 14, fontWeight: 800, color: BRAND.primary }}>{DRAFT_SONGS.length}</span>
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: 9.5, fontWeight: 800, letterSpacing: 1.4, textTransform: 'uppercase', color: BRAND.accent, marginBottom: 2 }}>Em montagem</div>
            <div style={{ fontSize: 12.5, fontWeight: 600, color: BRAND.text }}>{DRAFT_SONGS.map(s => s.title.split(' ')[0]).join(', ')}…</div>
          </div>
          <button style={{ background: BRAND.primary, color: '#fff', border: 'none', borderRadius: 99, padding: '6px 12px', fontSize: 11, fontWeight: 700 }}>Abrir</button>
        </div>
      </div>

      {/* Saved reps */}
      <div style={{ padding: '18px 14px 0' }}>
        <div style={{ fontSize: 10.5, fontWeight: 800, letterSpacing: 1.4, textTransform: 'uppercase', color: BRAND.muted, marginBottom: 10 }}>Salvos</div>
        {SAVED_REPS.map(r => (
          <div key={r.id} style={{ background: BRAND.surface, border: `1px solid ${BRAND.border}`, borderRadius: 10, padding: '10px 12px', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ width: 34, height: 34, borderRadius: 8, background: r.color, opacity: 0.9, flexShrink: 0 }} />
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 13, fontWeight: 700, color: BRAND.text }}>{r.name}</div>
              <div style={{ fontSize: 10.5, color: BRAND.muted, marginTop: 1 }}>{r.count} músicas · {r.last}</div>
            </div>
            <button style={{ background: 'none', border: 'none', color: BRAND.muted }}>{Icons.more(BRAND.muted)}</button>
          </div>
        ))}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// D3 — BOTTOM SHEET de rascunho (draft is a minimized bar;
//      tapping it expands to a full bottom sheet)
// ═══════════════════════════════════════════════════════════════
function RepD3_DraftSheet() {
  return (
    <div style={{ flex: 1, overflow: 'hidden', background: BRAND.bg, position: 'relative' }}>
      {/* Main content: saved reps list */}
      <div style={{ padding: '12px 14px 220px', overflow: 'auto', height: '100%', boxSizing: 'border-box' }}>
        <h2 style={{ margin: '4px 0 14px', fontSize: 22, fontWeight: 800, color: BRAND.text, letterSpacing: -0.4 }}>Repertórios</h2>

        {SAVED_REPS.map(r => (
          <div key={r.id} style={{ background: BRAND.surface, border: `1.5px solid ${BRAND.border}`, borderRadius: 14, padding: '12px 12px', marginBottom: 10, display: 'flex', alignItems: 'center', gap: 11 }}>
            <div style={{ width: 40, height: 40, borderRadius: 10, background: r.color, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
              {Icons.music('#fff', true)}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: 14, fontWeight: 700, color: BRAND.text, letterSpacing: -0.1 }}>{r.name}</div>
              <div style={{ fontSize: 11.5, color: BRAND.muted, marginTop: 2 }}>{r.count} músicas · {r.last}</div>
            </div>
            <button style={{ width: 36, height: 36, borderRadius: 99, background: BRAND.primaryLight, border: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>{Icons.play(BRAND.primary)}</button>
            <button style={{ background: 'none', border: 'none', color: BRAND.muted }}>{Icons.more(BRAND.muted)}</button>
          </div>
        ))}
      </div>

      {/* Sticky draft bottom-sheet-like bar */}
      <div style={{ position: 'absolute', left: 0, right: 0, bottom: 0, zIndex: 15, background: BRAND.surface, borderTop: `1px solid ${BRAND.border}`, borderRadius: '16px 16px 0 0', padding: '10px 14px 14px', boxShadow: '0 -8px 30px rgba(91,75,138,.12)' }}>
        {/* grab handle */}
        <div style={{ width: 36, height: 4, borderRadius: 2, background: BRAND.border, margin: '0 auto 10px' }} />
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ width: 36, height: 36, borderRadius: 10, background: BRAND.accentBg, border: `1px solid ${BRAND.accentBorder}`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
            <span style={{ fontSize: 14, fontWeight: 800, color: BRAND.accent }}>{DRAFT_SONGS.length}</span>
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: 9.5, fontWeight: 800, letterSpacing: 1.4, textTransform: 'uppercase', color: BRAND.accent, marginBottom: 1 }}>Em montagem</div>
            <div style={{ fontSize: 12, color: BRAND.muted }}>Toque pra nomear e salvar</div>
          </div>
          <button style={{ background: BRAND.primary, color: '#fff', border: 'none', borderRadius: 99, padding: '8px 14px', fontSize: 12, fontWeight: 700 }}>Abrir</button>
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// D4 — PROMPT DE SALVAR APARECE APÓS 1ª MÚSICA
// Same as D1 but with a contextual "save" prompt on top of
// the draft card to emphasize that saving = persisting.
// ═══════════════════════════════════════════════════════════════
function RepD4_SavePrompt() {
  return (
    <div style={{ flex: 1, overflow: 'auto', padding: '12px 14px 100px', background: BRAND.bg }}>
      {/* Contextual toast/prompt */}
      <div style={{ background: BRAND.primaryLight2, border: `1px solid ${BRAND.primary}`, borderRadius: 10, padding: '10px 12px', marginBottom: 10, display: 'flex', alignItems: 'center', gap: 10 }}>
        <div style={{ fontSize: 16 }}>✨</div>
        <div style={{ flex: 1, fontSize: 12, color: BRAND.text, lineHeight: 1.4 }}>
          <b>{DRAFT_SONGS.length} músicas no rascunho.</b>
          <div style={{ color: BRAND.muted, marginTop: 1 }}>Dê um nome pra salvar permanentemente.</div>
        </div>
      </div>

      {/* Draft card (same as D1 but more streamlined) */}
      <div style={{ background: BRAND.surface, border: `1.5px solid ${BRAND.border}`, borderRadius: 14, padding: '4px 0', marginBottom: 18, boxShadow: '0 1px 3px rgba(60,40,100,.08)' }}>
        <div style={{ padding: '10px 14px 8px', borderBottom: `1px solid ${BRAND.border}`, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
            <span style={{ width: 8, height: 8, borderRadius: 99, background: BRAND.accent }} />
            <span style={{ fontSize: 10.5, fontWeight: 800, letterSpacing: 1.4, textTransform: 'uppercase', color: BRAND.muted }}>Em montagem</span>
          </div>
          <button style={{ background: 'transparent', border: 'none', color: BRAND.muted, fontSize: 11, fontWeight: 600 }}>Limpar</button>
        </div>
        {DRAFT_SONGS.map((s, i) => (
          <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '10px 14px', borderBottom: i < DRAFT_SONGS.length - 1 ? `1px solid ${BRAND.border}` : 'none' }}>
            <span style={{ color: BRAND.muted }}>{Icons.drag(BRAND.muted)}</span>
            <span style={{ fontSize: 11.5, fontWeight: 700, color: BRAND.primary, width: 16 }}>{i + 1}</span>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: 13, fontWeight: 700, color: BRAND.text, letterSpacing: -0.1 }}>{s.title}</div>
              <div style={{ fontSize: 10.5, color: BRAND.muted, marginTop: 1 }}>{s.cat}</div>
            </div>
            <span style={{ fontSize: 10, fontWeight: 700, color: BRAND.accent, background: BRAND.accentBg, border: `1px solid ${BRAND.accentBorder}`, borderRadius: 99, padding: '1px 7px' }}>{s.tom}</span>
            <button style={{ width: 22, height: 22, borderRadius: 99, background: 'transparent', border: 'none', color: BRAND.muted, padding: 0 }}>{Icons.close(BRAND.muted)}</button>
          </div>
        ))}

        <div style={{ padding: '10px 12px 12px', display: 'flex', gap: 6, alignItems: 'center' }}>
          <input placeholder="Nome do repertório..." style={{ flex: 1, padding: '9px 12px', border: `1.5px solid ${BRAND.border}`, borderRadius: 99, background: BRAND.bg, fontSize: 12.5, fontWeight: 600, color: BRAND.text, outline: 'none', fontFamily: 'inherit' }} />
          <button style={{ background: BRAND.primary, color: '#fff', border: 'none', borderRadius: 99, padding: '9px 14px', fontSize: 12, fontWeight: 800 }}>Salvar</button>
        </div>
      </div>

      {/* Saved reps */}
      <div style={{ fontSize: 10.5, fontWeight: 800, letterSpacing: 1.4, textTransform: 'uppercase', color: BRAND.muted, marginBottom: 10 }}>Salvos</div>
      {SAVED_REPS.map(r => (
        <div key={r.id} style={{ background: BRAND.surface, border: `1.5px solid ${BRAND.border}`, borderRadius: 12, padding: '11px 12px', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 11 }}>
          <div style={{ width: 38, height: 38, borderRadius: 10, background: r.color, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>{Icons.music('#fff', true)}</div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: 13.5, fontWeight: 700, color: BRAND.text }}>{r.name}</div>
            <div style={{ fontSize: 11, color: BRAND.muted, marginTop: 2 }}>{r.count} músicas · {r.last}</div>
          </div>
          <button style={{ width: 34, height: 34, borderRadius: 99, background: BRAND.primaryLight, border: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>{Icons.play(BRAND.primary)}</button>
        </div>
      ))}
    </div>
  );
}

Object.assign(window, { RepD1_DraftTop, RepD2_ActiveAndDraft, RepD3_DraftSheet, RepD4_SavePrompt });
