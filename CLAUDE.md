# CLAUDE.md — Cifras App

Contexto e instruções para o Claude Code trabalhar neste projeto.

---

## O que é este projeto

Aplicação web para músicos gerenciarem cifras e montarem repertórios.
Roda com Flask, autentica via OAuth 2.0 com Google e armazena as cifras
no Google Drive. Também suporta modo local (sem autenticação) para desenvolvimento.

Stack: **Python 3.10+ · Flask · HTML/CSS/JS puro · python-docx · PyMuPDF · Google Drive API · OAuth 2.0**

---

## Estrutura do projeto

```
cifras-app/
├── app.py                  ← servidor Flask, rotas e extração de texto
├── auth.py                 ← OAuth 2.0 com Google, login_required, get_service
├── drive.py                ← operações Google Drive (list, download, upload)
├── scraper.py              ← scraping de cifras por URL (CifraClub etc.)
├── migrate.py              ← script único de migração: .docx/.pdf/.txt → .md
├── requirements.txt
├── .env                    ← variáveis de ambiente (não versionado)
├── .env.example            ← template comentado
├── templates/
│   ├── index.html          ← toda a UI: HTML + CSS + JS em um único arquivo
│   └── login.html          ← tela de login OAuth
└── CLAUDE.md
```

### Onde cada coisa vive

- **Rotas e lógica de servidor** → `app.py`
- **Autenticação OAuth** → `auth.py` (Blueprint Flask `auth`)
- **Operações Drive** → `drive.py` (funções puras, recebem `service` como parâmetro)
- **Extração de texto** (.docx, .pdf, .txt, .md) → funções `_*_from_bytes` em `app.py`
- **Scraping de URL** → `scraper.py`
- **UI, estilos e interatividade** → `templates/index.html` (tudo junto)
- **Transposição tonal** → JavaScript no cliente, dentro de `index.html`

---

## Modos de operação

| Variável `.env` | Modo |
|---|---|
| Sem `GOOGLE_CLIENT_ID` | **Local** — sem autenticação, lê de `CIFRAS_ROOT` |
| Com OAuth + `CIFRAS_FOLDER_ID` | **Drive** — login obrigatório, lê/grava no Google Drive |

O switch é automático — basta configurar ou não as variáveis.

---

## Variáveis de ambiente (.env)

```env
# Modo local
CIFRAS_ROOT=C:\Users\...\OneDrive\Cifras

# OAuth 2.0
GOOGLE_CLIENT_ID=...apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-...
CIFRAS_FOLDER_ID=<id-da-pasta-raiz-no-drive>

# Flask
FLASK_SECRET_KEY=<string-aleatoria-longa>
```

Para gerar a secret key:
```bash
python -c "import secrets; print(secrets.token_hex())"
```

---

## Rotas da API

| Método | Rota | Descrição |
|---|---|---|
| GET | `/` | Serve `index.html` (requer login se OAuth ativo) |
| GET | `/login` | Tela de login |
| GET | `/login/google` | Inicia fluxo OAuth |
| GET | `/oauth/callback` | Callback OAuth do Google |
| GET | `/logout` | Encerra sessão |
| GET | `/api/me` | Dados do usuário logado |
| GET | `/api/library` | Estrutura completa da biblioteca (JSON) |
| GET | `/api/songs` | Lista plana de todas as músicas |
| GET | `/api/cifra?path=` | Texto de arquivo local |
| GET | `/api/cifra?fileId=&mimeType=` | Texto de arquivo no Drive |
| POST | `/api/upload` | Upload de arquivo avulso, retorna texto |
| POST | `/api/export` | Recebe lista de músicas, retorna HTML consolidado |
| POST | `/api/import/preview` | Scraping de URL ou texto colado → { title, artist, key, text } |
| POST | `/api/import/save` | Salva cifra como .md (Drive ou local) |
| GET | `/api/sections` | Seções e categorias disponíveis |

**Segurança:** `/api/cifra?path=` valida que o path está dentro de `CIFRAS_ROOT`.
Todas as rotas protegidas por `@login_required` quando OAuth configurado.

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

- Mantém o formato brasileiro (acordes em linha separada)
- Metadados estruturados no cabeçalho
- Legível sem ferramenta, git-friendly
- Frontmatter é removido automaticamente antes de exibir

---

## Extração de texto

Todas as extrações são **por bytes** (`extract_text_from_bytes`), reutilizável
tanto para arquivos locais quanto para downloads do Drive.

| Formato | Biblioteca | Observação |
|---|---|---|
| `.docx` | `python-docx` | Lê parágrafos **e tabelas** em ordem de documento |
| `.doc` | `python-docx` → fallback `win32com` | Word COM para binários antigos |
| `.pdf` | `PyMuPDF` | Stream de bytes direto |
| `.txt` / `.md` | built-in | Strip de frontmatter automático |

**Atenção:** muitas cifras .docx usam tabelas para alinhar acordes. A extração
itera `doc.element.body` em ordem, lendo `w:p` (parágrafos) e `w:tbl` (tabelas).

---

## Convenções de código

### Python
- Funções de extração retornam `str` sempre — nunca levantam exceção para o caller
- Funções de `drive.py` recebem `service` como primeiro parâmetro (sem estado global)
- `auth.get_service()` obtém o service autenticado da sessão Flask atual
- Nomes em português onde fazem sentido para o domínio

### JavaScript (dentro do index.html)
- Estado global: `library`, `allSongs`, `repertorio`, `currentModal`, `rawCifraText`, `currentSemitone`
- Músicas do Drive têm `fileId` + `mimeType`; locais têm `path`
- `escHtml()` obrigatório ao inserir dados no DOM via innerHTML
- Sem frameworks — JS puro, sem npm, sem build step

### CSS
- Variáveis CSS em `:root`: `--bg`, `--surface`, `--surface2`, `--text`, `--accent`, `--border`
- Classes em kebab-case: `.song-card`, `.btn-add`, `.rep-item`

---

## Lógica de transposição

Roda inteiramente no cliente (JS), sem chamar o servidor.

1. `rawCifraText` guarda o texto original ao abrir o modal
2. `transposeText(text, semitones)` processa linha a linha
3. Linha é "linha de acordes" se ≥ 50% das palavras batem com o regex de acorde
4. Apenas linhas de acordes são transpostas — a letra é preservada
5. `applyTranspose(semitones)` atualiza o DOM e redesenha a barra

**Notas:** C, C#, D, D#, E, F, F#, G, G#, A, A#, B
**Enarmônicos normalizados:** Db→C#, Eb→D#, Gb→F#, Ab→G#, Bb→A#

---

## Migração da base existente

```bash
# Simular (sem gravar nada)
python migrate.py --dry-run

# Migrar de verdade
python migrate.py

# Caminhos customizados
python migrate.py --source C:\...\Cifras --dest C:\...\Cifras_md
```

O script usa `CIFRAS_ROOT` do `.env` como origem e cria `<origem>_md` como destino.
Após migrar, faça upload da estrutura de pastas para o Google Drive.

---

## Controle de acesso (OAuth)

- **Usuários de teste:** Google Cloud Console → Tela de permissão OAuth → Usuários de teste
  (até 100 usuários sem precisar publicar o app)
- **Acesso às cifras:** compartilhar a pasta no Google Drive com o e-mail de cada músico
- **Revogar acesso:** remover do compartilhamento no Drive (imediato)

---

## Como instalar e rodar

```bash
pip install -r requirements.txt
python app.py
```

Acesse: `http://localhost:5000`
Celular (mesma rede): `http://<IP-do-PC>:5000`

---

## Próximas features planejadas (ver cifra_prd.md para detalhes)

- Persistência de repertórios em JSON local
- Transposição aplicada na exportação
- Layout mobile otimizado
- Deploy em produção (Railway / Google Cloud Run)
