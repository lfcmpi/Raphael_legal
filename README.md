# Raphael Legal

Sistema de processamento de casos jurídicos com IA. Analisa briefings de clientes e gera automaticamente documentos legais (procurações, contratos de honorários) e pareceres jurídicos usando a Claude API.

## Stack

- **Backend:** Python 3.11+ / FastAPI / SQLAlchemy / SQLite
- **Frontend:** React 19 / TypeScript / Tailwind CSS / Vite
- **IA:** Claude API (Anthropic)
- **Infra:** Docker Compose

## Funcionalidades

- Cadastro e análise de casos jurídicos via briefing
- Geração automática de documentos (procuração, contrato de honorários)
- Panorama jurídico com análise de complexidade
- Ficha estruturada do caso (JSON)
- Dashboard com filtros e busca
- Gestão de usuários com 3 níveis de permissão (admin, manager, consulta)
- Login com email/senha ou Google OAuth
- API RESTful com autenticação JWT

## Início Rápido

### Com Docker (recomendado)

```bash
# Copiar variáveis de ambiente
cp .env.example .env
# Editar .env com suas chaves (ANTHROPIC_API_KEY, JWT_SECRET, etc.)

# Subir em modo produção
docker compose up --build

# Ou em modo desenvolvimento (hot-reload)
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

- **Frontend:** http://localhost:3000 (produção) ou http://localhost:5173 (dev)
- **API:** http://localhost:8000
- **Docs da API:** http://localhost:8000/docs

### Sem Docker

```bash
# Backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m api.seed        # cria usuário admin
uvicorn api.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Variáveis de Ambiente

| Variável | Descrição |
|---|---|
| `ANTHROPIC_API_KEY` | Chave da API Anthropic (obrigatória) |
| `JWT_SECRET` | Secret para tokens JWT |
| `ADMIN_EMAIL` | Email do usuário admin inicial |
| `ADMIN_PASSWORD` | Senha do usuário admin inicial |
| `DATABASE_URL` | URL do banco (default: SQLite local) |
| `GOOGLE_CLIENT_ID` | Client ID do Google OAuth (opcional) |
| `VITE_GOOGLE_CLIENT_ID` | Mesmo Client ID, para o frontend |

## Estrutura

```
├── api/                  # Backend FastAPI
│   ├── routes/           # Endpoints (auth, cases, documents, users)
│   ├── services/         # Lógica de negócio
│   ├── db_models.py      # Modelos SQLAlchemy
│   ├── schemas.py        # Schemas Pydantic
│   └── auth.py           # JWT e autenticação
├── frontend/             # React + Vite
│   └── src/
│       ├── pages/        # Páginas (Login, Dashboard, Cases, etc.)
│       ├── components/   # Componentes reutilizáveis
│       └── hooks/        # Hooks (auth, cases, users)
├── raphael_legal/        # Core: processador de casos com Claude
│   ├── processor.py      # Processamento via Claude API
│   ├── document_generator.py  # Geração de DOCX
│   └── prompts.py        # Prompts para a IA
├── templates/            # Templates DOCX (procuração, contrato)
└── tests/                # Testes unitários e de integração
```

## Comandos Make

```bash
make build    # Build das imagens Docker
make up       # Subir em produção
make dev      # Subir em desenvolvimento
make down     # Parar containers
make logs     # Ver logs
make test     # Rodar testes
make clean    # Limpar tudo (volumes, imagens)
```

## Licença

Projeto privado.
