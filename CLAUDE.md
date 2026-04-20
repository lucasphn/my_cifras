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
├── Dockerfile              ← Python 3.12-slim, gunicorn 1 worker gthread na porta 8000
├── render.yaml             ← deploy automatizado na Render.com
├── .env                    ← variáveis de ambiente (não versionado)
├── .env.example            ← template comentado
├── .gitignore
├── templates/
│   ├── index.html          ← toda a UI do app: HTML + CSS + JS em um único arquivo
│   ├── landing.html        ← landing page pública (rota /)
│   ├── login.html          ← tela de login OAuth
│   ├── privacy.html        ← Política de Privacidade (pública, para Google OAuth)
│   └── terms.html          ← Termos de Serviço (público)
├── static/
│   ├── manifest.json       ← PWA manifest (Android/iOS home screen)
│   ├── sw.js               ← Service Worker (cache offline, stale-while-revalidate)
│   └── brand/              ← logos SVG do My Cifras
│       ├── favicon.svg
│       ├── icon.svg
│       ├── logo-dark.svg
│       ├── logo-light.svg
│       ├── logo-mono-dark.svg
│       ├── logo-mono-white.svg
│       └── apple-touch-icon.png
├── assets/
│   └── mycifras-logo/
└── CLAUDE.md
```

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
CALENDAR_KEYWORDS=missa,ensaio,louvor,música,repertório,liturgia,celebração,casamento

# Controle de acesso por role (e-mails owners separados por vírgula)
OWNER_EMAIL=email@exemplo.com,outro@exemplo.com

# Google Search Console (meta tag de verificação de domínio)
GOOGLE_SITE_VERIFICATION=<token>
```

**O app requer Drive e OAuth.** `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` e `CIFRAS_FOLDER_ID` são obrigatórios.

Se `OWNER_EMAIL` não estiver definido (desenvolvimento local), todos os usuários têm acesso de owner — comportamento compatível com versões anteriores.

---

## Escopos OAuth

```python
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/calendar.events",  # leitura e escrita de eventos
]
```

**Atenção:** o escopo `calendar.events` (não `calendar.readonly` nem `calendar` completo) cobre criar/editar/excluir eventos. Se o token foi gerado com escopo antigo, o usuário precisa fazer logout + login.

---

## Controle de acesso por role

```python
# Owner: pode editar, renomear, excluir músicas e gerenciar pastas
# Viewer: pode transpor, salvar Meu Tom, criar repertórios — apenas leitura do acervo

def is_owner() -> bool:
    if not _OWNER_EMAILS:   # sem ENV → todos são owner (dev local)
        return True
    return current_user().get("email", "").lower() in _OWNER_EMAILS

@owner_required  # decorator aplicado em todas as rotas de escrita
```

No frontend, `<body data-owner="1|0">` e `var _isOwner = document.body.getAttribute('data-owner') === '1'` controlam a exibição de botões de admin.

---

## Rotas da API

| Método | Rota | Descrição |
|---|---|---|
| GET | `/` | Landing (não autenticado) ou App principal (autenticado) |
| GET | `/privacy` | Política de Privacidade (pública) |
| GET | `/terms` | Termos de Serviço (público) |
| GET | `/login` | Tela de login |
| GET | `/login/google` | Inicia fluxo OAuth |
| GET | `/oauth/callback` | Callback OAuth do Google |
| GET | `/logout` | Encerra sessão |
| GET | `/sw.js` | Service Worker (header Service-Worker-Allowed: /) |
| GET | `/api/me` | Dados do usuário logado + campo `is_owner` |
| GET | `/api/library` | Estrutura completa da biblioteca (JSON) |
| GET | `/api/songs` | Lista plana de todas as músicas |
| GET | `/api/cifra?fileId=&mimeType=` | Texto de arquivo no Drive |
| GET | `/api/cifras/bundle` | Todas as cifras em JSON único para sync offline (ETag/304) |
| GET | `/api/search/content?q=` | Busca full-text no Drive |
| POST | `/api/upload` | Upload de arquivo avulso (owner) |
| POST | `/api/export` | Exporta HTML elegante (PDF-ready) |
| POST | `/api/export/docx` | Exporta DOCX |
| POST | `/api/import/preview` | Scraping de URL → preview |
| POST | `/api/import/save` | Salva cifra como .md no Drive (owner) |
| GET | `/api/sections` | Seções e categorias |
| POST | `/api/track_view` | Registra visualização |
| GET | `/api/repertorios` | Lista repertórios salvos |
| POST | `/api/repertorios` | Cria repertório (limite: 5 por usuário) |
| PUT | `/api/repertorios/<id>` | Atualiza repertório |
| DELETE | `/api/repertorios/<id>` | Exclui repertório |
| POST | `/api/folders` | Cria pasta/categoria (owner) |
| PUT | `/api/folders/<section>/<category>` | Renomeia categoria (owner) |
| DELETE | `/api/folders/<section>/<category>` | Exclui categoria (owner) |
| POST | `/api/songs/rename` | Renomeia arquivo (owner) |
| POST | `/api/songs/copy` | Copia arquivo (owner) |
| POST | `/api/songs/move` | Move arquivo (owner) |
| POST | `/api/songs/delete` | Lixeira do Drive (owner) |
| POST | `/api/songs/update_meta` | Atualiza frontmatter YAML (owner) |
| POST | `/api/save_content` | Salva conteúdo editado (owner) |
| GET | `/api/calendar` | Lista eventos do Calendar |
| POST | `/api/calendar/events` | Cria evento |
| PUT | `/api/calendar/events/<id>` | Atualiza evento |
| DELETE | `/api/calendar/events/<id>` | Exclui evento |
| GET | `/api/preferences` | Preferências (Meu Tom) do usuário |
| POST | `/api/preferences` | Salva preferência de tom |

---

## Bundle sync offline (`/api/cifras/bundle`)

Endpoint para sincronização offline do acervo completo. Suporta ETag/304 para economizar banda.

```python
# ETag calculado a partir de fileId + modifiedTime de cada música
# Se cliente envia If-None-Match com ETag atual → 304 (zero dados)
# Se ETag mudou → busca todas as cifras em paralelo (4 workers) → retorna JSON completo
# Cache servidor: só ETag em memória (não armazena json_bytes para economizar RAM)
```

**Cliente:** `_bundleSync()` dispara 4s após carregamento. Guarda ETag no localStorage (`mycifras_bundle_etag`) e timestamp da última sync (`mycifras_bundle_sync_ts`). Só faz request se passaram 30 minutos desde a última sync — refreshes normais não tocam o servidor.

---

## Persistência de dados no Drive

### Por usuário (viewers e owners)
- **Preferências / Meu Tom** (`_preferences.json`) — pasta `_mycifras_data` no Drive do próprio usuário
- **Repertórios** (`_repertorios.json`) — pasta `_mycifras_data` no Drive do próprio usuário
- **Views** (`_views.json`) — pasta `_mycifras_data` no Drive do próprio usuário
- Limite: **5 repertórios por usuário**

### Owner (acervo compartilhado)
- Cifras e pastas ficam em `CIFRAS_FOLDER_ID` (Drive do owner)

### Caches em memória (por e-mail do usuário)
```python
_prefs_cache: dict  # { email: { "data": {...}, "file_id": "..." } }
_views_cache: dict  # { email: { "data": {...}, "file_id": "..." } }
_reps_cache:  dict  # { email: { "data": {...}, "file_id": "..." } }
_library_cache      # { "data": ..., "ts": float }  — TTL 120s
_bundle_cache       # { "etag": str, "ts": float }   — só ETag, sem bytes
```

### Invalidação de cache
```python
invalidate_library_cache()  # chama também invalidate_bundle_cache()
invalidate_bundle_cache()   # chamado diretamente após save_content e import_save
```

---

## Funções em drive.py

```python
# Listagem e leitura (retorna modifiedTime em cada item)
list_folder(service, folder_id)               # lista { id, name, mimeType, modifiedTime }
scan_library(service, root_folder_id)         # escaneia estrutura completa (inclui modifiedTime)
download_bytes(service, file_id)
export_gdoc_as_text(service, file_id)

# Busca
search_content(service, query, root_folder_id, max_results=50)

# JSON genérico no Drive
load_repertorios / save_repertorios
load_views / save_views
load_preferences / save_preferences
get_user_data_folder(service)  # encontra/cria pasta _mycifras_data no Drive do usuário

# Upload / update
upload_md(service, name, content, folder_id)
update_md_content(service, file_id, content)

# Arquivo
get_file_name / trash_file / rename_file / copy_file / move_file

# Pastas
find_folder_by_name / create_folder / rename_folder / is_folder_empty
delete_folder / get_or_create_folder / resolve_folder
```

---

## Cache offline (IndexedDB)

- Store: `mycifras-offline` / `cifras`
- Chave: `fileId`
- Funções: `_idbGet(fileId)`, `_idbPut(fileId, data)`, `_idbBulkPut(entries)`, `_idbCount()`
- **Cache-first:** ao abrir uma cifra, serve IDB imediatamente → atualiza do servidor em background se texto mudou
- **Bundle sync:** `_bundleSync()` popula IDB com todo acervo em uma única transação

---

## Brand / identidade visual

**Paleta:**
```css
--primary:     #5b4b8a
--accent:      #d4af37
--bg:          #0f0e17
--surface:     #13111e
--surface2:    #1c1929
--text:        #e8e6f0
--text-muted:  #9b97b0
```

**Acordes** são sempre `#5b4b8a`. Nunca usar azul `#1d4ed8`.

**Pesos de fonte (cifra/apresentação):**
- Corpo: `font-weight: 600`
- Linhas de acordes (`.chord-line`): `font-weight: 800`

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

---

## Deploy

### Gunicorn (Dockerfile)
```
gunicorn app:app --bind 0.0.0.0:8000 --workers 1 --worker-class gthread --threads 4 --timeout 180
```
1 worker gthread com 4 threads — threads compartilham memória (economiza RAM vs. múltiplos processos). Timeout 180s para acomodar bundle build.

### Render.com
1. Push para o repositório Git
2. Render detecta `render.yaml` (runtime Docker, porta 8000)
3. Configurar variáveis de ambiente no painel
4. Adicionar `EXTERNAL_URL + /oauth/callback` como URI autorizada no Google Cloud Console

---

## Convenções de código

### Python
- `invalidate_library_cache()` após operações que alteram pastas/arquivos
- `invalidate_bundle_cache()` após operações que alteram conteúdo de cifras
- Funções de `drive.py` recebem `service` como primeiro parâmetro
- Nomes em português onde fazem sentido para o domínio

### JavaScript
- Estado global: `library`, `allSongs`, `repertorio`, `currentModal`, `rawCifraText`, `currentSemitone`, `currentRepId`, `savedReps`, `presenterSongs`, `presenterIdx`, `_myTones`, `_isOwner`
- `_myTones[fileId] = { my_key, my_capo }` — preferências de tom do usuário por música
- `_isOwner` lido de `document.body.getAttribute('data-owner') === '1'` (não via Jinja em script)
- `refreshGridBtns()` — atualiza apenas estado dos botões nos cards existentes (não recria o grid)
- `escHtml()` obrigatório ao inserir dados via innerHTML
- Sem frameworks — JS puro, sem npm, sem build step

### CSS
- Variáveis CSS em `:root`
- Classes em kebab-case
- Mobile breakpoint: `@media (max-width: 1024px)`
- iOS: evitar `:hover` com `transform` no mobile
