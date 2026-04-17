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

1. **Transposição + tom gravado**: mudar o tom em 1 clique e salvar automaticamente no Drive
2. **Repertórios pessoais**: montagem e organização do setlist de cada músico
3. **Navegação litúrgica**: categorias de Missa e Ministração para encontrar a música certa no contexto certo
4. **Liturgia diária**: integração com a liturgia do dia para preparar o repertório com antecedência
5. **Agenda pessoal**: Google Calendar integrado para acompanhar ensaios, missas e compromissos

O produto é projetado para ser comercializável. Cada músico conecta o próprio Google Drive — não existe repositório central compartilhado.

**Lucas Almeida** é músico litúrgico em Jaraguá do Sul (SC) e criador do produto.

---

### Estado atual do app (v3.0)

O app está **em produção** na Render.com. As seguintes funcionalidades já estão implementadas e funcionando:

#### Backend (`app.py` + `auth.py` + `drive.py`)
- OAuth 2.0 completo com Google (escopos: Drive, Calendar, userinfo)
- Todas as rotas de CRUD de cifras, pastas e repertórios
- `/api/track_view` — visualizações persistidas em `_views.json` no Drive (não mais em arquivo local)
- `/api/calendar` (GET), `/api/calendar/events` (POST/PUT/DELETE) — integração com Google Calendar
- Filtro de palavras-chave via `CALENDAR_KEYWORDS` (insensível a acentos, via `unicodedata.normalize`)
- Cache em memória para biblioteca (`library_cache`) e views (`_views_cache`)
- `get_calendar_service()` em `auth.py`
- `load_views()` / `save_views()` em `drive.py`

#### Frontend (`templates/index.html`)
- Sidebar com seções (sem ícones nas pastas mães) e categorias com ícones
- Home screen com: banner inspiracional, cards de volumetria, seção "Mais tocadas/Destaques" (top 8), liturgia do dia, Google Calendar
- Cards: nome, badge de categoria (tag dourada), badge de tom, contador de views, botão `⋯`
- Campo de busca com botão X para limpar
- Transposição tonal no cliente (JS puro), com **Salvar Tom** que persiste no Drive via `/api/songs/update_meta`
- Inferência automática de tom via `detectBaseNote(text)` quando `key` está vazio nos metadados
- `_refreshCardsForSong(songKey, updates)` — atualiza cards visíveis em tempo real após salvar metadados
- Google Calendar com FullCalendar 6 (CDN), vistas mensal/semanal/diária/lista, CRUD completo, drag-and-drop
- Modal de evento com campos: título, all-day toggle, datetime início/fim, local, descrição
- `_confirmDialog()` — modal de confirmação personalizado
- Painel de metadados editável (título, artista, tom, tags)
- Editor inline com toolbar (selecionar tudo, copiar, duas colunas)
- Modo Apresentação (fullscreen, keyboard navigation)
- Export HTML elegante para impressão

#### Templates adicionais
- `landing.html` — landing page pública com copy voltado para o músico individual
- `login.html` — tela de login OAuth

#### Static
- `static/manifest.json` — PWA para Android/iOS (display: standalone, theme_color: #5b4b8a)
- `static/brand/` — logos SVG + `apple-touch-icon.png`

---

### Stack

- **Backend:** Python 3.10+ + Flask
- **Autenticação:** OAuth 2.0 Google (`auth.py`) — obrigatório
- **Armazenamento:** Google Drive API v3 (`drive.py`) — único backend
- **Calendar:** Google Calendar API v3
- **Frontend:** HTML + CSS + JS puro em `templates/index.html` (sem frameworks, sem npm)
- **Calendar UI:** FullCalendar 6 via CDN
- **Deploy:** Docker + Gunicorn + Render.com

---

### Variáveis de ambiente necessárias

```env
GOOGLE_CLIENT_ID=...apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-...
CIFRAS_FOLDER_ID=<id-da-pasta-raiz-do-músico-no-drive>
FLASK_SECRET_KEY=<string-aleatoria-longa>
EXTERNAL_URL=https://meu-app.onrender.com
GOOGLE_CALENDAR_ID=primary
CALENDAR_KEYWORDS=missa,ensaio,louvor,música,repertório,liturgia,celebração,casamento
```

---

### Convenções importantes

- **Acordes** são sempre `#5b4b8a` — nunca usar `#1d4ed8` (azul)
- **Sem frameworks JS** — JS puro, sem npm, sem build step
- **Dropdowns** sempre appendados ao `document.body` com `position: fixed` + `getBoundingClientRect()`
- **`invalidate_library_cache()`** deve ser chamado após qualquer operação de escrita no Drive
- **Mobile breakpoint:** `max-width: 1024px`
- **Evitar `:hover` com `transform`** no mobile (duplo tap no iOS Safari)
- **`escHtml()`** obrigatório ao inserir dados no DOM via innerHTML

---

### Próximas funcionalidades sugeridas

- Workspace compartilhado: músico convida outros membros para colaborar no mesmo acervo
- Repertórios por usuário (`_rep_{user_id}.json`) para evitar conflitos de escrita simultânea
- Planos de assinatura por workspace (SaaS)

---

### Observações Finais

- Toda mensagem de erro e interface em **português**
- O app não tem modo local — OAuth e Drive são obrigatórios
- Ao reiniciar o servidor, o `load_dotenv()` recarrega as variáveis de ambiente — mudanças no `.env` requerem restart
- Token com escopo antigo (`calendar.readonly`) gera 403 `insufficientPermissions` nas rotas de Calendar — o músico precisa fazer logout + login para reemitir com o escopo `calendar` completo
