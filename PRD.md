# PRD — My Cifras
**Versão:** 2.0
**Produto:** Aplicação web para músicos litúrgicos e gospel gerenciarem cifras e repertórios
**Autor:** Lucas Almeida
**Status:** Em produção (v2.0)

---

## 1. Visão Geral

**My Cifras** é uma aplicação web que centraliza o acervo de cifras de um músico no Google Drive e oferece ferramentas para navegação, transposição tonal, montagem de repertórios e geração de documentos exportáveis. O foco é em músicos de grupos litúrgicos e gospel que precisam acessar cifras rapidamente em ensaios, missas e shows — em qualquer dispositivo.

---

## 2. Problema

Músicos litúrgicos acumulam dezenas ou centenas de cifras espalhadas em pastas do computador, grupos de WhatsApp e drives compartilhados. Na hora do ensaio ou da missa:

- É difícil encontrar a cifra certa rapidamente
- Transposição manual de tom é demorada e sujeita a erros
- Montar um repertório ordenado para impressão exige trabalho repetitivo
- O acervo não está acessível no celular durante a performance

---

## 3. Objetivo

Oferecer ao músico um acervo centralizado, sempre sincronizado com o Google Drive, acessível de qualquer dispositivo, com transposição em 1 clique, montagem de repertórios e exportação elegante para PDF.

---

## 4. Usuários

- Músico litúrgico / gospel (usuário principal, acesso individual ou compartilhado)
- Líder de grupo musical (organiza pastas, cria repertórios semanais)
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

- Lê automaticamente a estrutura de pastas do Google Drive (ou `CIFRAS_ROOT` local)
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

### 5.7 Gerenciamento de pastas

- Criar nova categoria: botão `＋` por seção na sidebar
- Renomear categoria: menu `⋯` → Renomear (edição inline)
- Excluir categoria: menu `⋯` → Excluir (somente pastas vazias)

### 5.8 Operações de arquivo

- **Renomear**: edição inline com feedback "Salvando..."
- **Copiar**: selecionar pasta de destino no seletor modal
- **Mover**: selecionar pasta de destino no seletor modal
- **Excluir**: confirmação inline, envia para lixeira do Drive

### 5.9 Importar cifra por URL ou texto

- Cole URL do CifraClub (ou outro site) → scraping automático
- Cole texto de cifra diretamente
- Preview com título, artista, tom e texto
- Selecionar seção e categoria destino
- Salva como `.md` no Drive com frontmatter YAML estruturado

### 5.10 Repertórios

- Criar, nomear e salvar múltiplos repertórios
- Adicionar músicas ao repertório aberto via botão `+ Repertório` nos cards
- Remover músicas do repertório
- Reordenar músicas (drag-and-drop)
- Persistência no Google Drive (`_repertorios.json`)

### 5.11 Modo Apresentação

- Abre repertório em tela cheia
- Navega cifra a cifra com botões, dots ou teclado
- Controles: zoom, fullscreen
- Teclado: `→/↓` próxima, `←/↑` anterior, `+/-` zoom, `F` fullscreen, `Esc` fechar

### 5.12 Exportação de repertório

- Gera HTML autocontido com todas as cifras
- Layout elegante e minimalista, pronto para impressão / salvar como PDF
- Logo `logo-mono-dark.svg` inlineado no documento
- Cabeçalho com título, data e quantidade de músicas
- Cada música: nome, badges de categoria e tom, cifra em fonte monospace
- Acordes destacados na cor primária (`#5b4b8a`)
- CSS `@media print` otimizado

### 5.13 Upload avulso de arquivo

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
CIFRAS_FOLDER_ID (raiz)
├── Missa/
│   ├── Entrada/
│   ├── Comunhão/
│   └── Final/
├── Gospel/
│   ├── Adoração/
│   ├── Louvor/
│   └── (raiz da seção — músicas sem subpasta)
└── _repertorios.json
```

Músicas na raiz de uma seção (sem categoria) ficam em `_raiz`.

---

## 9. Fluxo Principal do Usuário

```
1. Acessa a landing page (/)
2. Clica em "Entrar com Google" → OAuth
3. É redirecionado para o app (/app)
4. Navega na sidebar: seção → categoria
5. Clica em um card de música → modal com cifra
6. Transpõe o tom se necessário
7. Adiciona ao repertório aberto
8. Abre modo apresentação para o ensaio/missa
9. Ao final: exporta o repertório como HTML/PDF
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
- [x] Interface responsiva (mobile + desktop)

---

## 11. Fora de Escopo (v2.x)

- Editor de cifras em tempo real (editar o conteúdo do arquivo)
- Compartilhamento de repertórios entre usuários
- Histórico de versões de cifras
- Notificações / lembretes de ensaio
- Integração com YouTube / Spotify
- App nativo (iOS / Android)
