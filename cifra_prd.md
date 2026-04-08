# PRD — Cifras App

**Versão:** 1.1
**Autor:** Lucas Almeida · Abril 2026
**Status:** MVP funcional com Drive + OAuth

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
4. Permite montar um repertório como uma playlist.
5. Gera um único HTML consolidado com todas as cifras do repertório.
6. Permite importar cifras por URL (CifraClub) ou texto colado.
7. Acessível de qualquer dispositivo com o link do app.

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
| `.doc` | ✅ | Fallback via Word COM (`pywin32`) |
| `.pdf` | ✅ | Via `PyMuPDF` |
| `.txt` | ✅ | Leitura direta |

---

## 6. Features — Estado atual (v1.1)

### 6.1 Autenticação
- Login com Google (OAuth 2.0)
- Sessão persistente com renovação automática de token
- Controle de acesso por compartilhamento de pasta no Drive
- Modo local sem autenticação para desenvolvimento

### 6.2 Biblioteca (Google Drive)
- Leitura automática da estrutura de pastas do Drive
- Navegação por seção e subcategoria na sidebar colapsável
- Contagem de músicas por categoria
- Suporte a .md, .docx, .doc, .pdf, .txt

### 6.3 Busca
- Busca global por nome de música em tempo real
- Limpar busca e retornar à categoria anterior

### 6.4 Visualização de cifra
- Modal com conteúdo completo da cifra
- Linhas de acordes destacadas em azul
- Frontmatter YAML removido automaticamente

### 6.5 Transposição tonal
- Notação americana (C, D, E, F, G, A, B)
- Controle por semitons (+/−) com display do intervalo
- Seleção direta do tom destino por botões de nota
- Detecção automática do tom base
- Reset para o tom original

### 6.6 Arquivo avulso
- Botão "Abrir arquivo" no header
- Drag & drop de arquivo na janela (overlay visual)
- Suporta todos os formatos da biblioteca

### 6.7 Repertório
- Painel lateral estilo playlist
- Adicionar / remover músicas com um clique
- Reordenar por drag & drop
- Nome do repertório editável
- Contador de músicas no header

### 6.8 Exportação
- HTML consolidado com todas as cifras do repertório
- Abre em nova aba (pronto para imprimir ou salvar como PDF)
- Inclui título, data e número de músicas

### 6.9 Importação de cifras
- Por URL (CifraClub e sites genéricos)
- Por texto colado
- Preenchimento automático de título, artista e tom
- Seleção de seção e categoria
- Salva como `.md` no Drive (ou localmente)

### 6.10 Migração de acervo
- Script `migrate.py` converte base existente (.docx/.pdf/.txt) para `.md`
- Gera frontmatter YAML com metadados extraídos da estrutura de pastas
- Modo `--dry-run` para simular sem gravar

---

## 7. Roadmap

### v1.2 — Persistência de repertórios
- Salvar repertórios para reusar em missas futuras (JSON local ou Drive)
- Histórico dos últimos repertórios gerados

### v1.3 — Qualidade de cifras
- Transposição aplicada também na exportação HTML
- Indicação visual do tom atual no card da música
- Suporte a notação brasileira (Dó, Ré, Mi...)

### v1.4 — Experiência mobile
- Layout responsivo otimizado para toque
- Modo tela cheia para leitura no celular
- Aumentar/diminuir fonte da cifra

### v1.5 — Acervo
- Editar cifra diretamente na interface
- Editar metadados (título, tom, categoria)
- Mover música entre categorias

### v2.0 — Produto publicado
- Deploy em produção (Railway ou Google Cloud Run)
- Publicação do OAuth (sem limite de usuários de teste)
- Exportação para PDF nativo
- Compartilhamento de repertório por link

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

---

## 9. Fora do escopo (v1)

- Sincronização automática com OneDrive
- Edição de cifras dentro do app (v1.5)
- Reprodução de áudio ou play-along
- Reconhecimento de tom por áudio
- Multi-tenant (cada grupo com seu Drive separado)
