# PRD — My Cifras
**Versão:** 3.1
**Produto:** Aplicação web para o músico individual gerenciar cifras, transpor tons, criar repertórios e acompanhar sua agenda litúrgica
**Autor:** Lucas Almeida
**Status:** Em produção (v3.1)

---

## 1. Visão Geral

**My Cifras** é uma aplicação web que centraliza o acervo pessoal de cifras de um músico no Google Drive e oferece ferramentas para transposição de tom, montagem de repertórios, geração de documentos exportáveis, liturgia diária e agenda via Google Calendar.

O produto é projetado para ser **comercializável**: cada músico tem sua própria instância conectada ao seu Drive pessoal. Não é um app de grupo — é uma ferramenta individual, que resolve dores reais do músico litúrgico e gospel no dia a dia.

---

## 2. Problema

Músicos litúrgicos e gospel enfrentam dificuldades práticas na preparação e execução do seu ministério:

- As cifras estão espalhadas em pastas do computador, grupos de WhatsApp e drives sem organização
- Transpor um tom manualmente é demorado e sujeito a erros — e o tom escolhido se perde
- Montar um repertório para a missa ou ensaio exige trabalho repetitivo
- Não há visão integrada da agenda de compromissos (missas, ensaios, celebrações)
- A liturgia do dia precisa ser consultada em outro site para preparar o repertório
- O acervo não está acessível no celular durante a performance

---

## 3. Objetivo

Oferecer ao músico um acervo pessoal, sempre sincronizado com seu Google Drive, acessível de qualquer dispositivo, com transposição em 1 clique, tom salvo automaticamente, busca por nome ou letra, metadados estruturados, liturgia do dia, agenda integrada e exportação elegante para PDF.

---

## 4. Usuários

- **Owner (administrador):** cria e gerencia o acervo — pode editar, renomear, excluir músicas e pastas
- **Viewer (músico convidado):** acessa o acervo compartilhado — pode transpor, salvar Meu Tom e criar repertórios pessoais, mas não altera o acervo
- **Perfil técnico:** básico — não deve exigir conhecimento de código para operar
- **Dispositivos:** celular (uso principal em ensaios/missas), tablet, computador

---

## 5. Funcionalidades

### 5.1 Landing Page pública (`/`)

Página de apresentação da aplicação para visitantes não autenticados.
- Hero com headline "Para Ministros de Música e Adoradores", CTA "Entrar com Google" e preview do app
- Seção de features (10 cards)
- Seção "Como funciona" (3 passos)
- Links para Política de Privacidade e Termos de Serviço no footer e navbar
- `<link rel="privacy-policy">` no head (para Google OAuth consent screen)

### 5.2 Páginas legais

- `/privacy` — Política de Privacidade (pública, sem autenticação)
- `/terms` — Termos de Serviço (público, sem autenticação)
- Necessárias para aprovação do Google OAuth consent screen

### 5.3 Biblioteca de cifras

- Lê automaticamente a estrutura de pastas do Google Drive (`CIFRAS_FOLDER_ID`)
- Organização: **Seção** → **Categoria/pasta**
- Suporte a `.md`, `.docx`, `.pdf`, `.txt` e Google Docs nativos
- Cache de biblioteca invalidado após operações de escrita

### 5.4 Home screen

- **Banner inspiracional** com fundo na cor primária
- **Cards de volumetria** (`#home-stats-row`): total de músicas + quantidade por seção
- **Seção "Mais tocadas" / "Destaques"**: até 8 músicas com mais visualizações
- Cards com nome, badge de categoria (tag dourada), badge de tom (mostra **Meu Tom** quando definido), contador de views e menu `⋯`

### 5.5 Grade de músicas por categoria

- Exibe músicas da categoria selecionada na sidebar
- Menu `⋯` (visível apenas para owners): renomear, copiar, mover, excluir

### 5.6 Visualização de cifra — cache-first

- Modal com texto completo da cifra
- **Cache-first:** serve IDB imediatamente → atualiza do servidor em background se texto mudou
- Fonte: `font-weight: 600` no corpo, `font-weight: 800` nas linhas de acordes
- Controles de zoom, fullscreen
- Registro automático de visualização

### 5.7 Transposição tonal e Meu Tom

- Roda inteiramente no cliente (JS), sem chamar o servidor
- **Meu Tom:** preferência de tonalidade salva por música, por usuário, no próprio Drive do usuário (`_mycifras_data/_preferences.json`)
- Tom exibido nos cards e no export de repertório reflete o **Meu Tom** do usuário, não o metadado da música
- `_myTones[fileId] = { my_key, my_capo }` — estado JS por sessão

### 5.8 Metadados estruturados (owner only)

- Painel de metadados inline no modal: título, artista, tom, tags
- Salvo como frontmatter YAML via `/api/songs/update_meta`
- Inferência automática de tom via `detectBaseNote()`

### 5.9 Busca

- **Nome** (padrão): filtra `allSongs` localmente
- **Letra**: `GET /api/search/content?q=` → Drive `fullText contains`

### 5.10 Gerenciamento de pastas (owner only)

- Criar, renomear, excluir categorias via sidebar

### 5.11 Operações de arquivo (owner only)

- Renomear, copiar, mover, excluir (lixeira do Drive)

### 5.12 Importar cifra por URL ou texto (owner only)

- Scraping de URL (CifraClub etc.) ou texto colado
- Salva como `.md` com frontmatter YAML

### 5.13 Repertórios pessoais

- Criar, nomear e salvar múltiplos repertórios pessoais
- **Limite: 5 repertórios por usuário**
- Persistência em `_mycifras_data/_repertorios.json` no Drive do próprio usuário
- Export de repertório usa **Meu Tom** do usuário (não metadado da música)
- Abertura de repertório otimizada: `refreshGridBtns()` atualiza apenas os botões existentes (sem recriar o grid)

### 5.14 Modo Apresentação

- Abre repertório em tela cheia
- Navega cifra a cifra com botões, dots ou teclado
- Controles: zoom, fullscreen
- Tom exibido é o **Meu Tom** do usuário

### 5.15 Exportação de repertório

- Formatos: HTML (PDF-ready via browser print) e DOCX
- Tom exportado: **Meu Tom** do usuário (não o metadado)
- Logo inlineado, acordes em `#5b4b8a`, CSS `@media print` otimizado

### 5.16 Sync offline — Bundle Endpoint

- `GET /api/cifras/bundle` retorna todas as cifras em JSON único
- ETag calculado de `fileId + modifiedTime` → `304 Not Modified` quando nada mudou (zero dados trafegados)
- Cache servidor: apenas ETag em memória (sem `json_bytes` para economizar RAM)
- Build paralelo: 4 workers Drive para minimizar pico de RAM
- **Cliente:** `_bundleSync()` dispara 4s após carregamento, com cooldown de 30 min entre syncs
- Resultado: IDB populado com todo o acervo em uma transação (`_idbBulkPut`)

### 5.17 Google Calendar integrado

- Seção na home screen com FullCalendar 6 (CDN)
- CRUD completo: criar, editar, excluir eventos
- Drag-and-drop e resize de eventos
- Filtro de palavras-chave (`CALENDAR_KEYWORDS`)
- Escopo OAuth: `https://www.googleapis.com/auth/calendar.events`

### 5.18 Visualizações persistidas no Drive

- `_views.json` por usuário em `_mycifras_data`
- Cache em memória por e-mail

### 5.19 PWA

- `static/manifest.json` com `display: standalone`, `theme_color: #5b4b8a`
- Service Worker (`static/sw.js`) com stale-while-revalidate para app shell
- `apple-touch-icon.png` para iOS, manifest para Android

### 5.20 Liturgia do Dia

- Seção na home com leituras do dia
- Navegação de datas

---

## 6. Design & Identidade Visual

| Token | Valor | Uso |
|---|---|---|
| `--primary` | `#5b4b8a` | Botões, bordas ativas, acordes |
| `--accent` | `#d4af37` | Badges dourados |
| `--bg` | `#0f0e17` | Fundo principal |
| `--surface` | `#13111e` | Cards, modais |
| `--surface2` | `#1c1929` | Sidebar, painéis |
| `--text` | `#e8e6f0` | Texto principal |
| `--text-muted` | `#9b97b0` | Texto secundário |

**Pesos de fonte nas cifras:** corpo `600`, acordes `800`.

---

## 7. Stack Técnica

| Componente | Tecnologia |
|---|---|
| Backend | Python 3.10+ + Flask |
| Autenticação | OAuth 2.0 (Google) via `auth.py` |
| Armazenamento | Google Drive API v3 |
| Calendar | Google Calendar API v3 |
| Leitura de .docx | python-docx |
| Leitura de .pdf | PyMuPDF (lazy-loaded) |
| Export PDF | WeasyPrint (lazy-loaded) |
| Scraping | requests + BeautifulSoup |
| Frontend | HTML + CSS + JavaScript puro |
| Calendar UI | FullCalendar 6 (CDN) |
| Cache offline | IndexedDB (`mycifras-offline`) |
| Deploy | Docker + Gunicorn (1 worker gthread, 4 threads) + Render.com |

---

## 8. Estrutura de pastas no Drive

```
CIFRAS_FOLDER_ID (pasta do owner — acervo compartilhado)
├── Missa/
│   ├── Entrada/
│   └── Comunhão/
├── Gospel/
│   └── Adoração/
└── (sem arquivos de dados aqui — cada usuário tem sua pasta própria)

_mycifras_data/ (no Drive de cada usuário)
├── _preferences.json   ← Meu Tom por música
├── _repertorios.json   ← repertórios pessoais
└── _views.json         ← histórico de visualizações
```

---

## 9. Escopos OAuth (Google Cloud Console)

| Escopo | Tipo | Uso |
|---|---|---|
| `openid` | Não-sensitivo | Login |
| `userinfo.email` | Não-sensitivo | Identificar usuário |
| `userinfo.profile` | Não-sensitivo | Nome e foto |
| `drive` | Restrito | Ler cifras + salvar dados do usuário no Drive |
| `calendar.events` | Sensitivo | Ler, criar, editar e excluir eventos de ensaio |

---

## 10. Critérios de Aceite

- [x] Landing page pública com links de privacidade/termos
- [x] Páginas `/privacy` e `/terms` acessíveis sem login
- [x] Login OAuth redireciona corretamente
- [x] Roles: owner vê botões de admin, viewer não
- [x] Viewer pode transpor, salvar Meu Tom e criar repertórios
- [x] Meu Tom exibido nos cards, export e modo apresentação
- [x] Limite de 5 repertórios por usuário
- [x] Bundle sync com ETag/304 (zero dados em sessões normais)
- [x] Cache-first: cifra exibida imediatamente do IDB
- [x] Sync offline silencioso (sem indicador visual)
- [x] Abertura de repertório rápida (sem recriar o grid)
- [x] Transposição tonal no cliente
- [x] Export HTML/DOCX com Meu Tom
- [x] Google Calendar com CRUD completo
- [x] Visualizações persistidas por usuário no Drive
- [x] PWA com Service Worker
- [x] Interface responsiva (mobile + desktop)
- [x] Acordes sempre em `#5b4b8a`

---

## 11. Fora de Escopo (v3.x)

- Compartilhamento de repertórios entre músicos
- Histórico de versões de cifras
- Notificações / lembretes de ensaio
- Integração com YouTube / Spotify
- App nativo (iOS / Android)

---

## 12. Roadmap

### Fase 1 — Produto individual (atual v3.1)
- Owner + viewers com roles distintos
- Dados pessoais (Meu Tom, repertórios, views) isolados por usuário no Drive
- Sync offline completo via bundle endpoint

### Fase 2 — Workspace compartilhado
- Músico convida outros membros para colaborar no mesmo acervo
- Controle de quem pode editar vs. só ler

### Fase 3 — Multi-workspace (SaaS)
- N grupos/igrejas no mesmo app
- Planos de assinatura por workspace

### Fase 4 — Permissões granulares
- Audit log das operações de escrita
