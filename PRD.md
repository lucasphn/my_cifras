# PRD — My Cifras
**Versão:** 3.0
**Produto:** Aplicação web para o músico individual gerenciar cifras, transpor tons, criar repertórios e acompanhar sua agenda litúrgica
**Autor:** Lucas Almeida
**Status:** Em produção (v3.0)

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

- **Músico litúrgico / gospel** — usuário principal; conecta seu próprio Drive e gerencia seu acervo pessoal
- **Perfil técnico:** básico — não deve exigir conhecimento de código para operar
- **Dispositivos:** celular (uso principal em ensaios/missas), tablet, computador

---

## 5. Funcionalidades

### 5.1 Landing Page pública (`/`)

Página de apresentação da aplicação para visitantes não autenticados.
- Hero com headline voltado para o músico individual, CTA "Entrar com Google" e preview do app
- Seção de features (10 cards)
- Seção "Como funciona" (3 passos)
- CTA final
- Banner de citação inspiracional
- Footer

### 5.2 Biblioteca de cifras

- Lê automaticamente a estrutura de pastas do Google Drive (`CIFRAS_FOLDER_ID`)
- Organização: **Seção** (ex: Missa, Gospel) → **Categoria/pasta** (ex: Adoração, Entrada)
- Suporte a `.md`, `.docx`, `.pdf`, `.txt` e Google Docs nativos
- Cache de biblioteca invalidado após operações de escrita

### 5.3 Home screen

- **Banner inspiracional** (citação do Papa Leão XIV) com fundo na cor primária
- **Cards de volumetria** (`#home-stats-row`): total de músicas + quantidade por seção, distribuídos horizontalmente
- **Seção "Mais tocadas" / "Destaques"**: até 8 músicas com mais visualizações (ou todas se nenhuma foi tocada)
- Cards com nome, badge de categoria (tag dourada), badge de tom, contador de views e menu `⋯`

### 5.4 Grade de músicas por categoria

- Exibe músicas da categoria selecionada na sidebar
- Mesmo estilo de card da home (com views e menu `⋯`)
- Menu `⋯` por música: renomear, copiar, mover, excluir

### 5.5 Visualização de cifra

- Modal com texto completo da cifra
- Identificação automática de linhas de acordes (destacadas na cor primária)
- Controles de zoom (+/-)
- Fullscreen
- Registro automático de visualização (`/api/track_view`) — persistido no Drive

### 5.6 Transposição tonal

- Roda inteiramente no cliente (JS), sem chamar o servidor
- Seleciona o tom destino ou usa +/- semitons
- Apenas linhas de acordes são transpostas — a letra é preservada
- Enarmônicos normalizados (Db→C#, Bb→A#, etc.)
- **Salvar Tom**: persiste o novo tom no frontmatter YAML do arquivo `.md` via `/api/songs/update_meta`

### 5.7 Metadados estruturados

- Painel de metadados inline no modal: título, artista, tom, tags
- Salvo como frontmatter YAML no arquivo `.md` via `/api/songs/update_meta`
- **Inferência de tom**: se `key` estiver vazio, detecta automaticamente a partir da primeira linha de acordes (`detectBaseNote()`)
- **Atualização em tempo real**: ao salvar metadados, `_refreshCardsForSong()` atualiza os cards visíveis sem reload da página
- Formato padrão:
  ```markdown
  ---
  title: Nome da Música
  artist: Nome do Artista
  key: G
  section: Gospel
  category: Adoração
  tags: []
  ---
  ```

### 5.8 Editor de cifra

- Modo de edição com textarea inline no modal
- Toolbar: Selecionar tudo, Copiar, Duas colunas
- Vista em duas colunas (`column-count: 2`) para cifras longas
- Confirmação antes de sair sem salvar (compara com `rawCifraText`)

### 5.9 Busca

- Campo com botão X para limpar
- Dois modos: **Nome** (filtro local instantâneo) e **Letra** (full-text Drive API)
- Busca por letra usa `fullText contains` — encontra qualquer palavra dentro dos arquivos
- Resultados exibidos com destaque do trecho encontrado

### 5.10 Gerenciamento de pastas

- Criar nova categoria: botão `＋` por seção na sidebar
- Renomear categoria: menu `⋯` → Renomear (edição inline)
- Excluir categoria: menu `⋯` → Excluir (somente pastas vazias)
- Sidebar exibe apenas o nome das seções (sem ícones nas pastas mães)

### 5.11 Operações de arquivo

- **Renomear**: edição inline com feedback "Salvando..."
- **Copiar**: selecionar pasta de destino no seletor modal
- **Mover**: selecionar pasta de destino no seletor modal
- **Excluir**: confirmação inline, envia para lixeira do Drive

### 5.12 Importar cifra por URL ou texto

- Cole URL do CifraClub (ou outro site) → scraping automático
- Cole texto de cifra diretamente
- Preview com título, artista, tom e texto
- Selecionar seção e categoria destino
- Salva como `.md` no Drive com frontmatter YAML estruturado

### 5.13 Repertórios

- Criar, nomear e salvar múltiplos repertórios pessoais
- Adicionar músicas ao repertório aberto via botão `+ Repertório` nos cards
- Remover músicas do repertório
- Reordenar músicas (drag-and-drop)
- Persistência no Google Drive (`_repertorios.json`) — na pasta pessoal do músico

### 5.14 Modo Apresentação

- Abre repertório em tela cheia
- Navega cifra a cifra com botões, dots ou teclado
- Controles: zoom, fullscreen
- Teclado: `→/↓` próxima, `←/↑` anterior, `+/-` zoom, `F` fullscreen, `Esc` fechar

### 5.15 Exportação de repertório

- Gera HTML autocontido com todas as cifras
- Layout elegante e minimalista, pronto para impressão / salvar como PDF
- Logo `logo-mono-dark.svg` inlineado no documento
- Cabeçalho com título, data e quantidade de músicas
- Cada música: nome, badges de categoria e tom, cifra em fonte monospace
- Acordes destacados na cor primária (`#5b4b8a`)
- CSS `@media print` otimizado

### 5.16 Upload avulso de arquivo

- Aceita `.docx`, `.pdf`, `.txt` — extrai e exibe o texto
- Não salva no Drive; serve para consulta pontual

### 5.17 Google Calendar integrado

- Seção na home screen abaixo dos destaques
- Visualização com FullCalendar 6 (CDN): mensal, semanal, diária, lista
- CRUD completo: criar, editar, excluir eventos diretamente no app
- Drag-and-drop e resize de eventos
- Modal de evento com campos: título, toggle all-day, datetime início/fim, local, descrição
- Filtro de palavras-chave (`CALENDAR_KEYWORDS`) para exibir apenas eventos relacionados ao ministério
- Tema escuro integrado ao visual do app
- Escopo OAuth: `https://www.googleapis.com/auth/calendar`

### 5.18 Visualizações persistidas no Drive

- Contagem de visualizações por música salva em `_views.json` na pasta raiz do Drive
- Substitui `views.json` local (que se perderia a cada deploy)
- Cache em memória (`_views_cache`) para evitar chamadas desnecessárias à Drive API
- Fallback para arquivo local em desenvolvimento sem Drive configurado

### 5.19 PWA — Atalho na tela inicial

- `static/manifest.json` com `display: standalone`, `start_url: /app`, `theme_color: #5b4b8a`
- iOS: atalho via `apple-touch-icon.png` (180×180)
- Android: instalação automática via Chrome ("Adicionar à tela inicial")
- `<meta name="theme-color">` em todos os templates

### 5.20 Liturgia do Dia

- Seção na home screen com a liturgia do dia atual
- Título "Liturgia do Dia" acima dos botões de atalho
- Botões de acesso rápido às leituras (preenchem a largura disponível)
- Controles de navegação de data

### 5.21 Cards de volumetria

- Exibidos na home screen acima dos destaques
- Card total de músicas + um card por seção do acervo
- Distribuição horizontal com `flex: 1` (mobile: primeiro ocupa linha inteira, demais 50%)

---

## 6. Design & Identidade Visual

### Paleta

| Token | Valor | Uso |
|---|---|---|
| `--primary` | `#5b4b8a` | Botões, bordas ativas, acordes |
| `--accent` | `#d4af37` | Badges dourados, destaques |
| `--bg` | `#0f0e17` | Fundo principal |
| `--surface` | `#13111e` | Cards, modais |
| `--surface2` | `#1c1929` | Sidebar, painéis |
| `--text` | `#e8e6f0` | Texto principal |
| `--text-muted` | `#9b97b0` | Texto secundário |

### Logos

| Arquivo | Uso |
|---|---|
| `logo-dark.svg` | Landing page, login (fundo escuro) |
| `logo-light.svg` | Header do app (fundo claro) |
| `logo-mono-dark.svg` | Export HTML impresso |
| `favicon.svg` | `<link rel="icon">` em todos os templates |
| `apple-touch-icon.png` | Atalho na tela de início do iPhone/iPad/Android (180×180) |

---

## 7. Stack Técnica

| Componente | Tecnologia |
|---|---|
| Backend | Python 3.10+ + Flask |
| Autenticação | OAuth 2.0 (Google) via `auth.py` |
| Armazenamento | Google Drive API v3 |
| Calendar | Google Calendar API v3 |
| Leitura de .docx | python-docx |
| Leitura de .pdf | PyMuPDF |
| Scraping | requests + BeautifulSoup |
| Frontend | HTML + CSS + JavaScript puro (sem frameworks) |
| Calendar UI | FullCalendar 6 (CDN) |
| Deploy | Docker + Gunicorn + Render.com |

---

## 8. Estrutura de pastas no Drive

```
CIFRAS_FOLDER_ID (pasta pessoal do músico)
├── Missa/
│   ├── Entrada/
│   ├── Comunhão/
│   └── Final/
├── Gospel/
│   ├── Adoração/
│   ├── Louvor/
│   └── (raiz da seção — músicas sem subpasta)
├── _repertorios.json     ← repertórios pessoais do músico
└── _views.json           ← contagem de visualizações (persistida no Drive)
```

Músicas na raiz de uma seção (sem categoria) ficam em `_raiz`.

---

## 9. Fluxo Principal do Usuário

```
1. Acessa a landing page (/)
2. Clica em "Entrar com Google" → OAuth
3. É redirecionado para o app (/app)
4. Visualiza home: volumetria, destaques, liturgia do dia, calendário
5. Navega na sidebar: seção → categoria
6. Ou busca por nome / letra no campo de busca
7. Clica em um card de música → modal com cifra
8. Transpõe o tom se necessário → salva o novo tom
9. Adiciona ao repertório pessoal
10. Consulta a liturgia do dia para preparar o repertório
11. Verifica a agenda no Google Calendar integrado
12. Abre modo apresentação para o ensaio/missa
13. Ao final: exporta o repertório como HTML/PDF
```

---

## 10. Critérios de Aceite

- [x] Landing page pública acessível sem login
- [x] Login OAuth com Google redireciona corretamente
- [x] Biblioteca carrega estrutura de pastas do Drive automaticamente
- [x] Home exibe cards de volumetria, destaques e liturgia do dia
- [x] Banner inspiracional exibido no topo da home
- [x] Sidebar exibe seções sem ícones, apenas nomes
- [x] Criar / renomear / excluir categorias via sidebar
- [x] Cards de música com menu `⋯`: renomear, copiar, mover, excluir
- [x] Feedback "Salvando..." durante rename
- [x] Dropdowns não são clipados por overflow/transform dos cards
- [x] Transposição tonal funciona sem chamar o servidor
- [x] Salvar Tom persiste o tom no Drive via update_meta
- [x] Inferência automática de tom quando key está vazio
- [x] Atualização em tempo real dos cards após salvar metadados
- [x] Modo Apresentação com navegação por teclado
- [x] Export HTML com logo inline, acordes em `#5b4b8a`, otimizado para impressão
- [x] Import por URL scrapa CifraClub e salva como .md estruturado
- [x] Repertórios persistem no Drive pessoal do músico
- [x] Interface responsiva (mobile + desktop + tablet até 10")
- [x] Busca por nome (instantânea) e por letra (full-text Drive)
- [x] Campo de busca com botão X para limpar
- [x] Painel de metadados editável (título, artista, tom, tags)
- [x] Editor inline com toolbar (selecionar tudo, copiar, duas colunas)
- [x] Confirmação ao sair do modo edição com alterações não salvas
- [x] Atalho iOS (apple-touch-icon) e Android (PWA manifest)
- [x] Google Calendar com CRUD completo e filtro por palavras-chave
- [x] Visualizações persistidas no Drive (_views.json)
- [x] Cards de volumetria distribuídos horizontalmente na home
- [x] Liturgia do Dia com título acima dos botões de atalho

---

## 11. Fora de Escopo (v3.x)

- Compartilhamento de repertórios entre músicos
- Histórico de versões de cifras
- Notificações / lembretes de ensaio (push notifications)
- Integração com YouTube / Spotify
- App nativo (iOS / Android)

---

## 12. Roadmap

### Fase 1 — Produto individual (atual)
- Um músico por instância, conectado ao seu Drive pessoal
- Foco na dor do músico: transposição, tom salvo, repertório, liturgia, agenda

### Fase 2 — Workspace compartilhado
- Músico convida outros membros para colaborar no mesmo acervo
- Repertórios por usuário (`_rep_{user_id}.json`) para evitar conflitos de escrita
- Controle de quem pode editar vs. só ler

### Fase 3 — Multi-workspace (SaaS)
- Suporte a N grupos/igrejas no mesmo app
- Tabela de configuração associando `user_email → workspace_id → CIFRAS_FOLDER_ID`
- Administrador do workspace pode convidar membros e controlar permissões
- Planos de assinatura por workspace

### Fase 4 — Permissões granulares
- Músicos podem ter acesso somente-leitura
- Apenas líderes podem criar/mover/renomear/excluir arquivos e pastas
- Audit log das operações de escrita
