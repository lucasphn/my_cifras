# My Cifras — Design Reference

> Referência viva de design extraída do CSS do app. Use como guia ao criar novos elementos, features ou ao refinar a UI.

---

## 1. Tokens de Cor

### Paleta principal (CSS custom properties)

| Token | Valor | Uso |
|---|---|---|
| `--bg` | `#f7f6fb` | Fundo geral da aplicação |
| `--surface` | `#ffffff` | Cards, modais, painéis elevados |
| `--surface2` | `#eeebf6` | Fundo de inputs, hover suave, superfícies secundárias |
| `--border` | `#e6e1f0` | Bordas de cards, separadores |
| `--text` | `#1f2937` | Texto primário |
| `--text-muted` | `#6b7280` | Texto secundário, labels, placeholders |
| `--primary` | `#5b4b8a` | Roxo principal — brand, acordes, CTA, ativo na sidebar |
| `--primary-hover` | `#4a3a78` | Hover de elementos primary |
| `--primary-light` | `rgba(91,75,138,.09)` | Fundo de hover/ativo sutil (sidebar, botões) |
| `--primary-light2` | `rgba(91,75,138,.16)` | Versão levemente mais densa do primary-light |
| `--accent` | `#d4af37` | Dourado — badges de categoria, destaques, links |
| `--accent-hover` | `#b8961f` | Hover do accent |
| `--danger` | `#dc2626` | Ações destrutivas, badge de contagem no repertório |
| `--success` | `#16a34a` | Confirmações, botão "Salvar Tom", músicas adicionadas |
| `--chord-color` | `#5b4b8a` | Cor dos acordes nas cifras (= `--primary`) |

### Usos de cor sem token (hardcoded — candidatos a tokenizar)

| Cor | Contexto |
|---|---|
| `#a090c0` | Títulos de seção na sidebar |
| `#f87171` | Texto de ações danger em dropdowns |
| `rgba(248,113,113,.1)` | Fundo hover de ação danger |
| `rgba(212,175,55,.12-.15)` | Fundo de badge dourada (categoria, tom) |
| `rgba(212,175,55,.28-.35)` | Borda de badge dourada |
| `rgba(91,75,138,.06-.09)` | Hover sutil em itens de lista |

---

## 2. Tipografia

| Fonte | Família | Uso |
|---|---|---|
| Interface | `'Inter', system-ui, -apple-system, sans-serif` | Todo o app |
| Mono (cifras) | `'Fira Mono', 'Consolas', 'Courier New', monospace` | Conteúdo da cifra (`--font-mono`) |

### Escala de tamanhos em uso

| Tamanho | Contexto |
|---|---|
| `1.9rem / 800` | Valor dos stat cards |
| `1.15rem / 600` | Texto do quote banner |
| `1.05rem / 800` | Título do header (brand) |
| `1rem / 700–800` | Títulos de seção na home |
| `0.95rem / 600` | Nome da celebração litúrgica |
| `0.92rem / 600` | Nome da música no modal |
| `0.9rem / 700` | Nome da música nos cards |
| `0.88rem / 700` | Nome nas top cards |
| `0.875rem / 500` | Item de categoria na sidebar |
| `0.85rem` | Botões `.btn`, resultados de busca |
| `0.84rem` | Texto de leitura litúrgica |
| `0.82rem` | Dropdowns, inputs inline |
| `0.78rem / 700` | Labels de formulário, autor da citação |
| `0.75rem` | `.song-meta`, excerpts de busca, tag `.hc-cat` |
| `0.72rem / 600` | Label dos stat cards, count na sidebar |
| `0.68rem / 700–800` | Badges de seção, ranking, micro-labels |
| `0.65rem / 800` | Títulos de seção sidebar (`uppercase + letter-spacing`) |

### Padrão de label uppercase

```css
font-size: .68rem;
font-weight: 700–800;
text-transform: uppercase;
letter-spacing: 0.10–0.13em;
color: var(--text-muted);  /* ou #a090c0 na sidebar */
```

---

## 3. Espaçamento & Layout

### Variáveis de layout

| Token | Valor | Uso |
|---|---|---|
| `--sidebar-w` | `260px` | Largura da sidebar |
| `--rep-w` | `300px` | Largura do painel de repertório |
| `--header-h` | `58px` | Altura do header |
| `--radius` | `10px` | Border-radius padrão |
| `--radius-lg` | `14px` | Border-radius de modais e cards principais |

### Border-radius em uso

| Valor | Elemento |
|---|---|
| `99px` | Botões pill, search box, badges, contadores |
| `16px` | Quote banner |
| `14px` | Song cards, modais principais |
| `12px` | Home cards top, lit-card |
| `10px` | Stat cards, home cards, `.cat-dropdown` |
| `9px` | Dropdowns de operações |
| `7px` | Selects, botões de modal |
| `6px` | Inputs inline, tags |
| `5px` | Section markers, mini botões |
| `4px` | Ranking badge, separadores |

### Grid de músicas

```css
/* Grid principal (categorias) */
display: grid;
grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
gap: 12px;

/* Grid home — compacto */
grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
gap: 7px;

/* Top músicas */
grid-template-columns: repeat(4, 1fr);
gap: 8px;
```

---

## 4. Sombras

| Token | Valor | Uso |
|---|---|---|
| `--shadow-sm` | `0 1px 3px rgba(60,40,100,.08), 0 1px 2px rgba(60,40,100,.05)` | Cards em repouso |
| `--shadow-md` | `0 4px 16px rgba(60,40,100,.12), 0 1px 4px rgba(60,40,100,.06)` | Cards em hover |
| `--shadow-lg` | `0 12px 40px rgba(60,40,100,.16), 0 2px 8px rgba(60,40,100,.08)` | Modais, overlays |

---

## 5. Componentes

### Botões

```css
/* .btn — padrão */
background: var(--surface);
border: 1.5px solid var(--border);
border-radius: 99px;
padding: 6px 14px;
font-size: 0.85em;
font-weight: 500;
color: var(--text);
transition: all .18s;

/* .btn-accent — CTA primário */
background: var(--primary);
border-color: var(--primary);
color: #fff;
box-shadow: 0 2px 8px rgba(91,75,138,.28);

/* hover .btn-accent */
background: var(--primary-hover);
box-shadow: 0 4px 14px rgba(91,75,138,.38);
```

### Cards de música

```css
/* Song card (grid de categoria) */
background: var(--surface);
border: 1.5px solid var(--border);
border-radius: 14px;
padding: 16px;
box-shadow: var(--shadow-sm);
transition: transform .18s cubic-bezier(.4,0,.2,1), box-shadow .18s, border-color .18s;

/* hover */
border-color: rgba(91,75,138,.35);
transform: translateY(-2px);
box-shadow: var(--shadow-md);

/* Home card — compacto */
border-radius: 10px;
padding: 10px 12px;

/* Top card — gradiente sutil */
background: linear-gradient(135deg, var(--surface) 0%, rgba(91,75,138,.08) 100%);
border: 1.5px solid rgba(91,75,138,.25);
border-radius: 12px;
```

### Badges / Pills

```css
/* Categoria — dourado */
background: rgba(212,175,55,.12);
color: var(--accent);           /* #d4af37 */
border: 1px solid rgba(212,175,55,.28);
border-radius: 99px;
padding: 1px 7px;
font-size: .65rem;
font-weight: 700;

/* Tom — dourado sobre primary-light */
background: var(--primary-light);
color: var(--accent);
border-radius: 99px;
padding: 1px 7px;
font-size: .68rem;
font-weight: 700;

/* Tag — dourado mais sutil */
background: rgba(212,175,55,.10);
color: var(--accent);
border: 1px solid rgba(212,175,55,.20);
border-radius: 99px;
padding: 1px 6px;
font-size: .64rem;
font-weight: 600;
```

### Section markers (cifras)

```css
/* Base compartilhada */
.section-marker {
  display: inline-block;
  border-radius: 5px;
  padding: 1px 10px;
  font-size: 0.78em;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin: 2px 0;
}

/* Refrão / Coro — roxo escuro sólido */
.sm-chorus {
  background: var(--primary);   /* #5b4b8a */
  color: #ede8ff;
  border: 1px solid rgba(91,75,138,.7);
}

/* Pré-Refrão — roxo médio */
.sm-prechorus {
  background: #8b7bca;
  color: #fff;
  border: 1px solid rgba(91,75,138,.5);
}

/* Verso / Parte / Estrofe / Ponte / Interlúdio — creme claro */
.sm-part {
  background: #fef3c7;
  color: #5c3d00;
  border: 1px solid rgba(212,175,55,.55);
}
```

### Sidebar

```css
/* Título de seção */
font-size: 0.68em; font-weight: 800;
text-transform: uppercase; letter-spacing: 0.13em;
color: #a090c0;

/* Item de categoria */
padding: 8px 12px 8px 14px;
border-left: 3px solid transparent;
border-radius: 0 10px 10px 0;
transition: color .15s, background .15s;

/* Ativo */
color: var(--primary); font-weight: 700;
background: var(--primary-light);
border-left-color: var(--primary);
```

### Inputs

```css
background: var(--bg);            /* ou var(--surface2) inline */
border: 1.5px solid var(--border);
border-radius: 99px;              /* search */ /* ou 6–7px inline */
color: var(--text);
outline: none;
transition: border-color .18s, box-shadow .18s;

/* focus */
border-color: var(--accent);
box-shadow: 0 0 0 3px rgba(74,108,247,.12);
```

### Dropdowns de contexto

```css
background: var(--surface2);
border: 1px solid var(--border);
border-radius: 9px;
box-shadow: 0 8px 24px rgba(0,0,0,.4–.45);
min-width: 130–145px;

/* item */
padding: .55rem .9rem;
font-size: .82rem;
transition: background .12s;

/* item:hover */
background: var(--primary-light);

/* item danger */
color: #f87171;
/* danger:hover */
background: rgba(248,113,113,.1);
```

### Quote banner

```css
background: var(--primary);
border-radius: 16px;
padding: 2.5rem 2.75rem;

/* tag interna */
color: var(--accent);
background: rgba(212,175,55,.15);
border: 1px solid rgba(212,175,55,.3);

/* texto */
color: rgba(255,255,255,.95);
font-size: 1.15rem; font-weight: 600;

/* divider */
width: 36px; height: 2px;
background: linear-gradient(90deg, var(--accent), transparent);
```

---

## 6. Cifras — Tipografia e Cores

```css
/* Container da cifra */
font-family: var(--font-mono);
font-size: 0.93em;
font-weight: 600;
line-height: 1.65;
white-space: pre;

/* Linhas de acorde */
.chord-line {
  color: var(--chord-color);   /* #5b4b8a */
  font-weight: 800;
}

/* Modo apresentação */
font-size: 1.05em;
font-weight: 700;
```

---

## 7. Animações & Transições

| Duração | Uso |
|---|---|
| `.12s` | Hover rápido em dropdowns |
| `.15s` | Hover padrão (cor, background) |
| `.18s` | Transições de botão, card, border |
| `.20s` | Chevron, ícones rotativos |
| `.22s cubic-bezier(.4,0,.2,1)` | Arrow de seção na sidebar |
| `.18s cubic-bezier(.4,0,.2,1)` | Hover de card com `translateY` |
| `@keyframes spin .7s linear` | Spinner de busca |

---

## 8. Padrões de Interação

### Hover de card (padrão universal)
```css
transform: translateY(-2px);
box-shadow: var(--shadow-md);
border-color: rgba(91,75,138,.30–.50);
```

### Estado ativo na sidebar
```css
color: var(--primary);
background: var(--primary-light);
border-left: 3px solid var(--primary);
font-weight: 700;
```

### Feedback de ação confirmada
```css
/* Adicionado ao repertório */
background: rgba(22,163,74,.1);
border-color: var(--success);
color: var(--success);
```

### Ação destrutiva
```css
color: #f87171;  /* texto */
/* hover */
background: rgba(248,113,113,.1);
```

---

## 9. Responsividade

| Breakpoint | Comportamento |
|---|---|
| `max-width: 1024px` | Mobile/tablet — sidebar vira drawer, repertório vira drawer bottom |
| `min-width: 600px` and `max-width: 1024px` | Tablet — touch targets mínimos 44×44px em `.modal-vctrl` |

```css
/* Ocultar em mobile */
@media (max-width: 1024px) {
  #sidebar { display: none; }
  /* sidebar vira #sidebar-drawer com overlay */
}
```

---

## 10. Android — Modo Claro Forçado

Quando `<body class="android">`, o browser força fundo branco. Compensar com texto escuro:

```css
body.android #cifra-content {
  font-weight: 700;
  color: #1a1529;
  text-rendering: optimizeLegibility;
}
body.android #cifra-content .chord-line {
  color: #5b4b8a;
  font-weight: 900;
}
```

---

## 11. Regras de Design

1. **Acordes sempre em `--primary` (`#5b4b8a`)**. Nunca azul `#1d4ed8`.
2. **Badges de categoria/tom**: dourado `--accent` com fundo `rgba(212,175,55,.12)`.
3. **CTAs principais**: `background: var(--primary)`, border-radius `99px` (pill) ou `7–10px`.
4. **Elevação**: usar `--shadow-sm` em repouso, `--shadow-md` em hover, `--shadow-lg` em modais.
5. **Hover de card**: sempre `translateY(-2px)` + shadow-md + border accent sutil.
6. **Textos uppercase**: apenas para labels/metadados, nunca para conteúdo de cifra.
7. **Touch targets mínimos**: 44×44px em mobile/tablet para controles de modal.
8. **Transições**: `.15s` para cor/background, `.18s` para transforms/shadows.
9. **Border-radius**: pill (`99px`) para badges e inputs de busca; `14px` para cards; `10px` para itens menores; `9px` para dropdowns.
10. **Fonte de cifra**: monospace + `font-weight: 600` para corpo, `800` para acordes.
