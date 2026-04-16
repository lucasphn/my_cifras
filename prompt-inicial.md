# Prompt Inicial — My Cifras

> **Como usar:** Coloque este arquivo, o `CLAUDE.md` e o `PRD.md` na pasta `my_cifras_pc_owner`.
> Abra o terminal nessa pasta, inicie o Claude Code e cole o conteúdo abaixo.

---

## PROMPT

Você é um desenvolvedor Python + JavaScript experiente. Vamos construir a aplicação web **"My Cifras"** para o grupo de música litúrgica liderado por Lucas Almeida.

**Antes de escrever qualquer código, leia completamente os arquivos `CLAUDE.md` e `PRD.md` nesta pasta.** Eles têm todas as especificações, convenções e regras do projeto.

---

### Contexto

Lucas lidera um grupo de música litúrgica e gospel em Jaraguá do Sul (SC). Ele e os músicos do grupo precisam de um lugar centralizado para acessar o acervo de cifras do Google Drive, transpor tons rapidamente durante ensaios, montar repertórios semanais e exportar documentos para impressão.

A aplicação usa um **repositório central no Google Drive** — uma pasta compartilhada com todos os músicos do grupo. Cada músico acessa com o próprio login Google; a pasta raiz das cifras é fixada no servidor via `CIFRAS_FOLDER_ID`. Não existe modo local ou sem autenticação.

---

### Stack

- **Backend:** Python 3.10+ + Flask
- **Autenticação:** OAuth 2.0 Google (`auth.py`) — obrigatório
- **Armazenamento:** Google Drive API v3 (`drive.py`) — único backend
- **Frontend:** HTML + CSS + JS puro em `templates/index.html` (sem frameworks, sem npm)
- **Deploy:** Docker + Gunicorn + Render.com

---

### Tarefa 1 — Estrutura do Projeto

Crie a estrutura de arquivos:

```
my_cifras_pc_owner/
├── app.py
├── auth.py
├── drive.py
├── scraper.py
├── requirements.txt
├── Dockerfile
├── render.yaml
├── .env.example
├── .gitignore
├── templates/
│   ├── index.html
│   ├── landing.html
│   └── login.html
└── static/brand/         ← logos SVG (ver CLAUDE.md)
```

`requirements.txt`:
```
flask
google-auth
google-auth-oauthlib
google-api-python-client
python-docx
PyMuPDF
requests
beautifulsoup4
gunicorn
```

`.env.example`:
```env
GOOGLE_CLIENT_ID=...apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-...
CIFRAS_FOLDER_ID=<id-da-pasta-raiz-compartilhada>
FLASK_SECRET_KEY=<string-aleatoria-longa>
EXTERNAL_URL=https://meu-app.onrender.com
```

---

### Tarefa 2 — Autenticação OAuth (`auth.py`)

- Blueprint Flask `auth` com rotas `/login`, `/login/google`, `/oauth/callback`, `/logout`
- `@login_required` decorator — redireciona para `/login` se não autenticado
- `get_service()` — retorna o service Google Drive autenticado da sessão
- Token expirado → `session.clear()` → redirect ao login

**Não existe modo local.** A autenticação OAuth é obrigatória para acessar o app.

---

### Tarefa 3 — Drive (`drive.py`)

Funções puras (recebem `service` como parâmetro):

```python
# Listagem e leitura
list_folder(service, folder_id)
scan_library(service, root_folder_id)
download_bytes(service, file_id)
export_gdoc_as_text(service, file_id)

# Busca full-text (Drive API)
search_content(service, query, root_folder_id, max_results=50)
  # ATENÇÃO: não usar orderBy com fullText — a Drive API não suporta

# Repertórios JSON
load_repertorios(service, root_folder_id)
save_repertorios(service, file_id, data)

# Upload / update
upload_md(service, name, content, folder_id)
update_md_content(service, file_id, content)

# Arquivo
get_file_name(service, file_id)
trash_file(service, file_id)
rename_file(service, file_id, new_name_with_ext)
copy_file(service, file_id, new_name, target_folder_id)
move_file(service, file_id, source_folder_id, target_folder_id)

# Pastas
find_folder_by_name(service, name, parent_id)
create_folder(service, name, parent_id)
rename_folder(service, folder_id, new_name)
is_folder_empty(service, folder_id)
delete_folder(service, folder_id)
get_or_create_folder(service, name, parent_id)
resolve_folder(service, section, category, root_folder_id)
```

---

### Tarefa 4 — Backend (`app.py`)

Implemente todas as rotas do CLAUDE.md. Pontos críticos:

**`/api/library`:**
- Retorna estrutura `{ sections: [{ name, id, categories: [{ name, id, songs: [...] }] }] }`
- Cache em memória com `invalidate_library_cache()` após operações de escrita

**`/api/cifra`:**
- Aceita apenas `?fileId=&mimeType=` (Drive)
- Extrai texto de `.md`, `.docx`, `.pdf`, `.txt`, Google Docs
- Remove frontmatter YAML antes de retornar
- Retorna `{ text, key, name, title, tags }`

**`/api/search/content`:**
- GET com `?q=`
- Chama `drive.search_content()` — Drive `fullText contains`
- Retorna lista de `{ fileId, name, mimeType, excerpt }`

**`/api/songs/update_meta`:**
- POST com `{ fileId, meta: { title, artist, key, tags } }`
- Baixa o arquivo `.md`, atualiza apenas o frontmatter, preserva o corpo
- Invalida o cache de biblioteca

**`/api/export`:**
- Lê `static/brand/logo-mono-dark.svg` e inlina no HTML
- Acordes em `#5b4b8a` (nunca azul `#1d4ed8`)
- Layout elegante: cabeçalho com logo + data + contagem, cards por música com badges categoria/tom
- CSS `@media print` otimizado

**`/api/songs/rename|copy|move|delete`:**
- Chamar `invalidate_library_cache()` após cada operação
- rename: preservar extensão original

**`/api/folders` (CRUD):**
- POST: `{ section, category }` → cria pasta no Drive
- PUT `/<section>/<category>`: `{ new_name }` → renomeia
- DELETE `/<section>/<category>`: verifica `is_folder_empty` antes de deletar

---

### Tarefa 5 — Frontend (`templates/index.html`)

Interface completa em arquivo único (HTML + CSS + JS). Ver CLAUDE.md para variáveis CSS e convenções JS.

**Layout:**
- Header fixo com logo `logo-light.svg` e campo de busca
- Sidebar com item "Início" no topo, seções/categorias, ícones, botões `＋` e `⋯`
- Main: home grid ou grade de categoria
- Painel de repertório (direita)

**Home screen:**
- Banner `.home-quote` com citação inspiracional (fundo `var(--primary)`)
- Seção "🔥 Mais tocadas" (views > 0, máx 8)
- Seção "Todas as músicas" (A–Z)
- Cards via `_makeHomeCard(song, cls)`

**Busca:**
- Toggle "Nome / Letra" (`#search-mode-toggle`)
- Busca por nome: filtro local instantâneo
- Busca por letra: `GET /api/search/content?q=`

**Sidebar:**
- Dropdowns appendados ao `document.body` com `position: fixed` + `getBoundingClientRect()`
- `_openCatMenu` / `_openSongMenu` com toggle

**Modal de cifra:**
- Zoom, fullscreen, transposição
- Painel de metadados (`#meta-panel`): título, artista, tom, tags — editável
- Modo edição com `#edit-toolbar`: Selecionar tudo, Copiar, Duas colunas
- `_confirmLeaveEdit()` guard — avisa se conteúdo foi alterado sem salvar

**Mobile (breakpoint 1024px):**
- Drawer lateral em vez de sidebar fixa
- Bottom nav: Início · Pesquisar · Repertório
- Sem `transform` em `:hover` (evita duplo tap no iOS Safari)

**Cards de música:**
- Nome, badge categoria, badge tom, views (olhinho), botão `⋯`
- Menu `⋯`: Renomear, Copiar, Mover, Excluir

**Modais:**
- Modal de cifra: zoom, fullscreen, transposição
- Seletor de pasta (mover/copiar): lista seções e categorias do Drive

---

### Tarefa 6 — Landing Page (`templates/landing.html`)

Página escura com tema `--bg: #0f0e17`:
- Nav fixo com `logo-dark.svg`
- Hero com headline, CTA "Entrar com Google", preview do app mockado
- 8 feature cards (incluindo busca por letra e metadados estruturados)
- "Como funciona" em 3 passos (1: login Google, 2: acessa biblioteca compartilhada, 3: monte repertório)
- CTA final
- Banner de citação (`"O canto exige, acima de tudo, uma profunda vida espiritual" — Papa Leão XIV`)
- Footer

---

### Tarefa 7 — Login (`templates/login.html`)

- Tema escuro, centralizado
- Logo `logo-dark.svg`
- Botão "Entrar com Google" com ícone SVG oficial do Google
- Link de volta para `/`

---

### Ordem de Execução Sugerida

1. Estrutura de arquivos + `.env.example`
2. `auth.py` com OAuth obrigatório
3. `drive.py` com todas as funções
4. `app.py` com todas as rotas
5. `templates/index.html` (sidebar → home → modal → repertório → export)
6. `templates/landing.html`
7. `templates/login.html`
8. Logos SVG em `static/brand/`
9. Teste completo do fluxo Drive

---

### Observações Finais

- Toda mensagem de erro e interface em **português**
- O app não tem modo local — OAuth e Drive são obrigatórios
- JS puro — sem npm, sem build step, sem frameworks
- Dropdowns nunca clipados: sempre appendar ao `document.body`
- `invalidate_library_cache()` após qualquer escrita no Drive
- Acordes sempre em `#5b4b8a`, nunca azul
- Mobile breakpoint: `max-width: 1024px` (cobre tablets de 10")
- Evitar `:hover` com `transform` no mobile (problema de duplo tap no iOS Safari)
