# PRD — My Cifras
**Versão:** 2.1
**Produto:** Aplicação web para grupos de música litúrgica e gospel gerenciarem cifras e repertórios
**Autor:** Lucas Almeida
**Status:** Em produção (v2.1)

---

## 1. Visão Geral

**My Cifras** é uma aplicação web que centraliza o acervo de cifras de um grupo musical no Google Drive e oferece ferramentas para navegação, transposição tonal, montagem de repertórios e geração de documentos exportáveis.

O acervo fica em uma **pasta central compartilhada** no Google Drive. Todos os músicos do grupo acessam o mesmo repositório após autenticar com suas contas Google. O foco é em grupos litúrgicos e gospel que precisam acessar cifras rapidamente em ensaios, missas e shows — em qualquer dispositivo.

---

## 2. Problema

Músicos litúrgicos acumulam dezenas ou centenas de cifras espalhadas em pastas do computador, grupos de WhatsApp e drives compartilhados. Na hora do ensaio ou da missa:

- É difícil encontrar a cifra certa rapidamente — pelo nome ou pela letra
- Transposição manual de tom é demorada e sujeita a erros
- Montar um repertório ordenado para impressão exige trabalho repetitivo
- O acervo não está acessível no celular durante a performance
- Metadados como artista, tom e tags ficam perdidos em arquivos sem estrutura

---

## 3. Objetivo

Oferecer ao grupo musical um acervo centralizado, sempre sincronizado com o Google Drive, acessível de qualquer dispositivo, com transposição em 1 clique, busca por nome ou letra, metadados estruturados, montagem de repertórios e exportação elegante para PDF.

---

## 4. Usuários

- Músico litúrgico / gospel (usuário principal, acesso ao repositório compartilhado)
- Líder de grupo musical (organiza pastas, cria repertórios, importa novas cifras)
- Nível técnico: básico — não deve exigir conhecimento de código para operar

---

## 5. Funcionalidades

### 5.1 Landing Page pública (`/`)

Página de apresentação da aplicação para visitantes não autenticados.
- Hero com headline, CTA "Entrar com Google" e preview do app
- Seção de features (8 cards)
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
- **Seção "🔥 Mais tocadas"**: até 8 músicas com mais visualizações
- **Seção "Todas as músicas"**: lista completa em ordem A–Z
- Cards com nome, badge de categoria, badge de tom, contador de views e menu `⋯`

### 5.4 Grade de músicas por categoria

- Exibe músicas da categoria selecionada na sidebar
- Mesmo estilo de card da home (com views e menu `⋯`)
- Menu `⋯` por música: renomear, copiar, mover, excluir

### 5.5 Visualização de cifra

- Modal com texto completo da cifra
- Identificação automática de linhas de acordes (destacadas na cor primária)
- Controles de zoom (+/-)
- Fullscreen
- Registro automático de visualização (`/api/track_view`)

### 5.6 Transposição tonal

- Roda inteiramente no cliente (JS), sem chamar o servidor
- Seleciona o tom destino ou usa +/- semitons
- Apenas linhas de acordes são transpostas — a letra é preservada
- Enarmônicos normalizados (Db→C#, Bb→A#, etc.)

### 5.7 Metadados estruturados

- Painel de metadados inline no modal: título, artista, tom, tags
- Salvo como frontmatter YAML no arquivo `.md` via `/api/songs/update_meta`
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

- Dois modos: **Nome** (filtro local instantâneo) e **Letra** (full-text Drive API)
- Busca por letra usa `fullText contains` — encontra qualquer palavra dentro dos arquivos
- Resultados exibidos com destaque do trecho encontrado

### 5.10 Gerenciamento de pastas

- Criar nova categoria: botão `＋` por seção na sidebar
- Renomear categoria: menu `⋯` → Renomear (edição inline)
- Excluir categoria: menu `⋯` → Excluir (somente pastas vazias)

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

- Criar, nomear e salvar múltiplos repertórios
- Adicionar músicas ao repertório aberto via botão `+ Repertório` nos cards
- Remover músicas do repertório
- Reordenar músicas (drag-and-drop)
- Persistência no Google Drive (`_repertorios.json`) — compartilhado entre usuários do grupo

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
| `apple-touch-icon.png` | Atalho na tela de início do iPhone/iPad (180×180) |

---

## 7. Stack Técnica

| Componente | Tecnologia |
|---|---|
| Backend | Python 3.10+ + Flask |
| Autenticação | OAuth 2.0 (Google) via `auth.py` |
| Armazenamento | Google Drive API v3 |
| Leitura de .docx | python-docx |
| Leitura de .pdf | PyMuPDF |
| Scraping | requests + BeautifulSoup |
| Frontend | HTML + CSS + JavaScript puro (sem frameworks) |
| Deploy | Docker + Gunicorn + Render.com |

---

## 8. Estrutura de pastas no Drive

```
CIFRAS_FOLDER_ID (repositório central compartilhado)
├── Missa/
│   ├── Entrada/
│   ├── Comunhão/
│   └── Final/
├── Gospel/
│   ├── Adoração/
│   ├── Louvor/
│   └── (raiz da seção — músicas sem subpasta)
└── _repertorios.json     ← repertórios de todos os usuários do grupo
```

Músicas na raiz de uma seção (sem categoria) ficam em `_raiz`.

---

## 9. Fluxo Principal do Usuário

```
1. Acessa a landing page (/)
2. Clica em "Entrar com Google" → OAuth
3. É redirecionado para o app (/app)
4. Navega na sidebar: seção → categoria
5. Ou busca por nome / letra no campo de busca
6. Clica em um card de música → modal com cifra
7. Transpõe o tom se necessário
8. Adiciona ao repertório aberto
9. Abre modo apresentação para o ensaio/missa
10. Ao final: exporta o repertório como HTML/PDF
```

---

## 10. Critérios de Aceite

- [x] Landing page pública acessível sem login
- [x] Login OAuth com Google redireciona corretamente
- [x] Biblioteca carrega estrutura de pastas do Drive automaticamente
- [x] Home exibe "Mais tocadas" e "Todas as músicas" em cards
- [x] Banner inspiracional exibido no topo da home
- [x] Ícones de categoria/seção na sidebar
- [x] Criar / renomear / excluir categorias via sidebar
- [x] Cards de música com menu `⋯`: renomear, copiar, mover, excluir
- [x] Feedback "Salvando..." durante rename
- [x] Dropdowns não são clipados por overflow/transform dos cards
- [x] Transposição tonal funciona sem chamar o servidor
- [x] Modo Apresentação com navegação por teclado
- [x] Export HTML com logo inline, acordes em `#5b4b8a`, otimizado para impressão
- [x] Import por URL scrapa CifraClub e salva como .md estruturado
- [x] Repertórios persistem no Drive
- [x] Interface responsiva (mobile + desktop + tablet até 10")
- [x] Busca por nome (instantânea) e por letra (full-text Drive)
- [x] Painel de metadados editável (título, artista, tom, tags)
- [x] Editor inline com toolbar (selecionar tudo, copiar, duas colunas)
- [x] Confirmação ao sair do modo edição com alterações não salvas
- [x] Atalho iOS (apple-touch-icon)

---

## 11. Fora de Escopo (v2.x)

- Compartilhamento de repertórios entre grupos diferentes
- Histórico de versões de cifras
- Notificações / lembretes de ensaio
- Integração com YouTube / Spotify
- App nativo (iOS / Android)

---

## 12. Roadmap: Multi-usuário (v3.x)

O app hoje opera com um único repositório central compartilhado por todos os membros do grupo. A evolução prevista:

### Fase 1 — Repertórios por usuário
- Separar `_repertorios.json` por usuário: `_rep_{user_id}.json`
- Evita sobrescrita simultânea quando múltiplos músicos acessam ao mesmo tempo
- Cada músico mantém seus próprios repertórios privados

### Fase 2 — Múltiplos grupos
- Suporte a N grupos no mesmo app
- Tabela de configuração associando `user_email → group_id → CIFRAS_FOLDER_ID`
- Cada grupo tem sua pasta raiz independente no Drive
- Administrador do grupo pode convidar membros

### Fase 3 — Permissões granulares
- Músicos podem ter acesso somente-leitura
- Apenas líderes podem criar/mover/renomear/excluir arquivos e pastas
- Audit log das operações de escrita
