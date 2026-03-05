# PRP: Frontend Web — Escritório Raphael

**Gerado em:** 2026-03-04
**Confidence Score:** 7/10
**Origem:** Requisito de interface gráfica com login, menus por etapa, consulta por processo, upload de documentos + legal-case-processor-mvp-prp.md

---

## 1. Core (OBRIGATÓRIO)

### Goal
Construir uma aplicação web completa (FastAPI + React) com autenticação, dashboard de casos, processamento interativo por fases, upload de documentos e download de artefatos gerados.

### Why
O CLI atual exige que Raphael use o terminal para submeter casos e navegar pelo filesystem para acessar resultados. Uma interface web permite:
- Login seguro com senha pessoal
- Submissão de casos com upload de documentos anexos
- Acompanhamento visual do processamento em 3 etapas (Ficha → Panorama → Documentos)
- Consulta e busca por casos anteriores
- Download direto de procurações, contratos e panoramas

### What
Aplicação web full-stack:
1. **Backend API (FastAPI)** — expõe o `CaseProcessor` existente como REST API + WebSocket para status em tempo real
2. **Banco de dados (SQLite)** — persistência de casos, usuários e documentos uploadados
3. **Frontend (React + Vite + TypeScript)** — SPA com login, dashboard, formulário por fases, visualização de resultados
4. **Autenticação JWT** — login/senha simples (usuário único: Raphael)

### Success Criteria
- [ ] Login com email/senha retorna JWT válido
- [ ] Dashboard lista todos os casos com filtros (matéria, complexidade, data)
- [ ] Busca por caso_id, nome do cliente ou matéria funciona
- [ ] Formulário de novo caso aceita briefing em texto + upload de arquivos (.pdf, .jpg, .png, .txt, .docx)
- [ ] Processamento executa as 3 etapas com feedback visual de progresso
- [ ] Resultado exibe ficha estruturada, panorama estratégico e documentos gerados
- [ ] Marcadores ⚠️ PENDENTE e [VERIFICAR] renderizados com destaque visual
- [ ] Alertas 🔴 CASO COMPLEXO exibidos com banner vermelho
- [ ] Download de DOCX (procuração, contrato) funciona
- [ ] Download de panorama.md e ficha.json funciona
- [ ] Interface 100% em português
- [ ] Responsivo (funciona em desktop e tablet)

---

## 2. Context

### Codebase Analysis
```
Backend já implementado e funcional:
- raphael_legal/processor.py → CaseProcessor.process(briefing) → CaseOutput
- raphael_legal/models.py → FichaCaso, CaseOutput, ParteProcessual, enums
- raphael_legal/document_generator.py → DocumentGenerator.generate(case_output, output_dir)
- raphael_legal/prompts.py → build_api_params(), SYSTEM_PROMPT
- raphael_legal/config.py → Settings (API key, paths)
- raphael_legal/cli.py → CLI funcional (será preservado, API é paralela)

Padrões identificados:
- Pydantic v2 para models (model_dump_json, BaseModel)
- anthropic SDK com tool_use para extração estruturada
- docxtpl para geração de DOCX
- Sem ORM/banco de dados atualmente (filesystem only)
- Python 3.11+, setuptools
```

### External Documentation
```
- FastAPI: https://fastapi.tiangolo.com/
- SQLAlchemy 2.0: https://docs.sqlalchemy.org/en/20/
- React + Vite: https://vite.dev/guide/
- TanStack Query: https://tanstack.com/query/latest
- Tailwind CSS: https://tailwindcss.com/docs
- python-jose (JWT): https://python-jose.readthedocs.io/
- python-multipart (upload): https://github.com/Kludex/python-multipart
```

---

## 3. Tree Structure

### Before (Current)
```
raphael/
├── raphael_legal/          # Backend CLI (existente — NÃO TOCAR)
│   ├── __init__.py
│   ├── __main__.py
│   ├── config.py
│   ├── models.py
│   ├── processor.py
│   ├── prompts.py
│   ├── document_generator.py
│   └── cli.py
├── templates/              # DOCX templates (existente)
├── tests/                  # Testes existentes
├── insumos/                # Prompts e planejamento
└── pyproject.toml
```

### After (Desired)
```
raphael/
├── raphael_legal/              # Backend existente (PRESERVADO)
│   ├── (todos os arquivos existentes inalterados)
│   └── ...
├── api/                        # NEW: FastAPI backend
│   ├── __init__.py
│   ├── main.py                 # FastAPI app, CORS, lifespan
│   ├── auth.py                 # JWT auth, login, hash de senha
│   ├── database.py             # SQLAlchemy engine + session
│   ├── db_models.py            # SQLAlchemy models (User, Case, Document)
│   ├── schemas.py              # Pydantic schemas para API (request/response)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth_routes.py      # POST /api/auth/login
│   │   ├── cases_routes.py     # CRUD /api/cases
│   │   └── documents_routes.py # Upload/download /api/documents
│   ├── services/
│   │   ├── __init__.py
│   │   └── case_service.py     # Orquestra CaseProcessor + DB + DocumentGenerator
│   └── seed.py                 # Script para criar usuário admin inicial
├── frontend/                   # NEW: React SPA
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── index.html
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx             # Router principal
│   │   ├── api/
│   │   │   └── client.ts       # Axios/fetch wrapper com JWT
│   │   ├── hooks/
│   │   │   ├── useAuth.ts      # Auth context + JWT management
│   │   │   └── useCases.ts     # TanStack Query hooks para casos
│   │   ├── pages/
│   │   │   ├── LoginPage.tsx
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── NewCasePage.tsx
│   │   │   └── CaseDetailPage.tsx
│   │   ├── components/
│   │   │   ├── Layout.tsx          # Shell com sidebar/nav
│   │   │   ├── ProtectedRoute.tsx  # Route guard
│   │   │   ├── CaseCard.tsx        # Card do caso no dashboard
│   │   │   ├── CaseFilters.tsx     # Filtros (matéria, complexidade, busca)
│   │   │   ├── BriefingForm.tsx    # Formulário de briefing + upload
│   │   │   ├── ProcessingStatus.tsx# Indicador de progresso 3 etapas
│   │   │   ├── FichaView.tsx       # Visualização da ficha do caso
│   │   │   ├── PanoramaView.tsx    # Renderização do panorama (markdown)
│   │   │   ├── DocumentsList.tsx   # Lista de documentos com download
│   │   │   └── AlertBanner.tsx     # Banner para CASO COMPLEXO
│   │   └── styles/
│   │       └── globals.css         # Tailwind base + custom
│   └── public/
│       └── favicon.ico
├── uploads/                    # NEW: Arquivos uploadados (runtime)
├── templates/                  # DOCX templates (existente)
├── tests/                      # Testes existentes (preservados)
│   ├── (testes existentes...)
│   └── test_api/               # NEW: Testes da API
│       ├── __init__.py
│       ├── test_auth.py
│       ├── test_cases.py
│       └── test_documents.py
├── pyproject.toml              # Atualizado com deps da API
└── .env.example                # Atualizado com novas vars
```

---

## 4. Known Gotchas

| Gotcha | Solução |
|--------|---------|
| Processamento do Claude demora 30-90s (blocking) | Usar BackgroundTasks do FastAPI; frontend faz polling ou WebSocket para status |
| Upload de arquivos grandes (PDFs de contratos) | Limitar a 10MB por arquivo; validar content-type no backend |
| SQLite não suporta acesso concorrente pesado | Adequado para usuário único; usar `check_same_thread=False` |
| CORS entre frontend (Vite :5173) e backend (FastAPI :8000) | Configurar CORSMiddleware no FastAPI com origins permitidos |
| JWT token expirado causa UX ruim | Interceptor no frontend redireciona para login; token com 24h de validade |
| Arquivos uploadados não devem ir para git | Adicionar `uploads/` ao .gitignore |
| Markdown do panorama precisa renderizar no frontend | Usar react-markdown com rehype-raw para HTML seguro |
| DOCX não pode ser pré-visualizado no browser | Oferecer apenas download; mostrar conteúdo como markdown |
| CaseProcessor importa de `raphael_legal` (path relativo) | API roda na raiz do projeto; imports funcionam se PYTHONPATH inclui raiz |
| Senha do Raphael precisa ser hasheada | Usar bcrypt via passlib; seed.py cria usuário com hash |

---

## 5. Implementation Blueprint

### Data Models / Schemas

```python
# api/db_models.py — SQLAlchemy models
from sqlalchemy import Column, String, DateTime, Text, Enum as SAEnum, JSON, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship
import uuid
from datetime import datetime

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: str  # UUID
    email: str  # unique
    hashed_password: str
    nome: str
    created_at: datetime

class Case(Base):
    __tablename__ = "cases"
    id: str  # UUID
    caso_id: str  # ID gerado pelo processador (ex: "20260304-a1b2c3")
    user_id: str  # FK → users
    briefing: str  # Texto original do briefing
    status: str  # "pending" | "processing" | "completed" | "error"
    materia: str | None
    complexidade: str | None
    cliente_nome: str | None
    resumo: str | None
    ficha_json: dict | None  # FichaCaso serializada
    panorama_md: str | None
    output_completo_md: str | None
    alerta_complexo: str | None
    error_message: str | None
    created_at: datetime
    processed_at: datetime | None

class Document(Base):
    __tablename__ = "documents"
    id: str  # UUID
    case_id: str  # FK → cases
    tipo: str  # "upload" | "procuracao" | "contrato" | "panorama" | "ficha"
    nome_arquivo: str
    caminho: str  # Path no filesystem
    content_type: str | None
    tamanho: int  # bytes
    created_at: datetime
```

```python
# api/schemas.py — Pydantic schemas para API
from pydantic import BaseModel
from datetime import datetime

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class CaseCreateRequest(BaseModel):
    briefing: str

class CaseSummary(BaseModel):
    id: str
    caso_id: str
    status: str
    materia: str | None
    complexidade: str | None
    cliente_nome: str | None
    resumo: str | None
    alerta_complexo: str | None
    created_at: datetime
    processed_at: datetime | None

class CaseDetail(CaseSummary):
    briefing: str
    ficha_json: dict | None
    panorama_md: str | None
    output_completo_md: str | None
    documentos: list["DocumentInfo"]

class DocumentInfo(BaseModel):
    id: str
    tipo: str
    nome_arquivo: str
    tamanho: int
    created_at: datetime

class CaseListResponse(BaseModel):
    cases: list[CaseSummary]
    total: int
```

### API Contracts

```yaml
# Autenticação
POST /api/auth/login:
  request: { email: str, password: str }
  response: { access_token: str, token_type: "bearer" }

# Casos
GET /api/cases:
  query: ?materia=Marcas&complexidade=Simples&search=João&page=1&per_page=20
  response: { cases: CaseSummary[], total: int }
  auth: Bearer JWT

GET /api/cases/{case_id}:
  response: CaseDetail
  auth: Bearer JWT

POST /api/cases:
  request: { briefing: str }
  response: CaseSummary (status: "pending")
  auth: Bearer JWT
  nota: Dispara processamento em background

POST /api/cases/{case_id}/process:
  response: { status: "processing" }
  auth: Bearer JWT
  nota: Re-processa um caso (se erro anterior)

GET /api/cases/{case_id}/status:
  response: { status: str, progress: str }
  auth: Bearer JWT
  nota: Polling endpoint para acompanhar processamento

# Documentos
POST /api/cases/{case_id}/upload:
  request: multipart/form-data (files[])
  response: DocumentInfo[]
  auth: Bearer JWT

GET /api/documents/{doc_id}/download:
  response: file stream (DOCX, PDF, etc.)
  auth: Bearer JWT
```

### Integration Points

| Ponto | Arquivo | Modificação |
|-------|---------|-------------|
| Expor CaseProcessor como API | `api/services/case_service.py` | create — wrap processor + DB save |
| Auth JWT | `api/auth.py` | create — login, verify, hash password |
| DB connection | `api/database.py` | create — SQLAlchemy async engine |
| API routes | `api/routes/*.py` | create — FastAPI routers |
| Frontend API client | `frontend/src/api/client.ts` | create — fetch wrapper com JWT |
| React pages | `frontend/src/pages/*.tsx` | create — 4 páginas principais |
| Atualizar deps | `pyproject.toml` | modify — adicionar FastAPI, SQLAlchemy, etc. |
| Atualizar .env.example | `.env.example` | modify — JWT_SECRET, ADMIN_EMAIL, etc. |
| Atualizar .gitignore | `.gitignore` | modify — uploads/, frontend/node_modules/, *.db |

---

## 6. Tasks

### Task 1: Scaffold da API FastAPI + banco de dados
**Keywords:** create API structure, wire FastAPI, create SQLAlchemy models, wire database
**Files:**
- `api/__init__.py` (create)
- `api/main.py` (create)
- `api/database.py` (create)
- `api/db_models.py` (create)
- `api/schemas.py` (create)
- `api/seed.py` (create)
- `pyproject.toml` (modify — adicionar deps: fastapi, uvicorn, sqlalchemy, python-jose, passlib, bcrypt, python-multipart)
- `.env.example` (modify — adicionar JWT_SECRET, ADMIN_EMAIL, ADMIN_PASSWORD)
- `.gitignore` (modify — adicionar uploads/, *.db, frontend/node_modules/, frontend/dist/)

**Description:**
Criar estrutura FastAPI com SQLAlchemy (SQLite). `api/main.py` cria app FastAPI com CORS, lifespan que cria tabelas. `api/database.py` configura engine SQLite + sessionmaker. `api/db_models.py` define User, Case, Document conforme blueprint. `api/schemas.py` define schemas Pydantic para request/response. `api/seed.py` script que cria usuário admin (lê email/senha de env vars e salva com bcrypt hash).

**Validation:**
```bash
python -c "from api.main import app; print(app.title)"
python -c "from api.db_models import Base, User, Case, Document; print('OK')"
```

---

### Task 2: Implementar autenticação JWT
**Keywords:** create auth module, wire JWT, wire password hashing, create login route
**Files:**
- `api/auth.py` (create)
- `api/routes/__init__.py` (create)
- `api/routes/auth_routes.py` (create)

**Description:**
`api/auth.py`: funções `hash_password(plain)`, `verify_password(plain, hashed)`, `create_access_token(data, expires_delta)`, `get_current_user(token)` dependency do FastAPI. Usar `passlib[bcrypt]` para hash e `python-jose` para JWT. Token expira em 24h. `api/routes/auth_routes.py`: router com `POST /api/auth/login` que valida email+senha contra DB e retorna JWT.

**Validation:**
```bash
python -c "from api.auth import hash_password, verify_password; h = hash_password('test'); assert verify_password('test', h)"
```

---

### Task 3: Implementar rotas de casos (CRUD + processamento)
**Keywords:** create case routes, wire CaseProcessor, wire background processing
**Files:**
- `api/routes/cases_routes.py` (create)
- `api/services/__init__.py` (create)
- `api/services/case_service.py` (create)

**Description:**
`api/services/case_service.py`: classe `CaseService` que:
1. `create_case(briefing, user_id)` → salva caso no DB com status="pending", retorna CaseSummary
2. `process_case(case_id)` → atualiza status="processing", chama `CaseProcessor.process(briefing)`, salva resultado (ficha_json, panorama_md, output_completo_md, materia, complexidade, etc.) no DB, gera DOCX via `DocumentGenerator`, salva registros de Document no DB, atualiza status="completed". Em caso de erro: status="error", error_message=str(e).
3. `get_case(case_id)` → retorna CaseDetail com documentos
4. `list_cases(user_id, filters)` → retorna lista paginada com filtros opcionais (materia, complexidade, search)

`api/routes/cases_routes.py`: router com:
- `GET /api/cases` — lista paginada com filtros
- `GET /api/cases/{case_id}` — detalhe do caso
- `POST /api/cases` — cria caso + dispara processamento em `BackgroundTasks`
- `POST /api/cases/{case_id}/process` — re-processa caso
- `GET /api/cases/{case_id}/status` — retorna status atual

Todos endpoints protegidos com `Depends(get_current_user)`.

**Validation:**
```bash
python -m pytest tests/test_api/test_cases.py -v
```

---

### Task 4: Implementar upload e download de documentos
**Keywords:** create document routes, wire file upload, wire file download
**Files:**
- `api/routes/documents_routes.py` (create)

**Description:**
Router com:
- `POST /api/cases/{case_id}/upload` — aceita multipart/form-data com múltiplos arquivos. Valida: max 10MB por arquivo, content-types permitidos (.pdf, .jpg, .jpeg, .png, .txt, .docx, .doc). Salva em `uploads/{case_id}/{filename}`. Cria registro Document no DB com tipo="upload". Retorna lista de DocumentInfo.
- `GET /api/documents/{doc_id}/download` — busca Document no DB, retorna FileResponse com o arquivo. Suporta tanto arquivos uploadados quanto gerados (procuracao.docx, contrato.docx).

Criar diretório `uploads/` se não existir. Proteger com `Depends(get_current_user)`.

**Validation:**
```bash
python -m pytest tests/test_api/test_documents.py -v
```

---

### Task 5: Registrar routers na app FastAPI e testar API completa
**Keywords:** wire routers, wire CORS, create API tests
**Files:**
- `api/main.py` (modify — registrar routers)
- `tests/test_api/__init__.py` (create)
- `tests/test_api/test_auth.py` (create)
- `tests/test_api/test_cases.py` (create)
- `tests/test_api/test_documents.py` (create)

**Description:**
Registrar todos os routers em `api/main.py` com prefixo `/api`. Configurar CORS para permitir `http://localhost:5173` (Vite dev) e `http://localhost:3000`. Configurar lifespan para criar tabelas + seed admin.

Testes com `httpx.AsyncClient` + `TestClient` do FastAPI:
- `test_auth.py`: login com credenciais válidas retorna JWT; login inválido retorna 401
- `test_cases.py`: CRUD de casos com mock do CaseProcessor; verificar filtros e paginação
- `test_documents.py`: upload de arquivo; download de arquivo; rejeição de arquivo grande

**Validation:**
```bash
python -m pytest tests/test_api/ -v --tb=short
```

---

### Task 6: Scaffold do frontend React + Vite + Tailwind
**Keywords:** create React project, wire Vite, wire Tailwind, create base layout
**Files:**
- `frontend/package.json` (create)
- `frontend/vite.config.ts` (create)
- `frontend/tsconfig.json` (create)
- `frontend/tailwind.config.js` (create)
- `frontend/postcss.config.js` (create)
- `frontend/index.html` (create)
- `frontend/src/main.tsx` (create)
- `frontend/src/App.tsx` (create)
- `frontend/src/styles/globals.css` (create)
- `frontend/src/api/client.ts` (create)
- `frontend/src/hooks/useAuth.ts` (create)
- `frontend/src/components/Layout.tsx` (create)
- `frontend/src/components/ProtectedRoute.tsx` (create)

**Description:**
Criar projeto React com Vite + TypeScript. Instalar deps: `react-router-dom`, `@tanstack/react-query`, `tailwindcss`, `react-markdown`, `axios`. Configurar Tailwind com preset de cores jurídicas (azul-marinho, cinza, branco). Vite proxy `/api` para `http://localhost:8000`.

`api/client.ts`: wrapper axios que injeta JWT do localStorage em Authorization header. Interceptor para 401 → redireciona para /login.

`useAuth.ts`: React context com `login(email, password)`, `logout()`, `isAuthenticated`, `user`. Persiste token em localStorage.

`Layout.tsx`: shell com sidebar (navegação: Dashboard, Novo Caso) + header com nome do usuário + logout. Sidebar colapsável em mobile.

`ProtectedRoute.tsx`: wrapper que redireciona para /login se não autenticado.

**Validation:**
```bash
cd frontend && npm install && npm run build
```

---

### Task 7: Implementar página de Login
**Keywords:** create LoginPage, wire auth form, wire JWT storage
**Files:**
- `frontend/src/pages/LoginPage.tsx` (create)

**Description:**
Página de login centrada com:
- Logo/título "Raphael Legal"
- Campo email + campo senha
- Botão "Entrar"
- Loading state durante autenticação
- Mensagem de erro em caso de credenciais inválidas
- Redirect para /dashboard após login bem-sucedido

Design: fundo azul-marinho escuro, card branco centralizado, fonte serif para título. Interface limpa e profissional.

**Validation:**
```bash
cd frontend && npm run build
```

---

### Task 8: Implementar Dashboard (lista de casos)
**Keywords:** create DashboardPage, create CaseCard, create CaseFilters, wire TanStack Query
**Files:**
- `frontend/src/pages/DashboardPage.tsx` (create)
- `frontend/src/components/CaseCard.tsx` (create)
- `frontend/src/components/CaseFilters.tsx` (create)
- `frontend/src/hooks/useCases.ts` (create)

**Description:**
`useCases.ts`: hooks TanStack Query: `useCasesList(filters)`, `useCaseDetail(id)`, `useCreateCase()`, `useProcessCase()`.

`DashboardPage.tsx`:
- Header com título "Meus Casos" + botão "Novo Caso"
- Barra de filtros: busca por texto (cliente, caso_id), dropdown matéria (todos os valores de MateriaJuridica), dropdown complexidade
- Grid/lista de CaseCards ordenados por data (mais recente primeiro)
- Paginação
- Estado vazio: "Nenhum caso encontrado. Clique em 'Novo Caso' para começar."
- Loading skeleton enquanto carrega

`CaseCard.tsx`:
- Caso_id + data de criação
- Nome do cliente (ou "⚠️ Sem nome")
- Badge de matéria (cores por categoria)
- Badge de complexidade (verde/amarelo/vermelho)
- Badge de status (pending/processing/completed/error)
- Resumo truncado (2 linhas)
- Alerta CASO COMPLEXO como ícone vermelho
- Click → navega para /cases/{id}

**Validation:**
```bash
cd frontend && npm run build
```

---

### Task 9: Implementar página Novo Caso (formulário + upload)
**Keywords:** create NewCasePage, create BriefingForm, wire file upload, wire case creation
**Files:**
- `frontend/src/pages/NewCasePage.tsx` (create)
- `frontend/src/components/BriefingForm.tsx` (create)
- `frontend/src/components/ProcessingStatus.tsx` (create)

**Description:**
`NewCasePage.tsx`: página com 2 estados:
1. **Formulário** (antes de submeter):
   - Título "Novo Caso"
   - Textarea grande para briefing (placeholder: "Descreva o caso do cliente. Pode ser informal, como uma transcrição de áudio...")
   - Zona de upload drag-and-drop para documentos anexos (multi-file, aceita PDF/imagens/TXT/DOCX)
   - Lista de arquivos anexados com botão para remover
   - Botão "Processar Caso"

2. **Processamento** (após submeter):
   - Muda para ProcessingStatus
   - Polling do endpoint /api/cases/{id}/status a cada 3 segundos
   - Quando completo → redireciona para /cases/{id}

`BriefingForm.tsx`:
- Textarea com min-height 200px
- Drag-and-drop zone com ícone de upload
- Validação: briefing não pode ser vazio
- Ao submeter: POST /api/cases com briefing, depois POST /api/cases/{id}/upload para cada arquivo

`ProcessingStatus.tsx`:
- 3 etapas visuais em stepper horizontal: "1. Ficha do Caso" → "2. Panorama Estratégico" → "3. Documentos"
- Etapa atual animada (spinner)
- Etapas concluídas com checkmark verde
- Texto de status: "Processando...", "Concluído!", "Erro — tente novamente"
- Barra de progresso estimada

**Validation:**
```bash
cd frontend && npm run build
```

---

### Task 10: Implementar página Detalhe do Caso
**Keywords:** create CaseDetailPage, create FichaView, create PanoramaView, create DocumentsList, create AlertBanner
**Files:**
- `frontend/src/pages/CaseDetailPage.tsx` (create)
- `frontend/src/components/FichaView.tsx` (create)
- `frontend/src/components/PanoramaView.tsx` (create)
- `frontend/src/components/DocumentsList.tsx` (create)
- `frontend/src/components/AlertBanner.tsx` (create)

**Description:**
`CaseDetailPage.tsx`: página com tabs ou seções accordion:
- Header: caso_id + matéria badge + complexidade badge + data
- Se alerta_complexo: AlertBanner vermelho no topo
- Tab/Seção 1: **Ficha do Caso** (FichaView)
- Tab/Seção 2: **Panorama Estratégico** (PanoramaView)
- Tab/Seção 3: **Documentos** (DocumentsList)
- Tab/Seção 4: **Briefing Original** (texto original colapsável)
- Se status="processing": mostrar ProcessingStatus no lugar do conteúdo
- Se status="error": mostrar mensagem de erro + botão "Reprocessar"

`FichaView.tsx`:
- Exibe dados da FichaCaso em layout de formulário read-only
- Dados do cliente em seção: nome, CPF/CNPJ, contato, endereço
- Dados da parte contrária (se existir)
- Resumo do caso
- Documentos recebidos (lista com bullets)
- Documentos pendentes (lista com badges ⚠️)
- Campos com "⚠️ PENDENTE" renderizados com background amarelo

`PanoramaView.tsx`:
- Renderiza panorama_md como markdown formatado (react-markdown)
- Marcadores [VERIFICAR] renderizados com highlight laranja e tooltip "Verificar citação legal"
- Seções de vias estratégicas com cards visuais

`DocumentsList.tsx`:
- Lista de documentos em 2 seções: "Documentos Gerados" e "Documentos Enviados" (uploads)
- Cada documento: ícone por tipo (DOCX, PDF, imagem), nome, tamanho, botão download
- Botão download chama GET /api/documents/{id}/download

`AlertBanner.tsx`:
- Banner vermelho com ícone 🔴 e texto do alerta_complexo
- Estilo: bg-red-50, border-red-500, text-red-800

**Validation:**
```bash
cd frontend && npm run build
```

---

### Task 11: Conectar Router e finalizar App
**Keywords:** wire React Router, wire all pages, create navigation
**Files:**
- `frontend/src/App.tsx` (modify — configurar rotas)
- `frontend/src/components/Layout.tsx` (modify — links de navegação ativos)

**Description:**
Configurar React Router DOM:
```
/login → LoginPage (sem Layout)
/dashboard → DashboardPage (com Layout)
/cases/new → NewCasePage (com Layout)
/cases/:id → CaseDetailPage (com Layout)
/ → redirect para /dashboard
```

Layout sidebar com links ativos (highlight na página atual). Botão "Novo Caso" sempre visível na sidebar. Logout funcional.

**Validation:**
```bash
cd frontend && npm run build
```

---

### Task 12: Script de inicialização e documentação
**Keywords:** create startup scripts, update env example, create run instructions
**Files:**
- `scripts/start_api.sh` (create)
- `scripts/start_frontend.sh` (create)
- `.env.example` (modify)

**Description:**
`scripts/start_api.sh`:
```bash
#!/bin/bash
# Inicializa banco + seed admin + inicia API
python -m api.seed
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

`scripts/start_frontend.sh`:
```bash
#!/bin/bash
cd frontend && npm run dev
```

Atualizar `.env.example` com todas as variáveis necessárias:
```
ANTHROPIC_API_KEY=sk-...
MODEL_NAME=claude-sonnet-4-6
OUTPUT_DIR=output
TEMPLATES_DIR=templates
JWT_SECRET=your-secret-key-here
ADMIN_EMAIL=raphael@email.com
ADMIN_PASSWORD=change-me
DATABASE_URL=sqlite:///./raphael.db
```

**Validation:**
```bash
bash scripts/start_api.sh &
sleep 3
curl -s http://localhost:8000/docs | head -5
kill %1
```

---

## 7. Validation Gating

### Level 1: Syntax & Types
```bash
# Backend
python -m py_compile api/main.py
python -m py_compile api/auth.py
python -m py_compile api/database.py
python -m py_compile api/db_models.py
python -m py_compile api/schemas.py
python -m py_compile api/routes/auth_routes.py
python -m py_compile api/routes/cases_routes.py
python -m py_compile api/routes/documents_routes.py
python -m py_compile api/services/case_service.py

# Frontend
cd frontend && npx tsc --noEmit
```
**Critério:** Zero errors em todos os módulos

### Level 2: Unit Tests
```bash
# Backend API tests
python -m pytest tests/test_api/ -v --tb=short

# Frontend build (verifica que compila sem erro)
cd frontend && npm run build
```
**Critério:** All tests pass, frontend build succeeds

### Level 3: Integration Test
```bash
# 1. Iniciar API
uvicorn api.main:app --port 8000 &
sleep 2

# 2. Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"raphael@email.com","password":"change-me"}' | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo "Token: ${TOKEN:0:20}..."

# 3. Criar caso
CASE=$(curl -s -X POST http://localhost:8000/api/cases \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"briefing":"Cliente João Silva, CPF 123.456.789-00, quer registrar marca Café Premium no INPI."}')

echo "Caso: $CASE"

# 4. Listar casos
curl -s http://localhost:8000/api/cases \
  -H "Authorization: Bearer $TOKEN"

kill %1
```
**Critério:** Login retorna token, caso é criado, listagem retorna o caso

### Level 4: E2E Frontend
```
1. Abrir http://localhost:5173/login
2. Fazer login com email/senha
3. Dashboard exibe lista de casos (pode estar vazio)
4. Clicar "Novo Caso"
5. Preencher briefing e submeter
6. Ver indicador de processamento
7. Após conclusão, ver ficha + panorama + documentos
8. Fazer download de um DOCX
9. Voltar ao dashboard e ver o caso na lista
10. Filtrar por matéria
11. Console sem erros JavaScript
```
**Critério:** Fluxo completo funciona sem erros

---

## 8. Final Checklist

### Quality Gates
- [ ] All Level 1 validations pass (py_compile + tsc)
- [ ] All Level 2 validations pass (pytest + npm build)
- [ ] Level 3 integration test passa (API funcional)
- [ ] Level 4 E2E visual confirmado
- [ ] Login/logout funciona corretamente
- [ ] JWT expira e redireciona para login
- [ ] Upload de arquivos funciona (múltiplos formatos)
- [ ] Download de DOCX funciona
- [ ] Filtros de busca no dashboard funcionam
- [ ] Marcadores ⚠️ PENDENTE renderizados com destaque amarelo
- [ ] Marcadores [VERIFICAR] renderizados com destaque laranja
- [ ] Alertas 🔴 CASO COMPLEXO exibidos como banner vermelho
- [ ] Interface 100% em português
- [ ] .env.example documentado (sem secrets reais)
- [ ] uploads/ e *.db no .gitignore
- [ ] Backend existente (raphael_legal/) inalterado
- [ ] Testes existentes (tests/) continuam passando

### Patterns to Avoid
- [ ] Não hardcodar JWT_SECRET (usar .env)
- [ ] Não armazenar senha em texto plano (usar bcrypt)
- [ ] Não expor API sem autenticação
- [ ] Não permitir upload de arquivos sem validação de tipo/tamanho
- [ ] Não logar conteúdo de briefings ou dados de clientes
- [ ] Não servir frontend em produção via Vite dev server (usar build estático)
- [ ] Não modificar código existente em raphael_legal/
- [ ] Não usar `any` types no TypeScript (exceto APIs externas)

---

## 9. Confidence Assessment

**Score:** 7/10

**Factors:**
- [+2] Backend completo e funcional (CaseProcessor, DocumentGenerator, models)
- [+1] API surface clara (CaseProcessor.process() retorna CaseOutput bem tipado)
- [+1] Stack bem documentada (FastAPI + React + SQLAlchemy)
- [+1] Caso de uso simples (usuário único, CRUD + processamento)
- [+1] Pydantic models existentes facilitam schemas da API
- [-1] Frontend React requer build toolchain separada (Node.js)
- [-1] Processamento assíncrono (background tasks + polling) adiciona complexidade
- [-1] Sem design mockup — UI decisions baseadas em bom senso
- [-1] Upload de arquivos + integração com briefing (como anexar conteúdo de PDFs ao prompt) não especificado

**Para aumentar confiança:**
- Obter mockup/wireframe das telas desejadas
- Definir se arquivos uploadados devem ser anexados ao briefing (extrair texto de PDFs?) ou apenas armazenados como referência
- Definir se haverá mais de um usuário no futuro (impacta modelo de permissões)

---

*PRP generated by dev-kit:10-generate-prp*
*IMPORTANTE: Execute em nova instância do Claude Code (use /clear antes de executar)*
