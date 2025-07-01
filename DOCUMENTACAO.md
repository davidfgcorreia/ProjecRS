# Documentação Completa do Projeto Full-Stack

## Visão Geral

Este projeto é uma aplicação full-stack composta por:
- **Backend:** FastAPI + SQLAlchemy (PostgreSQL em produção, SQLite para desenvolvimento local)
- **Frontend:** Vue.js 3 (Vite)
- **Containerização:** Docker e Docker Compose
- **Testes:** Pytest (backend), Vitest/Cypress (frontend)
- **Funcionalidades:** CRUD de usuários, upload de arquivos PDF, autenticação, geração de relatórios/resultados, sistema de permissões (usuário/admin), e testes automatizados.

> **Atenção:** A integração entre frontend e backend ainda está em ajuste. Algumas funcionalidades podem não estar totalmente conectadas.

---

## Estrutura de Pastas

```
projeto/
│
├── app/                # Backend FastAPI
│   ├── api/            # Rotas (user, upload, result)
│   ├── db/             # Configuração e acesso ao banco
│   ├── models/         # Modelos SQLAlchemy
│   ├── schemas/        # Schemas Pydantic
│   ├── services/       # Serviços (ex: file_storage)
│   └── main.py         # Inicialização do FastAPI
│
├── frontend/           # Frontend Vue.js
│   ├── src/            # Código-fonte Vue
│   └── ...             # Configurações e assets
│
├── tests/              # Testes automatizados do backend
│
├── requirements.txt    # Dependências Python
├── Dockerfile          # Dockerfile do backend
├── docker-compose.yml  # Orquestração dos serviços
└── README.md           # Este arquivo
```

---

## Como Executar

### 1. Local (Desenvolvimento)

**Backend:**
```bash
pip install -r requirements.txt
python -m app.init_db  # Cria o banco e admin se necessário
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### 2. Com Docker Compose

```bash
docker-compose up --build
```
- Backend: http://localhost:8000
- Frontend: http://localhost:5173

---

## Variáveis de Ambiente

- `DATABASE_URL`: URL do banco (ex: `postgresql://user:password@db:5432/appdb` ou `sqlite:///./test.db`)
- Outras variáveis podem ser adicionadas conforme necessidade.

---

## Endpoints Principais (Backend)

- `POST /users/` — Cria usuário (campos: name, email, password)
- `GET /users/` — Lista usuários
- `GET /users/{id}` — Detalhe do usuário
- `PUT /users/{id}` — Atualiza usuário
- `DELETE /users/{id}` — Remove usuário
- `POST /upload/pdf/` — Upload de PDF (autenticado)
- `GET /result/{id}` — Busca resultado/relatório

> Veja a documentação interativa em `/docs` (Swagger UI) ao rodar o backend.

---

## Autenticação e Segurança

- Senhas são armazenadas com hash SHA-256.
- Campo `role` diferencia usuários comuns e administradores.
- Usuário admin padrão é criado automaticamente (email: adm@admin.com, senha: adm).

---

## Testes

- **Backend:**  
  Execute `pytest` na raiz do projeto. O banco de testes é limpo após cada teste.
- **Frontend:**  
  Use `npm run test` (Vitest) ou `npm run cy:open` (Cypress) na pasta `frontend`.

---

## Observações sobre Integração

- A comunicação entre frontend e backend está em desenvolvimento.  
- Certifique-se de que as URLs e payloads dos requests estejam alinhados entre Vue.js e FastAPI.
- Se encontrar erros 422 ou CORS, revise os nomes dos campos e configurações de CORS no backend.

---

## Docker

- O backend e frontend são construídos e executados em containers separados.
- O banco PostgreSQL é persistido em volume Docker.
- Para resetar o banco local SQLite, basta remover o arquivo `test.db`.

---

## Manutenção e Escalabilidade

- Estrutura modular para fácil expansão.
- Pronto para deploy em produção com Docker.
- Suporte a migrações futuras via Alembic (pode ser ativado conforme necessidade).

---

Se precisar de exemplos de requests, instruções para deploy em nuvem, ou detalhes de integração, só pedir!
