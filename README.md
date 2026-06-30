# Bio Bone — Feed XML para Meta Catalog

Feed de produtos gerado automaticamente a partir do XML da Loja Integrada,
convertido para o formato aceito pelo Meta Gerenciador de Catálogos.

---

## Como funciona

```
Todo dia (06h e 18h, horário de Brasília)
        │
        ▼
GitHub Action executa generate_feed.py
        │
        ▼
Script baixa o XML da Loja Integrada
        │
        ▼
Converte para o formato Meta (campos obrigatórios, namespace correto, preço com BRL)
        │
        ▼
Salva docs/feed.xml e faz commit automático
        │
        ▼
GitHub Pages publica a URL — Meta lê e atualiza o catálogo
```

---

## Setup (fazer uma única vez)

### 1. Criar o repositório no GitHub

- Crie um repositório **público** chamado `biobone-meta-feed` (ou qualquer nome).
- Faça o upload de todos os arquivos deste pacote.

### 2. Ativar o GitHub Pages

- Vá em **Settings → Pages**.
- Em **Source**, selecione **Deploy from a branch**.
- Branch: `main` | Pasta: `/docs`.
- Clique em **Save**.
- Após alguns minutos, o feed estará disponível em:
  ```
  https://<seu-usuario>.github.io/biobone-meta-feed/feed.xml
  ```

### 3. Dar permissão de escrita ao GitHub Actions

- Vá em **Settings → Actions → General**.
- Em **Workflow permissions**, selecione **Read and write permissions**.
- Clique em **Save**.

### 4. Rodar o feed pela primeira vez

- Vá em **Actions → Atualizar Feed Meta → Run workflow**.
- Aguarde a execução (cerca de 30 segundos).
- Confirme que `docs/feed.xml` foi criado no repositório.

### 5. Configurar no Meta Gerenciador de Catálogos

- Acesse o **Gerenciador de Catálogos** da Bio Bone.
- Fontes de dados → **Adicionar itens** → **Feed de dados**.
- Cole a URL do GitHub Pages:
  ```
  https://<seu-usuario>.github.io/biobone-meta-feed/feed.xml
  ```
- Frequência de atualização: **Diária** (o GitHub Action já atualiza 2x por dia).

---

## Atualização manual

Se precisar forçar uma atualização fora do horário agendado:

1. Vá em **Actions → Atualizar Feed Meta**.
2. Clique em **Run workflow → Run workflow**.

Ou rode localmente:
```bash
python generate_feed.py
```
O arquivo `docs/feed.xml` será gerado na pasta local.

---

## Estrutura do repositório

```
biobone-meta-feed/
├── .github/
│   └── workflows/
│       └── update-feed.yml   # GitHub Action de atualização automática
├── docs/
│   ├── index.html            # Necessário para o GitHub Pages funcionar
│   └── feed.xml              # Feed gerado (criado automaticamente)
├── generate_feed.py          # Script de conversão
└── README.md
```

---

## Campos gerados no feed Meta

| Campo | Origem | Obrigatório |
|---|---|---|
| `g:id` | `g:id` do XML original | ✅ |
| `g:title` | `title` do item | ✅ |
| `g:description` | `description` do item | ✅ |
| `g:link` | `link` do item | ✅ |
| `g:image_link` | `g:image_link` | ✅ |
| `g:availability` | `g:availability` | ✅ |
| `g:condition` | `g:condition` | ✅ |
| `g:price` | `g:price` (força `BRL`) | ✅ |
| `g:sale_price` | `g:sale_price` | opcional |
| `g:brand` | `g:brand` | opcional |
| `g:product_type` | `g:product_type` | opcional |
| `g:gtin` | `g:gtin` | opcional |

Campos removidos do feed original que a Meta não aceita: `g:online_only`, `g:installment`, `g:months`, `g:amount`.
