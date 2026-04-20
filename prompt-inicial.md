# Prompt Inicial — My Cifras

> **Como usar:** Coloque este arquivo, o `CLAUDE.md` e o `PRD.md` na pasta `my_cifras_pc_owner`.
> Abra o terminal nessa pasta, inicie o Claude Code e cole o conteúdo abaixo.

---

## PROMPT

Você é um desenvolvedor Python + JavaScript experiente. Vamos evoluir a aplicação web **"My Cifras"** — uma ferramenta para o **músico individual** gerenciar seu acervo pessoal de cifras, transpor tons, criar repertórios e acompanhar sua agenda litúrgica.

**Antes de escrever qualquer código, leia completamente os arquivos `CLAUDE.md` e `PRD.md` nesta pasta.** Eles têm todas as especificações, convenções e regras do projeto.

---

### Contexto

**My Cifras** é um produto para o músico litúrgico e gospel. Não é um app de grupo — é uma ferramenta individual. O valor central está em:

1. **Transposição + Meu Tom:** muda o tom em 1 clique e salva no Drive do próprio usuário
2. **Repertórios pessoais:** montagem e organização do setlist de cada músico
3. **Navegação litúrgica:** categorias de Missa e Ministração para encontrar a música certa
4. **Liturgia diária:** integração com a liturgia do dia
5. **Agenda pessoal:** Google Calendar integrado para ensaios, missas e compromissos

**Lucas Almeida** é músico litúrgico em Jaraguá do Sul (SC) e criador do produto.

---

### Estado atual do app (v3.1)

O app está **em produção** na Render.com. As seguintes funcionalidades já estão implementadas:

#### Backend (`app.py` + `auth.py` + `drive.py`)

- OAuth 2.0 completo com Google (escopos: `drive`, `calendar.events`, `userinfo`)
- **Roles:** `OWNER_EMAIL` no env define owners; sem ENV → todos são owner (dev local)
  - `@owner_required` aplicado em todas as rotas de escrita
  - `/api/me` retorna `is_owner`
- **Dados por usuário:** prefs, repertórios e views em `_mycifras_data` no Drive de cada usuário
  - Caches em memória por e-mail: `_prefs_cache`, `_views_cache`, `_reps_cache`
- **Bundle sync:** `GET /api/cifras/bundle` com ETag/304 para sync offline completo
  - ETag de `fileId + modifiedTime`, 4 workers paralelos, só ETag em memória (sem json_bytes)
  - `invalidate_bundle_cache()` chamado após qualquer alteração de conteúdo
- **Cache de biblioteca:** TTL 120s, `invalidate_library_cache()` chama `invalidate_bundle_cache()`
- Todas as rotas de CRUD de cifras, pastas e repertórios
- Limite de 5 repertórios por usuário
- `/api/calendar` (GET), `/api/calendar/events` (POST/PUT/DELETE)
- Filtro de palavras-chave via `CALENDAR_KEYWORDS`
- Páginas públicas: `/privacy`, `/terms`
- Service Worker em `/sw.js`

#### Frontend (`templates/index.html`)

- `<body data-owner="1|0">` + `var _isOwner = document.body.getAttribute('data-owner') === '1'`
- Botões de admin (editar, renomear, excluir, importar) visíveis apenas para owners
- **Cache-first:** abre cifra do IDB imediatamente → atualiza do servidor em background
- **Bundle sync:** `_bundleSync()` com cooldown de 30 min, `_idbBulkPut()` para escrita em batch
- **Meu Tom:** `_myTones[fileId] = { my_key, my_capo }` — exibido nos cards, export e apresentação
- `refreshGridBtns()` — atualiza apenas o estado dos botões nos cards existentes (sem recriar o grid)
- `_markActiveSavedRep()` — atualiza apenas o `.active` na lista de repertórios (sem recriar)
- Pesos de fonte nas cifras: corpo `600`, acordes `.chord-line` `800`
- Sync pill removido — sync é silencioso
- Google Calendar com FullCalendar 6, CRUD completo, drag-and-drop
- Modo Apresentação, Export HTML/DOCX, Busca, PWA

#### Templates adicionais
- `landing.html` — "Para Ministros de Música e Adoradores", links privacy/terms, meta verificação Google
- `privacy.html` — Política de Privacidade pública
- `terms.html` — Termos de Serviço público

#### Static
- `static/manifest.json` — PWA
- `static/sw.js` — Service Worker stale-while-revalidate

---

### Stack

- **Backend:** Python 3.10+ + Flask
- **Autenticação:** OAuth 2.0 Google (`auth.py`) — obrigatório
- **Armazenamento:** Google Drive API v3 (`drive.py`)
- **Calendar:** Google Calendar API v3
- **Frontend:** HTML + CSS + JS puro em `templates/index.html` (sem frameworks, sem npm)
- **Calendar UI:** FullCalendar 6 via CDN
- **Cache offline:** IndexedDB (`mycifras-offline` / `cifras`)
- **Deploy:** Docker + Gunicorn (1 worker gthread, 4 threads, timeout 180s) + Render.com

---

### Variáveis de ambiente

```env
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
CIFRAS_FOLDER_ID=<pasta-raiz-do-acervo>
FLASK_SECRET_KEY=<string-aleatoria>
EXTERNAL_URL=https://meu-app.onrender.com
GOOGLE_CALENDAR_ID=primary
CALENDAR_KEYWORDS=missa,ensaio,louvor,música,repertório,liturgia,celebração,casamento
OWNER_EMAIL=email@exemplo.com
GOOGLE_SITE_VERIFICATION=<token-search-console>
```

---

### Convenções importantes

- **Acordes** sempre `#5b4b8a` — nunca `#1d4ed8`
- **Sem frameworks JS** — JS puro, sem npm, sem build step
- **`invalidate_library_cache()`** após operações de escrita no Drive (chama bundle automaticamente)
- **`invalidate_bundle_cache()`** após edições de conteúdo de cifras
- **`data-owner` no `<body>`** para passar roles ao JS (não usar Jinja em `<script>`)
- **`escHtml()`** obrigatório ao inserir dados via innerHTML
- **Mobile breakpoint:** `max-width: 1024px`
- **Dropdowns** appendados ao `document.body` com `position: fixed` + `getBoundingClientRect()`
- **Meu Tom:** sempre usar `_myTones[fileId]?.my_key || song.key` ao exibir tom

---

### Próximas funcionalidades sugeridas

- Workspace compartilhado: músico convida outros membros para colaborar no mesmo acervo
- Repertórios por usuário com controle de conflito de escrita
- Planos de assinatura por workspace (SaaS)
