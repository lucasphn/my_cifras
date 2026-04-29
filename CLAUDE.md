# CLAUDE.md — My Cifras

Contexto e instruções para o Claude Code trabalhar neste projeto.

---

## O que é este projeto

**My Cifras** é uma aplicação web para o **músico individual** gerenciar seu acervo pessoal de cifras, transpor tons, criar repertórios, compartilhar repertórios com colaboradores e acompanhar a liturgia diária e sua agenda de compromissos.

Stack: **Python 3.10+ · Flask · HTML/CSS/JS puro · python-docx · PyMuPDF · Google Drive API · Google Calendar API · OAuth 2.0 · FullCalendar 6 · Docker · Gunicorn**

Versão atual em produção: **v3.4**

---

## Estrutura do projeto

```
my_cifras/
├── app.py                  ← servidor Flask, rotas, extração de texto, repertórios, shares, export, calendar
├── auth.py                 ← OAuth 2.0 com Google, login_required, get_service, current_user
├── drive.py                ← operações Google Drive (list, download, upload, JSON, pastas, shares)
├── scraper.py              ← scraping de cifras por URL (CifraClub etc.)
├── migrate.py              ← script de migração: .docx/.pdf/.txt → .md
├── requirements.txt
├── Dockerfile              ← Python 3.12-slim, gunicorn 1 worker gthread na porta 8000
├── render.yaml             ← deploy automatizado na Render.com
├── .env                    ← variáveis de ambiente (não versionado)
├── .env.example            ← template comentado
├── _shares.json            ← registro local de compartilhamentos (fallback quando Drive indisponível)
├── templates/
│   ├── index.html          ← toda a UI do app: HTML + CSS + JS em um único arquivo
│   ├── landing.html        ← landing page pública (rota / para não-autenticados); contém botões "Entrar com Google"
│   ├── login.html          ← arquivo mantido mas não usado; /login redireciona para /
│   ├── privacy.html        ← Política de Privacidade (pública)
│   └── terms.html          ← Termos de Serviço (público)
├── static/
│   ├── manifest.json       ← PWA manifest
│   ├── sw.js               ← Service Worker (cache offline)
│   └── brand/              ← logos SVG
└── CLAUDE.md
```

---

## Variáveis de ambiente (.env)

```env
GOOGLE_CLIENT_ID=...apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-...
CIFRAS_FOLDER_ID=<id-da-pasta-raiz>
FLASK_SECRET_KEY=<string-aleatoria-longa>
EXTERNAL_URL=https://meu-app.onrender.com
GOOGLE_CALENDAR_ID=primary
CALENDAR_KEYWORDS=missa,ensaio,louvor,música,repertório,liturgia,celebração,casamento
OWNER_EMAIL=email@exemplo.com,outro@exemplo.com
GOOGLE_SITE_VERIFICATION=<token>
SESSION_FILE_DIR=/tmp/flask_session   # opcional; padrão é tmpdir do SO
```

Se `OWNER_EMAIL` não estiver definido, todos os usuários têm acesso de owner (dev local).

---

## Escopos OAuth

```python
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/calendar.events",
]
```

---

## Controle de acesso por role

```python
# Owner: edita, renomeia, exclui músicas e gerencia pastas
# Viewer: transpõe, salva Meu Tom, cria e compartilha repertórios — apenas leitura do acervo

def is_owner() -> bool:
    if not _OWNER_EMAILS:   # sem ENV → todos são owner (dev local)
        return True
    return current_user().get("email", "").lower() in _OWNER_EMAILS

@owner_required  # decorator aplicado em todas as rotas de escrita do acervo
```

No frontend:
- `<body data-owner="1|0" data-user-email="{{ user.email }}" data-user-name="{{ user.name }}">`
- `var _isOwner = document.body.getAttribute('data-owner') === '1'`
- `document.body.dataset.userEmail` — usado para comparação de e-mails no compartilhamento

---

## Rotas da API

| Método | Rota | Descrição |
|---|---|---|
| GET | `/` | Landing (não autenticado) ou App (autenticado) |
| GET | `/privacy` | Política de Privacidade (pública) |
| GET | `/terms` | Termos de Serviço (público) |
| GET | `/login` | Redireciona para `/` (landing page tem os botões OAuth) |
| GET | `/login/google` | Inicia fluxo OAuth |
| GET | `/oauth/callback` | Callback OAuth do Google |
| GET | `/logout` | Encerra sessão |
| GET | `/sw.js` | Service Worker |
| GET | `/api/me` | Dados do usuário logado + `is_owner` |
| GET | `/api/library` | Estrutura completa da biblioteca |
| GET | `/api/songs` | Lista plana de todas as músicas |
| GET | `/api/cifra?fileId=&mimeType=` | Texto de arquivo no Drive |
| GET | `/api/cifras/bundle` | Bundle completo para sync offline (ETag/304) |
| GET | `/api/search/content?q=` | Busca full-text no Drive |
| POST | `/api/upload` | Upload de arquivo avulso (owner) |
| POST | `/api/export` | Exporta HTML elegante |
| POST | `/api/export/docx` | Exporta DOCX |
| POST | `/api/import/preview` | Scraping de URL → preview |
| POST | `/api/import/save` | Salva cifra como .md (owner) |
| GET | `/api/sections` | Seções e categorias |
| POST | `/api/track_view` | Registra visualização |
| GET | `/api/repertorios` | Lista repertórios salvos |
| POST | `/api/repertorios` | Cria repertório (limite: 5) |
| PUT | `/api/repertorios/<id>` | Atualiza repertório |
| DELETE | `/api/repertorios/<id>` | Exclui repertório |
| **POST** | **`/api/share-rep`** | **Compartilha repertório com outro usuário (via e-mail)** |
| **GET** | **`/api/shares-by-me`** | **Meus compartilhamentos ativos (saída)** |
| **GET** | **`/api/shared-with-me`** | **Repertórios compartilhados comigo (entrada)** |
| **DELETE** | **`/api/share/<id>`** | **Remove compartilhamento (remetente)** |
| **POST** | **`/api/share/<id>/dismiss`** | **Destinatário remove da sua lista** |
| **POST** | **`/api/share/<id>/seen`** | **Marca compartilhamento como visto** |
| **GET** | **`/api/notifications/count`** | **Contagem de notificações não vistas** |
| POST | `/api/folders` | Cria pasta/categoria (owner) |
| PUT | `/api/folders/<section>/<category>` | Renomeia categoria (owner) |
| DELETE | `/api/folders/<section>/<category>` | Exclui categoria (owner) |
| POST | `/api/songs/rename` | Renomeia arquivo (owner) |
| POST | `/api/songs/copy` | Copia arquivo (owner) |
| POST | `/api/songs/move` | Move arquivo (owner) |
| POST | `/api/songs/delete` | Lixeira do Drive (owner) |
| POST | `/api/songs/update_meta` | Atualiza frontmatter YAML (owner) |
| POST | `/api/save_content` | Salva conteúdo editado (owner) |
| GET | `/api/calendar` | Lista eventos |
| POST | `/api/calendar/events` | Cria evento |
| PUT | `/api/calendar/events/<id>` | Atualiza evento |
| DELETE | `/api/calendar/events/<id>` | Exclui evento |
| GET | `/api/preferences` | Meu Tom por música |
| POST | `/api/preferences` | Salva preferência de tom |

---

## Persistência de dados no Drive

### Por usuário (pasta `_mycifras_data/` no Drive de cada usuário)
- `_preferences.json` — Meu Tom por música
- `_repertorios.json` — repertórios pessoais (limite: 5)
- `_views.json` — histórico de visualizações

### Compartilhamentos (registro central)
- `_shares.json` em `CIFRAS_FOLDER_ID` (Drive do owner, lido por todos os usuários)
- Fallback local: `_shares.json` na raiz do projeto
- Estrutura de cada share:
```json
{
  "shr_abc123": {
    "id": "shr_abc123",
    "rep_id": "rpt_xyz",
    "rep_name": "Missa de Domingo",
    "songs": [...],
    "from_email": "lucas@gmail.com",
    "from_name": "Lucas",
    "from_picture": "https://...",
    "to_email": "amigo@gmail.com",
    "shared_at": "2025-01-01T00:00:00",
    "seen_by": [],
    "dismissed_by": []
  }
}
```

### Owner (acervo compartilhado)
- Cifras e pastas em `CIFRAS_FOLDER_ID`

### Caches em memória
```python
_prefs_cache: dict   # { email: { "data": None, "file_id": "..." } }  ← só file_id; data sempre lida do Drive
_views_cache: dict   # { email: { "data": {...}, "file_id": "..." } }
_reps_cache:  dict   # { email: { "data": None, "file_id": "..." } }   ← só file_id; data sempre lida do Drive
_library_cache       # { "data": ..., "ts": float }  — TTL 120s
_bundle_cache        # { "etag": str, "ts": float }  — só ETag
_shares_drive_file_id: str | None  # cache global do file_id do _shares.json
_shares_cache_data: dict | None    # cache em memória para shares (performance do live sharing)
_songs_meta: dict    # metadados globais de músicas (artist, key, capo, youtube) — persiste em _songs_meta.json
```

**Importante:** `_load_prefs()` e `_load_reps()` **não** cacheiam `data` — sempre releem o Drive a cada GET. Apenas `file_id` é cacheado para acelerar writes. Isso garante que alterações feitas em outra instância (ex: produção vs. localhost) sejam sempre visíveis.

### Metadados globais (`_songs_meta.json`)
- Arquivo em `CIFRAS_FOLDER_ID` (acervo do owner)
- Contém `artist`, `key`, `capo`, `youtube` por `fileId`
- Carregado lazy via `_ensure_songs_meta_loaded()` com **TTL de 5 min** (`SONGS_META_TTL = 300`) — re-lê o Drive para sincronizar entre processos/instâncias
- Persistido em background thread via `_persist_songs_meta(svc)` — **`svc` obrigatório**, passado pelo chamador no contexto de request (não chama `get_service()` dentro da thread, pois Flask session não existe fora do request context)
- Todos os callers devem passar `svc`: `_set_song_meta(..., svc=svc)` e `_persist_songs_meta(svc=svc)`
- Bundle endpoint inclui esses metadados para seed do `_metaStore` no cliente

### Invalidação
```python
invalidate_library_cache()  # chama também invalidate_bundle_cache()
invalidate_bundle_cache()   # após save_content e import_save
```

---

## Funções em drive.py

```python
# Listagem e leitura
list_folder(service, folder_id)
scan_library(service, root_folder_id)
download_bytes(service, file_id)
export_gdoc_as_text(service, file_id)
search_content(service, query, root_folder_id, max_results=50)

# JSON por usuário no Drive
load_repertorios / save_repertorios
load_views / save_views
load_preferences / save_preferences
get_user_data_folder(service)       # encontra/cria _mycifras_data

# Compartilhamentos (registro central em CIFRAS_FOLDER_ID)
load_shares(service, root_folder_id)   # retorna (data, file_id)
save_shares(service, file_id, data)

# Upload / update
upload_md(service, name, content, folder_id)
update_md_content(service, file_id, content)

# Arquivo
get_file_name / trash_file / rename_file / copy_file / move_file

# Pastas
find_folder_by_name / create_folder / rename_folder
is_folder_empty / delete_folder / get_or_create_folder / resolve_folder
```

---

## Sessões (Flask-Session)

Sessões server-side com filesystem backend (`Flask-Session==0.8.0`). O cookie contém apenas um ID de sessão assinado (~40 chars), eliminando:
- Problemas de tamanho de cookie (OAuth tokens + dados de usuário)
- Rejeição por ITP do iOS Safari em redirecionamentos OAuth cross-site

```python
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = _session_dir  # env SESSION_FILE_DIR ou tmpdir
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_USE_SIGNER"] = True
```

**Importante:** sessões ficam no filesystem — em ambientes onde o `/tmp` é volátil (ex: reinicialização de container), usuários precisarão re-autenticar. Para persistência entre restarts, configurar `SESSION_FILE_DIR` para volume persistente.

---

## Brand / identidade visual (tema claro — produção)

```css
--bg:          #f7f6fb   /* fundo principal */
--surface:     #ffffff
--surface2:    #eeebf6
--text:        #1f2937
--text-muted:  #6b7280
--primary:     #5b4b8a   /* botões, acordes — SEMPRE este roxo */
--accent:      #d4af37   /* badges dourados */
--border:      #e6e1f0
--danger:      #dc2626
--success:     #16a34a
```

**Acordes sempre `#5b4b8a`. Nunca usar azul `#1d4ed8`.**

---

## Formato de arquivo: `.md` com frontmatter YAML

```markdown
---
title: Além do Véu
artist: Ministério Zoe
key: G
capo: 0
section: Gospel
category: Adoração
youtube: https://youtube.com/watch?v=...
---

G           D          Em
Além do véu eu quero te ver
```

O campo `tags` foi substituído por `youtube` (link opcional para o YouTube da música). O mini-player de áudio é exibido no modal se o link estiver preenchido (iframe `height: 72px` mostra apenas a barra de controles).

---

## Cache offline (IndexedDB)

- Store: `mycifras-offline` / `cifras`
- Chave: `fileId`
- Funções: `_idbGet(fileId)`, `_idbPut(fileId, data)`, `_idbBulkPut(entries)`, `_idbCount()`
- **Cache-first:** abre do IDB imediatamente → atualiza do servidor em background
- **Bundle sync:** `_bundleSync()` dispara 4s após carregamento, cooldown 30 min

---

## Estado JavaScript global

```js
var library = {};
var allSongs = [];
var repertorio = [];
var currentModal = null;
var rawCifraText = "";
var currentSemitone = 0;
var currentCategory = null;
var searchActive = false;
var repOpen = false;
var editMode = false;
var currentRepId = null;       // ID do repertório salvo aberto
var savedReps = {};            // cache local dos repertórios salvos
var sharedWithMe = [];         // repertórios compartilhados comigo
var sharesByMe = {};           // { rep_id: [share, ...] } — meus shares ativos
var currentSharedId = null;    // ID do share compartilhado atualmente aberto
var _shareTargetRepId = null;  // rep sendo compartilhado no diálogo
var _pendingDelete = null;
var _myTones = {};             // { fileId: { my_key, my_capo } }
var _isOwner = false;
var presenterSongs = [];
var presenterIdx = 0;
```

---

## Deploy

### Gunicorn (Dockerfile)
```
gunicorn app:app --bind 0.0.0.0:8000 --workers 1 --worker-class gthread --threads 4 --timeout 180
```

### Render.com
1. Push para o repositório Git
2. Render detecta `render.yaml`
3. Configurar variáveis de ambiente no painel
4. `EXTERNAL_URL + /oauth/callback` como URI autorizada no Google Cloud Console

---

## Convenções de código

### Python
- `invalidate_library_cache()` após operações que alteram pastas/arquivos
- `invalidate_bundle_cache()` após operações que alteram conteúdo de cifras
- Funções de `drive.py` recebem `service` como primeiro parâmetro

### JavaScript
- `refreshGridBtns()` — atualiza apenas botões `.btn-hc-add` com estado diferente (skip se `inRep === wasAdded`)
- `renderSongGrid()` — usa `DocumentFragment` para batch insert (1 reflow em vez de N)
- `renderRepList()` — usa `DocumentFragment` para batch insert
- `openPresenter()` — carrega todas as cifras em **paralelo** com `Promise.all` + IDB-first (não sequencial)
- `openSavedRep()` / `openSharedRep()` — defere `refreshGridBtns` com `requestAnimationFrame`
- `escHtml()` obrigatório ao inserir dados via innerHTML
- `_forceCloseModal()` para fechar modal sem acionar confirm de edição (ex: ao navegar)
- `_closeAllDropdowns()` antes de abrir qualquer dropdown novo
- Sem frameworks — JS puro, sem npm, sem build step

### CSS
- Variáveis CSS em `:root`
- Mobile breakpoint: `@media (max-width: 1024px)`
- iOS safe area: `env(safe-area-inset-bottom, 0px)` sem margem extra acima dela
- `font-size` mínimo de **16px** em todos os inputs mobile (evita zoom automático do iOS Safari)
- Evitar `:hover` com `transform` no mobile (double-tap em iOS)
- `touch-action: manipulation` deve incluir **todos** os elementos interativos, inclusive `.shared-rep-item` (elimina delay 300ms iOS)

### iOS PWA (standalone)
- Detecção: `navigator.standalone === true` → adiciona `html.pwa-standalone` via script inline no `<head>` (antes do CSS)
- `@media (display-mode: standalone)` é pouco confiável no iOS Safari — preferir `html.pwa-standalone`
- Focus mode: `html.pwa-standalone #modal.focus-mode #modal-body { padding-top: env(safe-area-inset-top) }` — necessário pois `#modal-header` é ocultado
- `-webkit-fill-available` apenas dentro de `@media (max-width: 1024px)` — **não** global (quebra layout desktop)

### Modo Apresentação (Presenter)

Layout de 5 zonas: `#presenter-topbar` (nav) → `#presenter-head` (título/artista) → `#presenter-body` (cifra) → `#presenter-footer` (controles) → `.pr-progress-bar` (base).

CSS tokens em `#presenter-overlay` com variante dark via `[data-pr-dark="1"]`.

**Modo foco** (`pr-focus`): oculta topbar + head. Ativado pelo botão fullscreen em mobile/tablet. Saída pelo `.pr-unfocus-btn` flutuante.

**Swipe lateral**: `touchstart` verifica se target está dentro de `#presenter-song-controls` — se sim, não ativa navegação (evita conflito com scroll horizontal da toolbar).

**Auto-scroll**: `_presenterScrollTimer` a 40ms, para no fim do conteúdo e ao navegar.

**Tema**: persiste em `localStorage('mycifras:presenter-theme')`. Ícones SVG trocam entre lua/sol.

### YouTube nos cards mobile
- `_makeHomeCard()` renderiza `.hc-yt-link` quando `song.youtube` está populado
- `song.youtube` é populado via bundle sync (`_bundleSync`) que roda 4s após carregamento
- No modal, `_showYtPlayer(url)` controla `#mt-yt-link` na barra de tons
