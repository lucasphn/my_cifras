# Prompt Inicial — My Cifras

> **Como usar:** Coloque este arquivo, o `CLAUDE.md` e o `PRD.md` na pasta `my_cifras`.
> Abra o terminal nessa pasta, inicie o Claude Code e cole o conteúdo abaixo.

---

## PROMPT

Você é um desenvolvedor Python + JavaScript experiente. Vamos evoluir a aplicação web **"My Cifras"** — uma ferramenta para o **músico individual** gerenciar seu acervo pessoal de cifras, transpor tons, criar e compartilhar repertórios, e acompanhar sua agenda litúrgica.

**Antes de escrever qualquer código, leia completamente os arquivos `CLAUDE.md` e `PRD.md` nesta pasta.** Eles têm todas as especificações, convenções e regras do projeto.

---

### Contexto

**My Cifras** é um produto para o músico litúrgico e gospel. Não é um app de grupo — é uma ferramenta individual que também permite colaboração pontual via compartilhamento de repertórios. O valor central está em:

1. **Transposição + Meu Tom:** muda o tom em 1 clique e salva no Drive do próprio usuário
2. **Repertórios pessoais e compartilhados:** montagem, organização e compartilhamento do setlist
3. **Mini-player YouTube:** link da música no metadado, player de áudio inline no modal
4. **Navegação litúrgica:** categorias de Missa e Ministração para encontrar a música certa
5. **Liturgia diária:** integração com a liturgia do dia
6. **Agenda pessoal:** Google Calendar integrado para ensaios, missas e compromissos

**Lucas Almeida** é músico litúrgico em Jaraguá do Sul (SC) e criador do produto.

---

### Estado atual do app (v3.2)

O app está **em produção** na Render.com. As seguintes funcionalidades já estão implementadas:

#### Backend (`app.py` + `auth.py` + `drive.py`)

- OAuth 2.0 completo com Google (escopos: `drive`, `calendar.events`, `userinfo`)
- **Roles:** `OWNER_EMAIL` no env define owners; sem ENV → todos são owner (dev local)
- **Dados por usuário:** prefs, repertórios e views em `_mycifras_data` no Drive de cada usuário
- **Bundle sync:** `GET /api/cifras/bundle` com ETag/304; build paralelo 4 workers
- **Cache de biblioteca:** TTL 120s
- CRUD completo de cifras, pastas, repertórios e eventos de calendário
- Limite de 5 repertórios por usuário
- **Compartilhamento de repertórios:**
  - `POST /api/share-rep` — compartilha via e-mail
  - `GET /api/shares-by-me` — meus shares ativos
  - `GET /api/shared-with-me` — recebidos por mim (filtra dispensados)
  - `DELETE /api/share/<id>` — remetente remove
  - `POST /api/share/<id>/dismiss` — destinatário dispensa
  - `POST /api/share/<id>/seen` — marca como visto
  - `GET /api/notifications/count` — badge do sino
  - Armazenamento: `_shares.json` em `CIFRAS_FOLDER_ID` com fallback local
- **Metadados:** campo `youtube` (substituiu `tags`) no frontmatter YAML
- Páginas públicas: `/privacy`, `/terms`
- Service Worker em `/sw.js`

#### Frontend (`templates/index.html`)

- **Tema claro**: `--bg: #f7f6fb`, `--primary: #5b4b8a`, `--accent: #d4af37`
- `<body data-owner="1|0" data-user-email="..." data-user-name="...">`
- Botões de admin visíveis apenas para owners
- **Cache-first:** abre cifra do IDB imediatamente → atualiza em background
- **Bundle sync:** `_bundleSync()` com cooldown 30 min
- **Meu Tom:** `_myTones[fileId] = { my_key, my_capo }` — exibido nos cards, export e apresentação
- **Mini-player YouTube:** iframe `height: 72px` no modal (só barra de controles); para ao fechar
- **Cards "Explorar por categoria":** grid responsivo no padrão dos cards de destaque (ícone + nome + tags)
- **Navegação auto-close:** clicar em pasta ou Início fecha modal de cifra aberto
- **Compartilhamento:**
  - Menu `⋯` nos saved-rep items (substituiu o botão ✕)
  - Opções: Compartilhar, Gerenciar compartilhamentos, Excluir
  - Sino no header com badge de notificações não vistas
  - Painel de notificações ao clicar no sino
  - Seção "COMPARTILHADOS COMIGO" abaixo de "SALVOS" no painel
  - Tag "Compartilhado" discreta nos repertórios com shares ativos
- **`_forceCloseModal()`** — fecha modal sem confirm (usado em navegação)
- **`_closeAllDropdowns()`** — fecha menus antes de abrir outro
- Google Calendar com FullCalendar 6, CRUD completo, drag-and-drop
- Modo Apresentação, Export HTML/DOCX, Busca, PWA
- **iOS/Android:**
  - `font-size: 16px` em todos os inputs (evita zoom automático do iOS Safari)
  - Bottom nav: `bottom: env(safe-area-inset-bottom, 6px)` (sem margem extra acima da safe area)
  - Modal footer: `padding-bottom: calc(env(safe-area-inset-bottom, 0px) + 14px)`
  - `#app` usa `min-height: 100dvh` (evita o bug do `100vh` no Safari)

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

- **Tema claro** — `--bg: #f7f6fb`, `--primary: #5b4b8a`, `--accent: #d4af37`
- **Acordes** sempre `#5b4b8a` — nunca `#1d4ed8`
- **Sem frameworks JS** — JS puro, sem npm, sem build step
- **`invalidate_library_cache()`** após operações de escrita no Drive
- **`invalidate_bundle_cache()`** após edições de conteúdo de cifras
- **`data-owner` e `data-user-email` no `<body>`** para passar contexto ao JS (não usar Jinja em `<script>`)
- **`escHtml()`** obrigatório ao inserir dados via innerHTML
- **Mobile breakpoint:** `max-width: 1024px`
- **iOS safe area:** `env(safe-area-inset-bottom, 0px)` — sem margem extra acima da safe area
- **`font-size` mínimo 16px** em inputs mobile — abaixo disso o iOS Safari faz zoom ao focar

---

### Próximas funcionalidades sugeridas

- Workspace colaborativo: múltiplos owners editando o mesmo acervo
- Notificações push para novos compartilhamentos
- Planos de assinatura por workspace (SaaS)
- Histórico de versões de cifras
