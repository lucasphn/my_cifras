# CLAUDE.md — My Cifras

Contexto e instruções para o Claude Code trabalhar neste projeto.

---

## O que é este projeto

**My Cifras** é uma aplicação web para o **músico individual** gerenciar seu acervo pessoal de cifras, transpor tons, criar repertórios e acompanhar a liturgia diária e sua agenda de compromissos.

O produto é projetado para ser vendável: resolve a dor real do músico litúrgico e gospel — encontrar e transpor cifras rapidamente, gravar o tom preferido, organizar o repertório pessoal e se localizar nas categorias de ministração e missa. O Drive do próprio usuário é o backend de armazenamento.

Stack: **Python 3.10+ · Flask · HTML/CSS/JS puro · python-docx · PyMuPDF · Google Drive API · Google Calendar API · OAuth 2.0 · FullCalendar 6 · Docker · Gunicorn**

---

## Estrutura do projeto

```
my_cifras_pc_owner/
├── app.py                  ← servidor Flask, rotas, extração de texto, repertórios, export, calendar
├── auth.py                 ← OAuth 2.0 com Google, login_required, get_service, get_calendar_service
├── drive.py                ← operações Google Drive (list, download, upload, JSON, pastas, arquivos, busca, views)
├── scraper.py              ← scraping de cifras por URL (CifraClub etc.)
├── migrate.py              ← script de migração: .docx/.pdf/.txt → .md
├── requirements.txt
├── Dockerfile              ← Python 3.12-slim, gunicorn na porta 8000
├── render.yaml             ← deploy automatizado na Render.com
├── .env                    ← variáveis de ambiente (não versionado)
├── .env.example            ← template comentado
├── .gitignore
├── templates/
│   ├── index.html          ← toda a UI do app: HTML + CSS + JS em um único arquivo
│   ├── landing.html        ← landing page pública (rota /)
│   └── login.html          ← tela de login OAuth
├── static/
│   ├── manifest.json       ← PWA manifest (Android/iOS home screen)
│   └── brand/              ← logos SVG do My Cifras
│       ├── favicon.svg
│       ├── icon.svg
│       ├── logo-dark.svg           ← para fundos escuros (landing, login)
│       ├── logo-light.svg          ← para fundos claros (header do app)
│       ├── logo-mono-dark.svg      ← monocromático roxo (export HTML, impressão)
│       ├── logo-mono-white.svg     ← monocromático branco (banners escuros)
│       └── apple-touch-icon.png    ← ícone 180×180 para atalho iOS e Android
├── assets/
│   └── mycifras-logo/      ← arquivos fonte dos logos + brand-tokens.css
└── CLAUDE.md
```

### Onde cada coisa vive

- **Rotas e lógica de servidor** → `app.py`
- **Autenticação OAuth** → `auth.py` (Blueprint Flask `auth`)
- **Operações Drive** → `drive.py` (funções puras, recebem `service` como parâmetro)
- **Repertórios JSON** → `drive.py` (`load_repertorios`, `save_repertorios`) — arquivo `_repertorios.json` no Drive
- **Views (contagem de visualizações)** → `drive.py` (`load_views`, `save_views`) — arquivo `_views.json` no Drive
- **Extração de texto** (.docx, .pdf, .txt, .md) → funções `_*_from_bytes` em `app.py`
- **Scraping de URL** → `scraper.py`
- **UI, estilos e interatividade do app** → `templates/index.html` (tudo junto)
- **Landing page pública** → `templates/landing.html`
- **Transposição tonal** → JavaScript no cliente, dentro de `index.html`
- **Modo Apresentação** → JavaScript no cliente, dentro de `index.html`
- **PWA** → `static/manifest.json` + `<link rel="manifest">` em todos os templates

---

## Variáveis de ambiente (.env)

```env
# OAuth 2.0 (obrigatório)
GOOGLE_CLIENT_ID=...apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-...

# Pasta raiz de cifras do músico no Drive
CIFRAS_FOLDER_ID=<id-da-pasta-raiz>

# Flask
FLASK_SECRET_KEY=<string-aleatoria-longa>

# Deploy (Render, ngrok, etc.)
EXTERNAL_URL=https://meu-app.onrender.com

# Google Calendar
GOOGLE_CALENDAR_ID=primary

# Filtro de palavras-chave para o calendário (opcional)
# Apenas eventos cujo título contenha ao menos uma das palavras são exibidos.
# Deixar em branco para exibir todos os eventos.
CALENDAR_KEYWORDS=missa,ensaio,louvor,música,repertório,liturgia,celebração,casamento
```

**O app requer Drive e OAuth.** `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` e `CIFRAS_FOLDER_ID` são obrigatórios.

---

## Escopos OAuth

```python
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/calendar",   # leitura e escrita no Calendar
]
```

**Atenção:** o escopo `calendar` (não `calendar.readonly`) é necessário para criar/editar/excluir eventos. Se o token foi gerado com o escopo antigo, o usuário precisa fazer logout + login para que o Google reemita com os escopos corretos.

---

## Rotas da API

| Método | Rota | Descrição |
|---|---|---|
| GET | `/` | Landing page pública (`landing.html`) |
| GET | `/` | Landing (não autenticado) ou App principal (autenticado) |
| GET | `/login` | Tela de login |
| GET | `/login/google` | Inicia fluxo OAuth |
| GET | `/oauth/callback` | Callback OAuth do Google |
| GET | `/logout` | Encerra sessão |
| GET | `/api/me` | Dados do usuário logado |
| GET | `/api/library` | Estrutura completa da biblioteca (JSON) |
| GET | `/api/songs` | Lista plana de todas as músicas |
| GET | `/api/cifra?fileId=&mimeType=` | Texto de arquivo no Drive — retorna `{ text, key, name, title, tags }` |
| GET | `/api/search/content?q=` | Busca full-text no Drive (`fullText contains`) |
| POST | `/api/upload` | Upload de arquivo avulso, retorna texto |
| POST | `/api/export` | Recebe lista de músicas, retorna HTML elegante com logo inline |
| POST | `/api/import/preview` | Scraping de URL ou texto colado → `{ title, artist, key, text }` |
| POST | `/api/import/save` | Salva cifra como .md no Drive |
| GET | `/api/sections` | Seções e categorias disponíveis |
| POST | `/api/track_view` | Registra visualização de uma música (persiste em `_views.json` no Drive) |
| GET | `/api/repertorios` | Lista todos os repertórios salvos |
| POST | `/api/repertorios` | Cria novo repertório → 201 + objeto |
| PUT | `/api/repertorios/<id>` | Atualiza repertório existente |
| DELETE | `/api/repertorios/<id>` | Exclui repertório |
| POST | `/api/folders` | Cria nova pasta/categoria no Drive |
| PUT | `/api/folders/<section>/<category>` | Renomeia categoria |
| DELETE | `/api/folders/<section>/<category>` | Exclui categoria (somente se vazia) |
| POST | `/api/songs/rename` | Renomeia arquivo de cifra |
| POST | `/api/songs/copy` | Copia arquivo para outra categoria |
| POST | `/api/songs/move` | Move arquivo para outra categoria |
| POST | `/api/songs/delete` | Envia arquivo para lixeira do Drive |
| POST | `/api/songs/update_meta` | Atualiza apenas o frontmatter YAML de um `.md` |
| GET | `/api/calendar` | Lista eventos do Google Calendar (`?start=&end=`) |
| POST | `/api/calendar/events` | Cria novo evento no Calendar |
| PUT | `/api/calendar/events/<id>` | Atualiza evento existente |
| DELETE | `/api/calendar/events/<id>` | Exclui evento |

Todas as rotas são protegidas por `@login_required`.

---

## Funções em drive.py

```python
# Listagem e leitura
list_folder(service, folder_id)               # lista { id, name, mimeType }
scan_library(service, root_folder_id)         # escaneia estrutura completa
download_bytes(service, file_id)              # retorna bytes raw
export_gdoc_as_text(service, file_id)         # exporta Google Doc como texto

# Busca
search_content(service, query, root_folder_id, max_results=50)
  # fullText contains; retorna [{ fileId, name, mimeType, excerpt }]
  # ATENÇÃO: não usa orderBy (incompatível com fullText na Drive API)

# Repertórios JSON
load_repertorios(service, root_folder_id)     # retorna (data, file_id)
save_repertorios(service, file_id, data)

# Views JSON (persistência no Drive)
load_views(service, root_folder_id)           # retorna (data, file_id) — arquivo _views.json
save_views(service, file_id, data)

# Upload / update
upload_md(service, name, content, folder_id) # cria .md; retorna file_id
update_md_content(service, file_id, content) # atualiza .md existente

# Arquivo
get_file_name(service, file_id)               # retorna nome com extensão
trash_file(service, file_id)                  # lixeira do Drive
rename_file(service, file_id, new_name_with_ext)
copy_file(service, file_id, new_name, target_folder_id)
move_file(service, file_id, source_folder_id, target_folder_id)

# Pastas
find_folder_by_name(service, name, parent_id)
create_folder(service, name, parent_id)
rename_folder(service, folder_id, new_name)
is_folder_empty(service, folder_id)           # bool
delete_folder(service, folder_id)
get_or_create_folder(service, name, parent_id)
resolve_folder(service, section, category, root_folder_id)
```

---

## Brand / identidade visual

**Paleta:**
```css
--primary:     #5b4b8a   /* roxo principal — botões, links, destaques, ACORDES */
--accent:      #d4af37   /* dourado — badges, ênfases */
--bg:          #0f0e17
--surface:     #13111e
--surface2:    #1c1929
--text:        #e8e6f0
--text-muted:  #9b97b0
```

**Acordes** são sempre `#5b4b8a`. Nunca usar azul `#1d4ed8` para acordes.

**Logos:** usar sempre o arquivo correto para o contexto:
- `logo-dark.svg` → landing, login (fundo escuro)
- `logo-light.svg` → header do app (fundo claro)
- `logo-mono-dark.svg` → export HTML impresso (inline como SVG)
- `favicon.svg` → `<link rel="icon">` em todos os templates
- `apple-touch-icon.png` → `<link rel="apple-touch-icon">` em todos os templates (180×180)

---

## Formato de arquivo preferido: `.md` com frontmatter YAML

```markdown
---
title: Além do Véu
artist: Ministério Zoe
key: G
section: Gospel
category: Adoração
tags: []
---

G           D          Em
Além do véu eu quero te ver
```

O frontmatter é removido automaticamente antes de exibir a cifra na UI.
`/api/songs/update_meta` atualiza apenas o frontmatter, preservando o corpo da cifra.

**Inferência de tom:** quando o campo `key` nos metadados estiver vazio, o frontend usa `detectBaseNote(text)` para detectar automaticamente o tom a partir da primeira linha de acordes da cifra.

**Salvar tom (saveTone):** ao usar o controle de transposição e clicar "Salvar Tom", o novo tom é persistido automaticamente no frontmatter via `/api/songs/update_meta` — não apenas no localStorage.

---

## Persistência de dados no Drive

### Repertórios (`_repertorios.json`)
```json
{
  "rpt_abc123": {
    "id": "rpt_abc123",
    "name": "Missa Domingo",
    "songs": [{ "name": "...", "fileId": "...", "mimeType": "...", "section": "...", "category": "..." }],
    "created_at": "2026-04-09T10:00:00",
    "updated_at": "2026-04-09T11:30:00"
  }
}
```

### Views (`_views.json`)
```json
{
  "<fileId-ou-path>": <número-de-visualizações>
}
```

Ambos os arquivos ficam na raiz de `CIFRAS_FOLDER_ID`. Em memória, `_views_cache = {"data": None, "file_id": None}` evita chamadas à Drive API a cada page load.

### Backend (`app.py`)
- `_load_reps()` / `_save_reps(data)` — carrega e salva repertórios via Drive
- `_load_views()` / `_save_views(data)` — carrega e salva views via Drive
- `_rep_lock` / `_views_lock` (threading.Lock) — evita race conditions em escrita

### Frontend (JS em `index.html`)
- `savedReps` — cache local de repertórios
- `_metaStore` (localStorage key `_mc2`) — cache client-side de metadados
- `_refreshCardsForSong(songKey, updates)` — atualiza cards visíveis sem recarregar a página

---

## Export de repertório (`/api/export`)

O HTML gerado é elegante e otimizado para impressão:
- Logo `logo-mono-dark.svg` inlineado no `<head>` (lido do disco em `static/brand/`)
- Fonte JetBrains Mono para o corpo da cifra
- Fonte Sora para cabeçalhos
- Cores dos acordes: `#5b4b8a` (não usar azul `#1d4ed8`)
- Cards por música com badges de categoria e tom
- `@media print` otimizado

Payload recebido do frontend:
```javascript
{ title, songs: [{ name, text, category, section, key }] }
```

---

## Sidebar do app

- Item "Início" fixado no topo da sidebar (`#sidebar-home-item`)
- Seções com nomes apenas (sem ícones nas seções mães)
- Categorias com ícones em `CAT_ICONS`
- Botão `＋` por seção: cria nova pasta inline
- Botão `⋯` por categoria: abre dropdown (renomear / excluir)
- Dropdowns appendados ao `document.body` com `position: fixed` + `getBoundingClientRect()` para escapar de `overflow: hidden` e `transform` nos cards

---

## Home screen

- Banner de citação inspiracional (`.home-quote`) acima das seções de músicas
- **Cards de volumetria** (`#home-stats-row`): quantidade total de músicas + uma por seção, distribuídos horizontalmente com `flex: 1` (mobile: primeiro ocupa linha inteira, demais 50%)
- **Seção "Mais tocadas" / "Destaques"** (músicas com views > 0 ou todas se nenhuma foi tocada, máx. 8 cards)
- Cards com: nome, badge de categoria (estilo tag dourada), badge de tom, contador de views (olhinho), botão `⋯`
- `_makeHomeCard(song, cls)` — fábrica de card reutilizada em home e grade de categoria
- `_songWithViews(song)` — enriquece músicas com views/key de `allSongs`
- `_refreshCardsForSong(songKey, updates)` — atualiza cards em tempo real após salvar metadados

---

## Liturgia do Dia

Seção na home screen que exibe a liturgia diária do dia atual (API externa).
- Título "Liturgia do Dia" acima dos botões de atalho (não ao lado)
- Botões de atalho (leituras, salmo, evangelho) preenchem a largura disponível
- Controles de navegação de data à direita

---

## Google Calendar

Seção na home screen abaixo dos destaques, com visualização FullCalendar 6.

### Frontend
- FullCalendar 6 via CDN: `https://cdn.jsdelivr.net/npm/fullcalendar@6.1.11/index.global.min.js`
- Vistas: mensal, semanal, diária, lista
- Header toolbar: `left: "prev,next today"`, `center: "title"`, `right: "dayGridMonth,timeGridWeek,timeGridDay,listMonth"`
- Tema escuro via CSS `#fc-wrap .fc-*`
- CRUD completo: clicar em evento abre modal de edição; clicar em slot vazio abre modal de criação; drag-and-drop e resize persistem
- `_confirmDialog()` — modal de confirmação personalizado (substitui `confirm()` do browser)

### Modal de evento
- `#event-modal-overlay` com campos: título, toggle all-day, datetime início/fim, local, descrição
- Botão "Excluir" com confirmação antes de deletar

### Backend (`app.py`)
```python
GET  /api/calendar?start=&end=   # lista eventos filtrados por keyword
POST /api/calendar/events         # cria evento
PUT  /api/calendar/events/<id>    # atualiza evento
DELETE /api/calendar/events/<id>  # exclui evento
```

### Filtro de palavras-chave
```python
def _calendar_keywords():
    raw = os.environ.get("CALENDAR_KEYWORDS", "").strip()
    if not raw: return []
    import unicodedata
    def _norm(s): return unicodedata.normalize("NFD", s).encode("ascii","ignore").decode().lower()
    return [_norm(k.strip()) for k in raw.split(",") if k.strip()]
```
Comparação insensível a acentos e maiúsculas. Deixar `CALENDAR_KEYWORDS` em branco exibe todos os eventos.

---

## PWA (Progressive Web App)

- `static/manifest.json` — define nome, ícones, `display: standalone`, `start_url: /`, `scope: /`, `theme_color: #5b4b8a`
- `<link rel="manifest" href="/static/manifest.json">` em todos os templates (landing, login, index)
- `<meta name="theme-color" content="#5b4b8a">` em todos os templates
- `apple-touch-icon.png` (180×180) para iOS
- No Android, o Chrome exibe banner "Adicionar à tela inicial" automaticamente

---

## Busca

Dois modos controlados por `#search-mode-toggle`:
- **Nome** (padrão): filtra `allSongs` localmente pelo nome; campo com botão X de limpar
- **Letra**: chama `GET /api/search/content?q=` → Drive `fullText contains`

A busca por letra não suporta `orderBy` na Drive API — não usar `orderBy` em `search_content()`.

---

## Modal de cifra

- Zoom, fullscreen, transposição tonal
- Inferência automática de tom: se `key` estiver vazio nos metadados, usa `detectBaseNote(text)` para detectar da cifra
- Painel de metadados (`#meta-panel`): título, artista, tom, tags — editável inline
- Modo de edição: `#modal-body.edit-mode` com `#edit-toolbar`
  - Toolbar: Selecionar tudo (`etb-select-all`), Copiar (`etb-copy`), Duas colunas (`etb-two-col`)
  - `_confirmLeaveEdit()` — confirma antes de sair se o conteúdo foi alterado
- `#cifra-content.two-col { column-count: 2 }` — vista em duas colunas

---

## Modo Apresentação

### Fluxo
1. Botão ▶ em "Meus Repertórios" → `openPresenter(repId)`
2. Carrega todas as cifras via `/api/cifra` em loop
3. Renderiza tela cheia com `_renderPresenterSong()`
4. Navegação: botões, dots, teclado

### Controles de teclado
| Tecla | Ação |
|---|---|
| `→` / `↓` / `PageDown` | Próxima cifra |
| `←` / `↑` / `PageUp` | Cifra anterior |
| `+` / `=` | Zoom in |
| `-` | Zoom out |
| `F` | Toggle fullscreen |
| `Esc` | Fechar apresentação |

---

## Extração de texto

| Formato | Biblioteca | Observação |
|---|---|---|
| `.docx` | `python-docx` | Lê parágrafos **e tabelas** em ordem de documento |
| `.pdf` | `PyMuPDF` | Stream de bytes direto |
| `.txt` / `.md` | built-in | Strip de frontmatter automático |
| Google Docs | Drive export API | Exporta como `text/plain` |

---

## Lógica de transposição

Roda inteiramente no cliente (JS), sem chamar o servidor.

1. `rawCifraText` guarda o texto original ao abrir o modal
2. `transposeText(text, semitones)` processa linha a linha
3. Linha é "linha de acordes" se ≥ 50% das palavras batem com o regex de acorde
4. Apenas linhas de acordes são transpostas — a letra é preservada

**Notas:** C, C#, D, D#, E, F, F#, G, G#, A, A#, B
**Enarmônicos normalizados:** Db→C#, Eb→D#, Gb→F#, Ab→G#, Bb→A#

---

## Convenções de código

### Python
- Funções de extração retornam `str` sempre — nunca levantam exceção para o caller
- Funções de `drive.py` recebem `service` como primeiro parâmetro (sem estado global)
- `auth.get_service()` obtém o Drive service autenticado da sessão Flask atual
- `auth.get_calendar_service()` obtém o Calendar service autenticado da sessão Flask atual
- `invalidate_library_cache()` deve ser chamado após qualquer operação que altere pastas ou arquivos
- Nomes em português onde fazem sentido para o domínio

### JavaScript (dentro do index.html)
- Estado global: `library`, `allSongs`, `repertorio`, `currentModal`, `rawCifraText`, `currentSemitone`, `currentRepId`, `savedReps`, `presenterSongs`, `presenterIdx`, `_openCatMenu`, `_openSongMenu`, `_twoColMode`, `_fcInstance`
- Músicas do Drive têm `fileId` + `mimeType` (não existe mais o campo `path`)
- `escHtml()` obrigatório ao inserir dados no DOM via innerHTML
- Dropdowns appendados ao `document.body` com `position: fixed` + `getBoundingClientRect()`
- `closeCatMenu()` / `closeOpenSongMenu()` chamados antes de abrir qualquer novo menu
- `_refreshCardsForSong(songKey, updates)` — atualiza cards visíveis sem reload de página
- Sem frameworks — JS puro, sem npm, sem build step

### CSS
- Variáveis CSS em `:root`: `--bg`, `--surface`, `--surface2`, `--text`, `--accent`, `--border`, `--primary`
- Classes em kebab-case: `.home-card`, `.btn-hc-open`, `.cat-dropdown`, `.song-ops-dropdown`
- Mobile breakpoint: `@media (max-width: 1024px)` (cobre celulares e tablets de até 10")
- iOS: evitar `:hover` com `transform` no mobile — causa duplo tap no Safari

---

## Deploy

### Docker local
```bash
docker build -t my-cifras .
docker run -p 8000:8000 --env-file .env my-cifras
```

### Render.com
1. Push para o repositório Git
2. Criar Web Service na Render apontando para o repo
3. Render detecta `render.yaml` automaticamente (runtime Docker, porta 8000)
4. Configurar variáveis de ambiente no painel da Render
5. Adicionar `EXTERNAL_URL + /oauth/callback` como URI autorizada no Google Cloud Console
6. Adicionar `EXTERNAL_URL` no painel da Render

**Nota:** a variável `CALENDAR_KEYWORDS` deve ser configurada na Render para que o filtro funcione em produção. O servidor precisa ser reiniciado após qualquer mudança de variáveis de ambiente (o `load_dotenv()` só roda na inicialização).

---

## Controle de acesso (OAuth)

- **Usuários de teste:** Google Cloud Console → Tela de permissão OAuth → Usuários de teste
- **Acesso às cifras:** cada músico usa sua própria pasta no Drive (`CIFRAS_FOLDER_ID` é configurada por instância do app)
- **Token expirado (7 dias em modo teste):** app detecta `invalid_grant` e redireciona ao login
- **Escopo Calendar:** requer `https://www.googleapis.com/auth/calendar` e precisa estar habilitado na Tela de Permissão OAuth do Google Cloud Console

---

## Visão do produto

My Cifras é um produto voltado para o **músico individual** — não para o grupo. O valor está em:

1. **Transposição + tom gravado**: muda o tom em 1 clique e salva no Drive para não perder
2. **Repertórios pessoais**: montagem e organização do setlist de cada músico
3. **Navegação litúrgica**: categorias de Missa e Ministração para localizar músicas no contexto certo
4. **Liturgia diária**: integração com a liturgia do dia para preparar o repertório com antecedência
5. **Agenda pessoal**: Google Calendar integrado para acompanhar ensaios, missas e outros compromissos

### Evolução prevista

| Fase | Descrição |
|---|---|
| Atual | App individual — um músico, uma conta Google, uma pasta Drive |
| Próxima | Workspace compartilhado — músico convida outros membros para colaborar no mesmo acervo |
| Futura | Multi-workspace — suporte a N grupos/igrejas; administração de membros e permissões |
