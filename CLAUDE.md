# CLAUDE.md — My Cifras

Contexto e instruções para o Claude Code trabalhar neste projeto.

---

## O que é este projeto

**My Cifras** é uma aplicação web para grupos de música litúrgica e gospel gerenciarem um acervo centralizado de cifras e montarem repertórios.

Roda com Flask, autentica via OAuth 2.0 com Google e lê/grava exclusivamente no **Google Drive** — a pasta raiz (`CIFRAS_FOLDER_ID`) é um repositório central compartilhado com todos os músicos do grupo.

Stack: **Python 3.10+ · Flask · HTML/CSS/JS puro · python-docx · PyMuPDF · Google Drive API · OAuth 2.0 · Docker · Gunicorn**

---

## Estrutura do projeto

```
my_cifras_pc_owner/
├── app.py                  ← servidor Flask, rotas, extração de texto, repertórios, export
├── auth.py                 ← OAuth 2.0 com Google, login_required, get_service
├── drive.py                ← operações Google Drive (list, download, upload, JSON, pastas, arquivos, busca)
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
│   └── brand/              ← logos SVG do My Cifras
│       ├── favicon.svg
│       ├── icon.svg
│       ├── logo-dark.svg           ← para fundos escuros (landing, login)
│       ├── logo-light.svg          ← para fundos claros (header do app)
│       ├── logo-mono-dark.svg      ← monocromático roxo (export HTML, impressão)
│       ├── logo-mono-white.svg     ← monocromático branco (banners escuros)
│       └── apple-touch-icon.png    ← ícone 180×180 para atalho iOS
├── assets/
│   └── mycifras-logo/      ← arquivos fonte dos logos + brand-tokens.css
└── CLAUDE.md
```

### Onde cada coisa vive

- **Rotas e lógica de servidor** → `app.py`
- **Autenticação OAuth** → `auth.py` (Blueprint Flask `auth`)
- **Operações Drive** → `drive.py` (funções puras, recebem `service` como parâmetro)
- **Repertórios JSON** → `drive.py` (`load_repertorios`, `save_repertorios`) — arquivo `_repertorios.json` no Drive
- **Extração de texto** (.docx, .pdf, .txt, .md) → funções `_*_from_bytes` em `app.py`
- **Scraping de URL** → `scraper.py`
- **UI, estilos e interatividade do app** → `templates/index.html` (tudo junto)
- **Landing page pública** → `templates/landing.html`
- **Transposição tonal** → JavaScript no cliente, dentro de `index.html`
- **Modo Apresentação** → JavaScript no cliente, dentro de `index.html`

---

## Variáveis de ambiente (.env)

```env
# OAuth 2.0 (obrigatório)
GOOGLE_CLIENT_ID=...apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-...

# Repositório central de cifras no Drive
CIFRAS_FOLDER_ID=<id-da-pasta-raiz-compartilhada>

# Flask
FLASK_SECRET_KEY=<string-aleatoria-longa>

# Deploy (Render, ngrok, etc.)
EXTERNAL_URL=https://meu-app.onrender.com
```

**O app requer Drive.** Não existe modo de operação local — `GOOGLE_CLIENT_ID` e `CIFRAS_FOLDER_ID` são obrigatórios.

---

## Rotas da API

| Método | Rota | Descrição |
|---|---|---|
| GET | `/` | Landing page pública (`landing.html`) |
| GET | `/app` | App principal (requer login OAuth) |
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
| POST | `/api/track_view` | Registra visualização de uma música |
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

---

## Persistência de repertórios

### Estrutura do JSON (`_repertorios.json`)
```json
{
  "rpt_abc123": {
    "id": "rpt_abc123",
    "name": "Missa Domingo",
    "songs": [
      {
        "name": "Não Vou Parar",
        "fileId": "...",
        "mimeType": "text/markdown",
        "section": "Gospel",
        "category": "Adoração"
      }
    ],
    "created_at": "2026-04-09T10:00:00",
    "updated_at": "2026-04-09T11:30:00"
  }
}
```

O arquivo `_repertorios.json` fica na raiz de `CIFRAS_FOLDER_ID` e é compartilhado entre todos os usuários do grupo.

### Backend (`app.py`)
- `_load_reps()` / `_save_reps(data)` — carrega e salva via Drive
- `_rep_lock` (threading.Lock) — evita race conditions em escrita

### Frontend (JS em `index.html`)
- `savedReps` — cache local
- `currentRepId` — ID do repertório aberto
- `_isSaving` — flag anti-duplo POST
- `_pendingDelete` — ID aguardando confirmação inline

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
- Seções com ícones mapeados em `SECTION_ICONS`
- Categorias com ícones em `CAT_ICONS`
- Botão `＋` por seção: cria nova pasta inline
- Botão `⋯` por categoria: abre dropdown (renomear / excluir)
- Dropdowns appendados ao `document.body` com `position: fixed` + `getBoundingClientRect()` para escapar de `overflow: hidden` e `transform` nos cards

---

## Home screen

- Banner de citação inspiracional (`.home-quote`) acima das seções de músicas
- Seção **🔥 Mais tocadas** (músicas com views > 0, máx. 8 cards)
- Seção **Todas as músicas** (todas em ordem A–Z)
- Cards com: nome, badge de categoria, badge de tom, contador de views (olhinho), botão `⋯`
- `_makeHomeCard(song, cls)` — fábrica de card reutilizada em home e grade de categoria
- `_songWithViews(song)` — enriquece músicas com views/key de `allSongs`

---

## Busca

Dois modos controlados por `#search-mode-toggle`:
- **Nome** (padrão): filtra `allSongs` localmente pelo nome
- **Letra**: chama `GET /api/search/content?q=` → Drive `fullText contains`

A busca por letra não suporta `orderBy` na Drive API — não usar `orderBy` em `search_content()`.

---

## Modal de cifra

- Zoom, fullscreen, transposição tonal
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
- `auth.get_service()` obtém o service autenticado da sessão Flask atual
- `invalidate_library_cache()` deve ser chamado após qualquer operação que altere pastas ou arquivos
- Nomes em português onde fazem sentido para o domínio

### JavaScript (dentro do index.html)
- Estado global: `library`, `allSongs`, `repertorio`, `currentModal`, `rawCifraText`, `currentSemitone`, `currentRepId`, `savedReps`, `presenterSongs`, `presenterIdx`, `_openCatMenu`, `_openSongMenu`, `_twoColMode`
- Músicas do Drive têm `fileId` + `mimeType` (não existe mais o campo `path`)
- `escHtml()` obrigatório ao inserir dados no DOM via innerHTML
- Dropdowns appendados ao `document.body` com `position: fixed` + `getBoundingClientRect()`
- `closeCatMenu()` / `closeOpenSongMenu()` chamados antes de abrir qualquer novo menu
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

---

## Controle de acesso (OAuth)

- **Usuários de teste:** Google Cloud Console → Tela de permissão OAuth → Usuários de teste
- **Acesso às cifras:** compartilhar a pasta central (`CIFRAS_FOLDER_ID`) no Google Drive com cada músico do grupo
- **Token expirado (7 dias em modo teste):** app detecta `invalid_grant` e redireciona ao login

---

## Arquitetura futura: multi-usuário

O app hoje usa um repositório central compartilhado (todos acessam o mesmo `CIFRAS_FOLDER_ID`). A evolução prevista é:

1. **Fase atual:** repositório único compartilhado — todos os músicos do grupo leem e editam o mesmo Drive
2. **Próxima fase:** repertórios por usuário — `_repertorios_{user_id}.json` em vez de arquivo compartilhado, evitando conflitos de escrita
3. **Fase futura:** suporte a múltiplos grupos — cada grupo tem seu próprio `CIFRAS_FOLDER_ID`; o app associa o e-mail do usuário ao grupo correto via tabela de configuração

Ao implementar mudanças no fluxo de dados, considerar que o `_rep_lock` atual não é suficiente para múltiplos usuários concorrentes em escrita — será necessário um mecanismo de versionamento ou CRDT no JSON.
