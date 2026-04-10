# PRD — Cifras App

**Versão:** 1.2  
**Autor:** Lucas Almeida · Abril 2026  
**Status:** MVP funcional — Drive + OAuth + Repertórios persistidos + Modo Apresentação

---

## 1. Problema

Músicos que tocam em missas e eventos gospel precisam gerenciar um acervo pessoal de cifras e montar repertórios rapidamente — muitas vezes em cima da hora, no celular, sem acesso fácil a computador.

O fluxo atual é quebrado em três pontos:

- **Armazenamento fragmentado:** cifras em pastas no OneDrive, separadas por categoria. Útil para organização, mas impraticável para montar um repertório ágil.
- **Consolidação manual:** para ter todas as cifras do dia num único lugar, o músico precisa copiar arquivos manualmente.
- **Dependência de dispositivo:** o acervo pessoal (com o tom certo) só está acessível onde o OneDrive está sincronizado.

---

## 2. Solução

Aplicação web (Flask + HTML) que:

1. Lê a estrutura de pastas do Google Drive automaticamente.
2. Autentica músicos via OAuth 2.0 com Google.
3. Oferece navegação por categoria e busca por nome.
4. Permite montar e **salvar múltiplos repertórios** como playlists persistentes.
5. Gera um único HTML consolidado com todas as cifras do repertório.
6. Permite importar cifras por URL (CifraClub) ou texto colado.
7. Exibe cifras diretamente na tela em **modo apresentação** (sem exportar).
8. Acessível de qualquer dispositivo com o link do app (incluindo celular).

---

## 3. Usuário

**Persona primária:** Músico litúrgico ou gospel que toca em comunidades religiosas, com acervo próprio de cifras digitais e necessidade de montar repertórios semanais.

**Perfil técnico:** Usuário de Python com autonomia para rodar scripts locais, mas sem experiência em desenvolvimento web ou infraestrutura.

---

## 4. Estrutura de categorias suportada

```
Cifras/
├── Missa/
│   ├── Entrada
│   ├── Ato penitencial
│   ├── Glória
│   ├── Salmos
│   ├── Aclamação
│   ├── Ofertório
│   ├── Respostas Eucarísticas
│   ├── Santo
│   ├── Cordeiro
│   ├── Comunhão
│   ├── Pós Comunhão
│   ├── Final
│   ├── Mantras
│   └── Momentos especiais/
│       ├── Sequências de Páscoa
│       ├── Sequências de Pentecostes
│       ├── Cantos Marianos
│       └── Outras canções
└── Gospel/
    ├── Amor de Deus
    ├── Pecado e Salvação
    ├── Adoração
    ├── Entrega
    ├── Louvor
    ├── Fé e Conversão
    ├── Vida em Comunidade
    ├── Acolhida
    └── Outras
```

A aplicação detecta qualquer estrutura de pastas automaticamente.

---

## 5. Formatos de arquivo suportados

| Formato | Suporte | Observação |
|---|---|---|
| `.md` | ✅ | Formato preferido — frontmatter YAML + cifra em texto |
| `.docx` | ✅ | Via `python-docx` (lê parágrafos e tabelas) |
| `.doc` | ✅ | Fallback via Word COM (`pywin32`) — apenas Windows local |
| `.pdf` | ✅ | Via `PyMuPDF` |
| `.txt` | ✅ | Leitura direta |

---

## 6. Features — Estado atual (v1.2)

### 6.1 Autenticação
- Login com Google (OAuth 2.0)
- Sessão persistente com renovação automática de token
- Tratamento de `invalid_grant` (token expirado) com redirecionamento automático ao login
- Suporte a `EXTERNAL_URL` para deploy atrás de reverse proxy (Render, ngrok)
- Controle de acesso por compartilhamento de pasta no Drive
- Modo local sem autenticação para desenvolvimento

### 6.2 Biblioteca (Google Drive)
- Leitura automática da estrutura de pastas do Drive com cache (TTL 120s)
- Navegação por seção e subcategoria na sidebar colapsável
- Contagem de músicas por categoria
- Contador de visualizações por música (persistido em `views.json`)
- Suporte a .md, .docx, .doc, .pdf, .txt e Google Docs nativos

### 6.3 Busca
- Busca global por nome de música em tempo real
- Limpar busca e retornar à categoria anterior

### 6.4 Visualização de cifra
- Modal com conteúdo completo da cifra
- Linhas de acordes destacadas em azul
- Frontmatter YAML removido automaticamente
- **Zoom (A− / A+)** com atalhos de teclado `+` e `-`
- **Tela cheia** com atalho `F`

### 6.5 Transposição tonal
- Notação americana (C, D, E, F, G, A, B)
- Controle por semitons (+/−) com display do intervalo
- Seleção direta do tom destino por botões de nota
- Detecção automática do tom base
- Reset para o tom original
- Tom transposto preservado ao adicionar ao repertório

### 6.6 Arquivo avulso
- Botão "Abrir arquivo" no header
- Drag & drop de arquivo na janela (overlay visual)
- Suporta todos os formatos da biblioteca

### 6.7 Repertório (painel lateral)
- Painel lateral estilo playlist, sempre visível no desktop
- Adicionar / remover músicas com um clique
- Reordenar por drag & drop
- Nome do repertório editável
- Contador de músicas no header e badge no botão

### 6.8 Repertórios persistidos ✅ (novo em v1.2)
- Seção "Meus Repertórios" no painel lateral
- Criar, salvar, editar, excluir repertórios nomeados
- Dados persistidos em `_repertorios.json` no Google Drive (ou localmente)
- Múltiplos repertórios com lista ordenada por data de atualização
- Confirmação de exclusão inline (sem popups nativos)
- Botão "Salvar" com estado visual ("Salvando...") que previne duplicatas

### 6.9 Modo Apresentação ✅ (novo em v1.2)
- Botão ▶ em cada repertório salvo abre modo apresentação fullscreen
- Carrega todas as cifras do repertório sequencialmente
- Navegação com botões Anterior/Próxima ou teclado (`← →`, `PageUp/Down`)
- Pontinhos de progresso clicáveis (navegação direta)
- **Zoom** (A− / A+ / teclado `+` `-`)
- **Tela cheia** (botão / teclado `F`)
- Fechar com `Esc` ou botão ✕

### 6.10 Exportação
- HTML consolidado com todas as cifras do repertório
- Abre em nova aba (pronto para imprimir ou salvar como PDF)
- Inclui título, data e número de músicas
- Barra de progresso visual durante geração

### 6.11 Importação de cifras
- Por URL (CifraClub e sites genéricos)
- Por texto colado
- Preenchimento automático de título, artista e tom
- Seleção de seção e categoria
- Salva como `.md` no Drive (ou localmente)

### 6.12 Layout responsivo (mobile)
- Sidebar como drawer lateral (ícone hamburguer)
- Painel de repertório como drawer inferior
- Cards de músicas adaptados para toque
- Modo apresentação funcional em celular

### 6.13 Deploy (Docker + Render)
- `Dockerfile` com Python 3.12-slim e Gunicorn
- `render.yaml` para deploy automatizado na Render.com
- `ProxyFix` para `https://` correto no OAuth callback
- Variável `EXTERNAL_URL` para override da URL de callback

### 6.14 Migração de acervo
- Script `migrate.py` converte base existente (.docx/.pdf/.txt) para `.md`
- Gera frontmatter YAML com metadados extraídos da estrutura de pastas
- Modo `--dry-run` para simular sem gravar

---

## 7. Roadmap

### v1.3 — Qualidade de cifras
- Transposição aplicada também na exportação HTML
- Indicação visual do tom atual no card da música
- Suporte a notação brasileira (Dó, Ré, Mi...)
- Edição de metadados (título, tom, categoria) diretamente na interface

### v1.4 — Acervo
- Editar cifra diretamente na interface (já parcialmente implementado)
- Mover música entre categorias
- Busca avançada (por categoria, tom, artista)

### v2.0 — Produto publicado
- Deploy em produção com OAuth publicado (sem limite de usuários de teste)
- Exportação para PDF nativo
- Compartilhamento de repertório por link
- Multi-tenant (cada grupo com seu Drive separado)

---

## 8. Decisões técnicas

| Decisão | Escolha | Motivo |
|---|---|---|
| Backend | Flask (Python) | Autonomia do usuário para debugar |
| Frontend | HTML/CSS/JS puro | Sem dependências de build, funciona offline |
| Armazenamento | Google Drive | Acesso de qualquer dispositivo, controle de acesso nativo |
| Autenticação | OAuth 2.0 Google | Sem gerenciar senhas, acesso controlado pelo Drive |
| Formato de cifra | `.md` com frontmatter | Legível, estruturado, git-friendly |
| Extração de texto | python-docx + PyMuPDF | Melhor suporte aos formatos usados |
| Transposição | Regex em JS no cliente | Sem round-trip ao servidor |
| Exportação | HTML gerado no servidor | Portátil, imprimível |
| Persistência de repertórios | JSON no Drive / local | Zero infra extra, backup automático no Drive |
| Deploy | Docker + Render | Gratuito, fácil de configurar, HTTPS automático |

---

## 9. Fora do escopo (v1)

- Sincronização automática com OneDrive
- Reprodução de áudio ou play-along
- Reconhecimento de tom por áudio
- Multi-tenant (cada grupo com seu Drive separado)
