# Prompt Inicial — My Cifras

> **Como usar:** Coloque este arquivo, o `CLAUDE.md` e o `PRD.md` na pasta `my_cifras_pc_owner`.
> Abra o terminal nessa pasta, inicie o Claude Code e cole o conteúdo abaixo.

---

## PROMPT

Você é um desenvolvedor Python + JavaScript experiente. Vamos construir a aplicação web **"My Cifras"** para o músico Lucas Almeida.

**Antes de escrever qualquer código, leia completamente os arquivos `CLAUDE.md` e `PRD.md` nesta pasta.** Eles têm todas as especificações, convenções e regras do projeto.

---

### Contexto

Lucas lidera um grupo de música litúrgica e gospel em Jaraguá do Sul (SC). Ele e os músicos do grupo precisam de um lugar centralizado para acessar o acervo de cifras do Google Drive, transpor tons rapidamente durante ensaios, montar repertórios semanais e exportar documentos para impressão.

A aplicação usa Google Drive como backend de armazenamento — cada músico acessa com o próprio login Google, e as pastas de cifras são compartilhadas via Drive.

---

### Stack

- **Backend:** Python 3.10+ + Flask
- **Autenticação:** OAuth 2.0 Google (`auth.py`)
- **Armazenamento:** Google Drive API v3 (`drive.py`)
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

---

### Tarefa 2 — Autenticação OAuth (`auth.py`)

- Blueprint Flask `auth` com rotas `/login`, `/login/google`, `/oauth/callback`, `/logout`
- `@login_required` decorator — redireciona para `/login` se não autenticado
- `get_service()` — retorna o service Google Drive autenticado da sessão
- Detectar modo local (sem `GOOGLE_CLIENT_ID`) e pular autenticação
- Token expirado → `session.clear()` → redirect ao login

---

### Tarefa 3 — Drive (`drive.py`)

Funções puras (recebem `service` como parâmetro):

```python
# Leitura
list_sections(service, root_id)
list_categories(service, section_id)
list_songs(service, folder_id)
download_file(service, file_id, mime_type)
export_gdoc_as_text(service, file_id)

# Escrita
upload_md(service, name, content, folder_id)
resolve_folder(service, section, category, root_id)

# Repertórios
load_repertorios(service, root_id)
save_repertorios(service, root_id, data)

# Pasta
find_folder_by_name(service, name, parent_id)
create_folder(service, name, parent_id)
rename_folder(service, folder_id, new_name)
is_folder_empty(service, folder_id)
delete_folder(service, folder_id)

# Arquivo
get_file_name(service, file_id)
trash_file(service, file_id)
rename_file(service, file_id, new_name_with_ext)
copy_file(service, file_id, new_name, target_folder_id)
move_file(service, file_id, source_folder_id, target_folder_id)
```

---

### Tarefa 4 — Backend (`app.py`)

Implemente todas as rotas do CLAUDE.md. Pontos críticos:

**`/api/library`:**
- Retorna estrutura `{ sections: [{ name, id, categories: [{ name, id, songs: [...] }] }] }`
- Cache em memória com `invalidate_library_cache()` após operações de escrita

**`/api/cifra`:**
- Aceita `?fileId=&mimeType=` (Drive) ou `?path=` (local)
- Extrai texto de `.md`, `.docx`, `.pdf`, `.txt`, Google Docs
- Remove frontmatter YAML antes de retornar
- Retorna `{ text, key, name }`

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
- Header fixo com logo `logo-light.svg`
- Sidebar com seções/categorias, ícones, botões `＋` e `⋯`
- Main: home grid ou grade de categoria
- Painel de repertório (direita)

**Home screen:**
- Banner `.home-quote` com citação inspiracional (fundo `var(--primary)`)
- Seção "🔥 Mais tocadas" (views > 0, máx 8)
- Seção "Todas as músicas" (A–Z)
- Cards via `_makeHomeCard(song, cls)`

**Sidebar:**
- Dropdowns appendados ao `document.body` com `position: fixed` + `getBoundingClientRect()`
- `_openCatMenu` / `_openSongMenu` com toggle (clicar no `⋯` já aberto fecha)
- `invalidate_library_cache()` após operações de pasta

**Cards de música:**
- Nome, badge categoria, badge tom, views (olhinho), botão `⋯`
- Menu `⋯`: Renomear, Copiar, Mover, Excluir
- Feedback "Salvando..." durante rename

**Modais:**
- Modal de cifra: zoom, fullscreen, transposição
- Seletor de pasta (mover/copiar): lista seções e categorias do Drive

---

### Tarefa 6 — Landing Page (`templates/landing.html`)

Página escura com tema `--bg: #0f0e17`:
- Nav fixo com `logo-dark.svg`
- Hero com headline, CTA "Entrar com Google", preview do app mockado
- 8 feature cards
- "Como funciona" em 3 passos
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
2. `auth.py` + modo local sem autenticação
3. `drive.py` com todas as funções
4. `app.py` com todas as rotas
5. `templates/index.html` (sidebar → home → modal → repertório → export)
6. `templates/landing.html`
7. `templates/login.html`
8. Logos SVG em `static/brand/`
9. Teste completo do fluxo (local e Drive)

---

### Observações Finais

- Toda mensagem de erro e interface em **português**
- Rodar com `python app.py` sem configurações adicionais (modo local)
- JS puro — sem npm, sem build step, sem frameworks
- Dropdowns nunca clipados: sempre appendar ao `document.body`
- `invalidate_library_cache()` após qualquer escrita no Drive
- Acordes sempre em `#5b4b8a`, nunca azul
