# Prompt Inicial — Cifras App

> Use este prompt para iniciar uma nova conversa e retomar o desenvolvimento.
> Cole o conteúdo abaixo diretamente na janela de chat.

---

## Prompt

Vou te apresentar um projeto que já está em desenvolvimento e preciso da sua ajuda para continuar.

**Contexto do projeto:**

Sou músico e toco em missas e eventos gospel. Tenho um acervo de cifras armazenado no Google Drive, organizado em pastas por categoria (Missa → Entrada, Glória, Comunhão... / Gospel → Louvor, Adoração...). Os arquivos estão no formato `.md` com frontmatter YAML.

Construí uma aplicação web em **Flask + HTML/CSS/JS** que:
- Autentica usuários via OAuth 2.0 com Google
- Lê a estrutura de pastas do Google Drive automaticamente
- Permite navegar por categoria e buscar músicas por nome
- Tem um painel de "Repertório" onde adiciono músicas como uma playlist
- Salva múltiplos repertórios nomeados em JSON (Google Drive ou local)
- Abre repertórios salvos em **modo apresentação** (cifra por cifra, fullscreen)
- Exporta HTML consolidado com todas as cifras do repertório
- Suporta transposição tonal (notação americana, por semitons ou tom destino)
- Permite importar cifras por URL (CifraClub) ou texto colado
- É responsivo para uso no celular
- Roda em Docker e faz deploy na Render.com

**Stack:**
- Backend: Python + Flask
- Auth: OAuth 2.0 com Google (`google-auth-oauthlib`)
- Storage: Google Drive API (`google-api-python-client`)
- Frontend: HTML/CSS/JS puro (tudo em `templates/index.html`)
- Extração de texto: `python-docx` (parágrafos + tabelas) + `PyMuPDF`
- Scraping: `requests` + `beautifulsoup4`
- Transposição: JavaScript no cliente
- Deploy: Docker + Gunicorn + Render.com

**Estrutura de arquivos:**
```
my_cifras_pc_owner/
├── app.py              ← rotas Flask, extração de texto, repertórios persistidos
├── auth.py             ← OAuth 2.0, login_required, get_service, EXTERNAL_URL
├── drive.py            ← operações Google Drive (list, download, upload, repertórios JSON)
├── scraper.py          ← scraping de cifras por URL
├── migrate.py          ← migração da base para .md
├── requirements.txt
├── Dockerfile          ← Python 3.12-slim + gunicorn
├── render.yaml         ← configuração de deploy na Render.com
├── .env                ← credenciais (não versionado)
├── .env.example
├── .gitignore
├── templates/
│   ├── index.html      ← UI completa (HTML + CSS + JS)
│   └── login.html      ← tela de login
└── CLAUDE.md           ← documentação técnica completa
```

**Variáveis de ambiente (.env):**
```
CIFRAS_ROOT=...               # modo local (fallback sem OAuth)
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
CIFRAS_FOLDER_ID=...          # ID da pasta raiz no Drive
FLASK_SECRET_KEY=...
EXTERNAL_URL=...              # URL pública para OAuth callback (Render, ngrok)
```

**O que já funciona (v1.2):**
- Login com Google (OAuth 2.0) com renovação automática de token
- Leitura da biblioteca do Google Drive com cache
- Navegação por sidebar com seções e categorias
- Busca global em tempo real
- Visualização de cifra em modal com zoom (A−/A+) e tela cheia
- Transposição por semitons e por nota destino
- Abertura de arquivo avulso (drag & drop e botão)
- Montagem de repertório com drag & drop
- **Repertórios persistidos:** criar, salvar, editar, excluir repertórios nomeados (JSON no Drive)
- **Modo Apresentação:** abrir cifras do repertório diretamente na tela, navegação por teclado/botão, zoom, fullscreen
- Exportação de HTML consolidado com barra de progresso
- Importação por URL (CifraClub) ou texto colado
- Layout responsivo para mobile (drawer sidebar + drawer repertório)
- Docker + deploy na Render.com
- Script de migração da base existente para .md

**Próximas features planejadas:**
1. Transposição na exportação — aplicar tom no HTML gerado
2. Edição de metadados (título, tom, categoria) na interface
3. Deploy com OAuth publicado (sem limite de usuários de teste)
4. Exportação para PDF nativo

---

Por favor, leia o `CLAUDE.md` para entender as convenções do projeto, e me ajude com o que eu pedir.
