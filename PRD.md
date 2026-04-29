# PRD — My Cifras
**Versão:** 3.4
**Produto:** Aplicação web para o músico individual gerenciar cifras, transpor tons, criar e compartilhar repertórios, e acompanhar sua agenda litúrgica
**Autor:** Lucas Almeida
**Status:** Em produção (v3.4)

---

## 1. Visão Geral

**My Cifras** é uma plataforma SaaS para músicos de missa e grupo de oração. Oferece um **acervo base completo** — pronto no primeiro acesso, sem configuração — mais ferramentas de transposição, repertórios pessoais, compartilhamento, liturgia diária, agenda e acesso offline.

O músico entra com Google e já encontra centenas de músicas organizadas por seção e categoria. Pode adicionar suas próprias cifras (via URL ou texto) em uma área pessoal com a mesma estrutura do acervo base. O frontend apresenta os dois acervos de forma unificada e transparente.

Não é um app de grupo — é uma ferramenta individual que também permite colaboração pontual via compartilhamento de repertórios.

---

## 2. Problema

Músicos litúrgicos e gospel enfrentam dificuldades práticas na preparação e execução do ministério:

- Cifras espalhadas em pastas, WhatsApp e drives sem organização
- Transpor um tom manualmente é demorado — e o tom escolhido se perde
- Montar um repertório para a missa ou ensaio é trabalho repetitivo
- Sem visão integrada da agenda (missas, ensaios, celebrações)
- A liturgia do dia precisa ser consultada em outro site
- O acervo não está acessível no celular durante a performance
- Compartilhar um setlist com outro músico exige copiar e colar manualmente
- Montar um acervo do zero exige horas de trabalho antes de qualquer uso real

---

## 3. Objetivo

Oferecer ao músico um **acervo completo e pronto para uso no primeiro acesso** — sem configuração — com transposição em 1 clique, tom salvo por música, possibilidade de adicionar cifras próprias, compartilhamento de repertórios, acesso offline, liturgia do dia, agenda integrada e exportação elegante.

---

## 4. Usuários

- **Owner (administrador):** cria e gerencia o acervo — pode editar, renomear, excluir músicas e pastas
- **Viewer (músico convidado):** acessa o acervo compartilhado — pode transpor, salvar Meu Tom, criar e compartilhar repertórios, mas não altera o acervo
- **Perfil técnico:** básico — não deve exigir conhecimento de código para operar
- **Dispositivos:** celular (uso principal em ensaios/missas), tablet, computador

---

## 5. Funcionalidades

### 5.1 Landing Page pública (`/`)
Página de apresentação para visitantes não autenticados. Hero com CTA "Entrar com Google" (aponta diretamente para `/login/google`), seção de features, "Como funciona", links de privacidade/termos.

> Não há tela de login intermediária — usuários não autenticados são redirecionados para a landing page, que já contém os botões de acesso OAuth.

### 5.2 Páginas legais
`/privacy` e `/terms` — públicas, necessárias para o Google OAuth consent screen.

### 5.3 Biblioteca de cifras — dois acervos, uma visão

**Acervo base** (`CIFRAS_FOLDER_ID` — Drive do owner/Lucas):
- Curado e mantido pelo administrador; disponível a todos os usuários
- Organização: **Seção** → **Categoria/pasta**
- Suporte a `.md`, `.docx`, `.pdf`, `.txt` e Google Docs nativos
- Read-only para viewers

**Acervo pessoal** (pasta `My Cifras/` no Drive do próprio usuário):
- Criado automaticamente no primeiro import do usuário
- Mesma estrutura de Seção/Categoria do acervo base
- Read-write pelo usuário — músicas importadas via URL ou texto colado
- **Etapa seguinte** (não implementado): frontend faz merge transparente dos dois acervos em uma única biblioteca unificada

### 5.4 Home screen
- Cards de volumetria (total de músicas + por seção)
- **Seção "Mais tocadas"**: até 8 músicas com mais visualizações
- **Seção "Explorar por categoria"**: grid responsivo de cards com ícone, nome e tags, no padrão visual dos cards de destaque (ícone, nome, categoria, tom)

### 5.5 Grade de músicas por categoria
- Músicas da categoria selecionada
- Menu `⋯` (owner only): renomear, copiar, mover, excluir

### 5.6 Visualização de cifra — cache-first
- Modal com texto completo
- Cache-first: IDB imediatamente → atualiza em background
- Fonte: corpo `600`, acordes `.chord-line` `800`
- Controles: zoom, fullscreen
- **Mini-player YouTube**: se a cifra tem link YouTube, exibe iframe `height: 72px` (somente controles, sem vídeo visível)

### 5.7 Transposição tonal e Meu Tom
- Roda inteiramente no cliente (JS), sem chamada ao servidor
- **Meu Tom:** tom e capo salvos por música, por usuário, em `_mycifras_data/_preferences.json`
- Tom nos cards e no export reflete o **Meu Tom** do usuário

### 5.8 Metadados estruturados (owner only)
- Painel inline no modal: título, artista, tom, capo, **YouTube** (substituiu Tags)
- Salvo como frontmatter YAML via `/api/songs/update_meta`

### 5.9 Busca
- **Nome** (padrão): filtra `allSongs` localmente
- **Letra**: full-text no Drive via `GET /api/search/content?q=`

### 5.10 Gerenciamento de pastas (owner only)
Criar, renomear, excluir categorias via sidebar.

### 5.11 Operações de arquivo (owner only)
Renomear, copiar, mover, excluir (lixeira do Drive).

### 5.12 Importar cifra por URL ou texto (owner only)
Scraping de URL (CifraClub etc.) ou texto colado → salva como `.md` com frontmatter YAML.

### 5.13 Repertórios pessoais
- Criar, nomear e salvar múltiplos repertórios pessoais
- **Limite: 5 repertórios por usuário**
- Persistência em `_mycifras_data/_repertorios.json` no Drive do próprio usuário
- Menu `⋯` em cada item: **Compartilhar**, **Gerenciar compartilhamentos**, **Excluir**
- Tag discreta "Compartilhado" nos repertórios com shares ativos

### 5.14 Modo Apresentação
Tela cheia refinada com layout de 5 zonas (topbar, head, body, footer, progress bar). Recursos:
- **Tema claro/escuro** independente do tema geral do app (persiste no localStorage)
- **Modo foco** (oculta topbar + head): ativado pelo botão fullscreen no mobile/tablet; saída pelo botão `⊙` flutuante
- **Swipe lateral** para navegar entre músicas (excluindo toolbar de controles)
- **Auto-scroll** configurable com pausa ao navegar
- **Barra de progresso** na base indicando posição no repertório
- Tom = Meu Tom do usuário

### 5.15 Exportação de repertório
Formatos: HTML (PDF-ready) e DOCX. Tom exportado = Meu Tom do usuário.

### 5.16 Sync offline — Bundle Endpoint
- `GET /api/cifras/bundle` com ETag/304 → zero dados em sessões normais
- `_bundleSync()` no cliente com cooldown de 30 min

### 5.17 Google Calendar integrado
FullCalendar 6, CRUD completo, drag-and-drop, filtro por palavras-chave.

### 5.18 PWA
`manifest.json` + Service Worker stale-while-revalidate.

### 5.19 Liturgia do Dia
Leituras do dia com navegação de datas na home screen.

### 5.20 Mini-player YouTube no modal
- Campo `youtube:` no frontmatter YAML das cifras (substituiu `tags:`)
- Modal exibe iframe `height: 72px` (apenas barra de controles — sem vídeo visível)
- Player para ao fechar o modal (src limpo)
- Painel de metadados tem campo de URL com hint explicativo

### 5.21 Compartilhamento de repertórios
- **Compartilhar**: menu `⋯` no item de repertório → "Compartilhar" → input de e-mail Google do destinatário
- **Notificação**: ícone de sino no header com badge vermelho quando chega um share novo; visível em desktop e mobile
- **COMPARTILHADOS COMIGO**: seção abaixo de "SALVOS" no painel de repertório — lista os repertórios recebidos com badge "Novo" enquanto não vistos
- **Abrir share**: carrega as músicas no painel de trabalho (leitura); marca automaticamente como visto
- **Descompartilhar** (remetente): "Gerenciar compartilhamentos" no menu `⋯` → lista destinatários com botão "Remover"
- **Dispensar** (destinatário): botão `✕` no item da seção "COMPARTILHADOS COMIGO"
- **Armazenamento**: `_shares.json` em `CIFRAS_FOLDER_ID` (Drive); fallback em arquivo local

---

## 6. Design & Identidade Visual

| Token | Valor | Uso |
|---|---|---|
| `--primary` | `#5b4b8a` | Botões, bordas ativas, acordes |
| `--accent` | `#d4af37` | Badges dourados |
| `--bg` | `#f7f6fb` | Fundo principal (tema claro) |
| `--surface` | `#ffffff` | Cards, modais |
| `--surface2` | `#eeebf6` | Sidebar, painéis |
| `--text` | `#1f2937` | Texto principal |
| `--text-muted` | `#6b7280` | Texto secundário |
| `--border` | `#e6e1f0` | Bordas |

**Acordes sempre `#5b4b8a`. Nunca usar azul `#1d4ed8`.**
Pesos de fonte nas cifras: corpo `600`, acordes `800`.

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
| Sessões | Flask-Session 0.8.0 (filesystem server-side) |
| Deploy | Docker + Gunicorn (1 worker gthread, 4 threads) + Render.com |

---

## 8. Estrutura de dados no Drive

```
CIFRAS_FOLDER_ID (pasta do owner — acervo compartilhado)
├── Missa/
│   ├── Entrada/
│   └── Comunhão/
├── Gospel/
│   └── Adoração/
└── _shares.json        ← registro de compartilhamentos de repertórios

_mycifras_data/ (no Drive de cada usuário)
├── _preferences.json   ← Meu Tom por música
├── _repertorios.json   ← repertórios pessoais
└── _views.json         ← histórico de visualizações
```

---

## 9. Escopos OAuth

| Escopo | Uso |
|---|---|
| `openid` | Login |
| `userinfo.email` | Identificar usuário |
| `userinfo.profile` | Nome e foto |
| `drive` | Ler cifras + salvar dados do usuário no Drive |
| `calendar.events` | Ler, criar, editar e excluir eventos |

---

## 10. Critérios de Aceite

- [x] Login OAuth redireciona corretamente
- [x] Roles: owner vê botões de admin, viewer não
- [x] Viewer pode transpor, salvar Meu Tom e criar/compartilhar repertórios
- [x] Meu Tom exibido nos cards, export e modo apresentação
- [x] Limite de 5 repertórios por usuário
- [x] Bundle sync com ETag/304
- [x] Cache-first: cifra exibida imediatamente do IDB
- [x] Transposição tonal no cliente
- [x] Export HTML/DOCX com Meu Tom
- [x] Google Calendar com CRUD completo
- [x] PWA com Service Worker
- [x] Campo YouTube no metadado + mini-player no modal
- [x] Cards "Explorar por categoria" no padrão visual dos cards de destaque
- [x] Clicar em pasta ou Início fecha o modal de cifra aberto
- [x] Compartilhamento de repertórios por e-mail
- [x] Notificação (sino) de novos repertórios compartilhados
- [x] Seção "COMPARTILHADOS COMIGO" no painel de repertório
- [x] Descompartilhar (remetente) e dispensar (destinatário)
- [x] Interface responsiva — mobile (iOS + Android) + desktop
- [x] iOS: sem zoom ao focar na busca
- [x] iOS: bottom nav posicionada corretamente (sem flutuar acima do home indicator)
- [x] iOS: botões do modal footer acima do home bar
- [x] Modo Apresentação: dark mode, foco, swipe, auto-scroll, barra de progresso
- [x] Metadados (`artist`, `key`, `capo`, `youtube`) sincronizados entre dispositivos via `_songs_meta.json` no Drive (TTL 5 min)
- [x] Sessões server-side (Flask-Session) — sem double-login em iOS/Android
- [x] Offline: Service Worker + IndexedDB (leitura funciona sem internet)

---

## 11. Fora de Escopo (v3.x)

- Workspace colaborativo (múltiplos owners editando o mesmo acervo)
- Histórico de versões de cifras
- Notificações push / lembretes de ensaio
- Integração com Spotify
- App nativo (iOS / Android)

---

## 12. Roadmap

### Fase 1 — Produto individual (atual v3.4)
- Owner + viewers com roles distintos
- Dados pessoais isolados por usuário no Drive
- Sync offline completo via bundle endpoint
- Compartilhamento de repertórios entre usuários
- Metadados globais (`_songs_meta.json`) sincronizados entre dispositivos (TTL 5 min)
- Live sharing: alterações no repertório propagadas automaticamente para shares ativos
- Performance: renderização em batch (DocumentFragment), presenter paralelo (Promise.all + IDB-first)
- PWA iOS: safe area correta incluindo focus mode; ícone YouTube nos cards mobile
- Sessões server-side (Flask-Session): elimina double-login em iOS/Android
- Modo Apresentação P1 Refinado: dark mode, foco, swipe, auto-scroll, barra de progresso
- Offline: leitura completa do acervo sem internet (Service Worker + IndexedDB)

### Fase 1.5 — Acervo pessoal integrado (próxima etapa)
- Import via URL/texto salva no Drive do próprio usuário (pasta `My Cifras/` com mesma estrutura)
- Frontend faz merge transparente: acervo base (read-only) + músicas pessoais (read-write)
- Diferenciação visual sutil entre músicas do acervo base e músicas pessoais
- Operações de escrita (renomear, mover, excluir) limitadas ao acervo pessoal do usuário

### Fase 2 — Workspace compartilhado
- Músico convida outros membros para colaborar no mesmo acervo
- Controle de quem pode editar vs. só ler

### Fase 3 — Multi-workspace (SaaS)
- N grupos/igrejas no mesmo app
- Planos de assinatura por workspace

### Fase 4 — Permissões granulares
- Audit log das operações de escrita
