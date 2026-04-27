# Prompt para Claude Code — Refatorar tags de seção da cifra

Quero que você refatore o estilo das **tags de seção** (marcadores como `[REFRÃO]`, `[1ª PARTE]`, `(PRÉ-REFRÃO)`, etc) no meu app **My Cifras**. Aqui estão os requisitos completos.

---

## 1. Objetivo visual

Substituir as tags coloridas atuais (pílulas com fundo amarelo/lilás/roxo) por um tratamento **monocromático, discreto e tipográfico**, que estrutura a leitura sem competir com o conteúdo da cifra.

**Tratamento:**
- **Barra vertical fina** à esquerda do rótulo (gutter acent), cor `#b1abc3`.
- **Rótulo em small-caps** (uppercase + letter-spacing), cor `#b1abc3`, fonte `Inter`.
- **Refrão tem peso extra** (font-weight 800 e barra mais espessa), sem mudar a cor. Toda a hierarquia é feita por peso tipográfico — não há cor de destaque.
- Zero pílulas, zero backgrounds, zero bordas.

---

## 2. Especificação CSS exata

```css
/* Base de toda tag de seção */
.section-marker {
  display: inline-flex;
  align-items: baseline;
  gap: 8px;
  margin: 3px 0;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  font-size: 9px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.13em;
  color: #b1abc3;
  background: none;
  border: none;
  padding: 0;
  border-radius: 0;
}

/* Barra vertical à esquerda (via ::before, pra não precisar mexer no HTML) */
.section-marker::before {
  content: '';
  display: inline-block;
  align-self: stretch;
  width: 2px;
  min-height: 12px;
  margin-top: 3px;
  background: #b1abc3;
  border-radius: 2px;
  opacity: 0.7;
  flex-shrink: 0;
}

/* Refrão: mais peso e barra mais espessa, mas MESMA cor */
.sm-chorus {
  font-weight: 800;
}
.sm-chorus::before {
  width: 3px;
  opacity: 1;
}

/* Demais tipos herdam a base e não precisam de override */
.sm-part,
.sm-prechorus,
.sm-bridge,
.sm-intro,
.sm-solo,
.sm-interlude,
.sm-outro {
  /* vazio — usa os defaults de .section-marker */
}
```

> Elimine `background`, `border`, `color: #5c3d00 / #fff / #ede8ff`, `padding: 1px 10px`, `border-radius: 5px` dos seletores existentes `.sm-*`. Substitua pelos valores acima.

---

## 3. Formatação do rótulo (variações suportadas)

O parser da cifra precisa aceitar **todas estas formas** como equivalentes e normalizar para a forma visual canônica:

### Formas aceitas na entrada (ChordPro-like)
| Entrada bruta | Normaliza para |
|---|---|
| `[1ª Parte]` | `1ª PARTE` |
| `[1a Parte]` | `1ª PARTE` |
| `(1ª Parte)` | `1ª PARTE` |
| `(1a Parte)` | `1ª PARTE` |
| `1ª Parte` (linha solo) | `1ª PARTE` |
| `1a Parte` (linha solo) | `1ª PARTE` |
| `[Refrão]` / `(Refrão)` / `Refrão` | `REFRÃO` |
| `[Pré-Refrão]` / `(Pré-Refrão)` / `Pré-Refrão` | `PRÉ-REFRÃO` |
| `[Ponte]` / `(Ponte)` / `Ponte` | `PONTE` |
| `[Intro]` / `(Intro)` / `Intro` | `INTRO` |
| `[Solo]` / `(Solo)` / `Solo` | `SOLO` |
| `[Interlúdio]` / `(Interlúdio)` / `Interlúdio` | `INTERLÚDIO` |
| `[Final]` / `(Final)` / `Final` / `[Outro]` | `FINAL` |

### Regras do parser
1. **Delimitadores opcionais**: a tag pode vir entre `[...]`, `(...)` ou **sem nenhum delimitador** se ocupar a linha inteira.
2. **Normalização ordinal**: `1a`, `2a`, `3a` → `1ª`, `2ª`, `3ª` (ordinal feminino). Idem `1o` → `1º` se houver uso masculino.
3. **Case-insensitive** na detecção, mas a saída renderizada é sempre **UPPERCASE**.
4. **Mapeamento para classe CSS** (pra aplicar peso do refrão):
   - `Refrão`, `Coro` → `sm-chorus`
   - `Pré-Refrão`, `Pre-Refrao` → `sm-prechorus`
   - `Parte`, `Verso`, `Estrofe` (com ou sem número) → `sm-part`
   - `Ponte` → `sm-bridge`
   - `Intro` → `sm-intro`
   - `Solo` → `sm-solo`
   - `Interlúdio` → `sm-interlude`
   - `Final`, `Outro` → `sm-outro`
5. **A renderização NÃO mostra colchetes nem parênteses.** Só o texto uppercase — os delimitadores do fonte são só sintaxe de entrada.

### Regex sugerido (JavaScript)
```js
// Detecta a linha inteira como tag, com ou sem delimitadores.
const SECTION_TAG_RE = /^\s*(?:\[([^\]]+)\]|\(([^)]+)\)|([A-Za-zÀ-ÿ0-9º ª.\-]+?))\s*$/;

// Normaliza ordinais
function normalizeOrdinals(s) {
  return s
    .replace(/\b(\d+)a\b/g, '$1ª')
    .replace(/\b(\d+)o\b/g, '$1º');
}

// Mapa tipo → classe
const TYPE_MAP = [
  { re: /^(refr[ãa]o|coro)$/i,              cls: 'sm-chorus'    },
  { re: /^pr[éeE]-?\s*refr[ãa]o$/i,          cls: 'sm-prechorus' },
  { re: /^(parte|verso|estrofe)/i,           cls: 'sm-part'      },
  { re: /^ponte$/i,                          cls: 'sm-bridge'    },
  { re: /^intro(du[çc][ãa]o)?$/i,            cls: 'sm-intro'     },
  { re: /^solo$/i,                           cls: 'sm-solo'      },
  { re: /^interl[úu]dio$/i,                  cls: 'sm-interlude' },
  { re: /^(final|outro)$/i,                  cls: 'sm-outro'     },
];

function classifySection(label) {
  const norm = label.trim();
  for (const { re, cls } of TYPE_MAP) {
    if (re.test(norm)) return cls;
  }
  return 'sm-part'; // fallback
}
```

### HTML renderizado (exemplo)
```html
<!-- [1ª Parte] -->
<div class="section-marker sm-part">1ª PARTE</div>

<!-- [Refrão] -->
<div class="section-marker sm-chorus">REFRÃO</div>

<!-- (Pré-Refrão) -->
<div class="section-marker sm-prechorus">PRÉ-REFRÃO</div>
```

> Use `<div>` (não `<span>`), pra que a tag ocupe sua própria linha e a barra vertical fique alinhada à altura completa do label.

---

## 4. Design tokens a respeitar

Do arquivo `DESIGN.md` do projeto. **Não adicione novas cores** — só use o que já existe (e `#b1abc3` como novo token dedicado).

Adicione no `:root`:
```css
:root {
  /* já existentes */
  --primary: #5b4b8a;
  --text: #1f2937;
  --border: #e6e1f0;
  /* NOVO */
  --section-marker: #b1abc3;
}
```

E use `var(--section-marker)` em vez do literal `#b1abc3` nos seletores `.section-marker` e `.section-marker::before`.

---

## 5. Espaçamento ao redor

- Espaço **acima** da tag (separando do bloco anterior): `margin-top: 12px` no `.section-marker`.
- Espaço **abaixo** da tag (colando no primeiro verso): `margin-bottom: 6px`.
- Se for a primeira tag do documento: `margin-top: 0`.

Ajuste:
```css
.section-marker {
  /* ...base... */
  margin: 12px 0 6px;
}
.section-marker:first-child {
  margin-top: 0;
}
```

---

## 6. Dark mode (se o app tiver)

A cor `#b1abc3` já funciona bem em ambos os modos porque é um cinza quente de luminância média. Se quiser refinar:
```css
@media (prefers-color-scheme: dark) {
  :root { --section-marker: #8a82a8; }
}
```

---

## 7. Checklist de entrega

- [ ] CSS de `.section-marker`, `.sm-chorus`, demais `.sm-*` substituído conforme spec.
- [ ] `:root` ganhou `--section-marker: #b1abc3;`.
- [ ] Parser da cifra aceita `[...]`, `(...)` e linha solo.
- [ ] Ordinais `1a/2a/3a` normalizados para `1ª/2ª/3ª`.
- [ ] Renderização sempre em UPPERCASE, sem os delimitadores originais.
- [ ] Função `classifySection()` aplicando a classe correta.
- [ ] Testado com os exemplos da tabela do item 3.
- [ ] `font-family: 'Inter'`, `font-size: 9px`, `letter-spacing: 0.13em`.
- [ ] Refrão com `font-weight: 800` e barra de 3px; demais com 700 e barra 2px/opacity 0.7.
- [ ] Modo apresentação (se existir) continuando a mostrar as tags legivelmente — pode aumentar pra `font-size: 11px` nesse modo.

---

## 8. O que NÃO fazer

- ❌ Não usar cores diferentes pra tipos diferentes de seção (nada de amarelo pro verso, roxo pro refrão, etc).
- ❌ Não usar backgrounds, bordas arredondadas ou pílulas.
- ❌ Não renderizar os colchetes/parênteses na saída visual.
- ❌ Não usar `font-weight` abaixo de 700 — tags precisam ter presença suficiente.
- ❌ Não quebrar a tag em duas linhas — ela é sempre `white-space: nowrap`.
