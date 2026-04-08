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
- Gera um HTML consolidado com todas as cifras do repertório
- Suporta transposição tonal (notação americana, por semitons ou tom destino)
- Permite importar cifras por URL (CifraClub) ou texto colado

**Stack:**
- Backend: Python + Flask
- Auth: OAuth 2.0 com Google (`google-auth-oauthlib`)
- Storage: Google Drive API (`google-api-python-client`)
- Frontend: HTML/CSS/JS puro (tudo em `templates/index.html`)
- Extração de texto: `python-docx` (parágrafos + tabelas) + `PyMuPDF`
- Scraping: `requests` + `beautifulsoup4`
- Transposição: JavaScript no cliente

**Estrutura de arquivos:**
```
cifras-app/
├── app.py          ← rotas Flask, extração de texto
├── auth.py         ← OAuth 2.0, login_required, get_service
├── drive.py        ← operações Google Drive
├── scraper.py      ← scraping de cifras por URL
├── migrate.py      ← migração da base para .md
├── requirements.txt
├── .env            ← credenciais (não versionado)
├── templates/
│   ├── index.html  ← UI completa
│   └── login.html  ← tela de login
└── CLAUDE.md       ← documentação técnica completa
```

**Variáveis de ambiente (.env):**
```
CIFRAS_ROOT=...               # modo local (fallback sem OAuth)
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
CIFRAS_FOLDER_ID=...          # ID da pasta raiz no Drive
FLASK_SECRET_KEY=...
```

**O que já funciona (v1.1):**
- Login com Google (OAuth 2.0)
- Leitura da biblioteca do Google Drive
- Navegação por sidebar com seções e categorias
- Busca global em tempo real
- Visualização de cifra em modal (com suporte a tabelas Word)
- Transposição por semitons e por nota destino
- Abertura de arquivo avulso (drag & drop e botão)
- Montagem de repertório com drag & drop
- Exportação de HTML consolidado
- Importação por URL (CifraClub) ou texto colado
- Script de migração da base existente para .md

**Próximas features planejadas:**
1. Persistência de repertórios — salvar/carregar em JSON no Drive
2. Transposição na exportação — aplicar tom no HTML gerado
3. Layout mobile — otimizar para toque e leitura no celular
4. Deploy em produção — Railway ou Google Cloud Run

---

Por favor, leia o `CLAUDE.md` para entender as convenções do projeto, e me ajude com o que eu pedir.
