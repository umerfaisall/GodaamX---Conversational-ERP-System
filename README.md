# GodaamX

> Inventory & Logistics ERP System — a modern warehouse management backend with AI-powered data assistant.

![Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.132+-009688.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-336791.svg)
![asyncpg](https://img.shields.io/badge/asyncpg-raw_SQL-purple.svg)
![LangChain](https://img.shields.io/badge/LangChain-AI_Agent-green.svg)
![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70B-orange.svg)
![JWT](https://img.shields.io/badge/Auth-JWT_+_bcrypt-red.svg)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-e92063.svg)

---

## What It Does

GodaamX is a multi-tenant ERP backend for managing warehouses, inventory, suppliers, purchase orders, invoices, shipments, and customers. It features role-based access control (SUPERADMIN / SUPPLIER), real-time dashboard analytics, report generation with CSV export, and an AI chat assistant that lets users query their ERP data using natural language.

---

## Key Features

- **Suppliers, Products, Categories, Warehouses** — full CRUD with soft deletes
- **Inventory Tracking** — per-product, per-warehouse stock with reorder alerts
- **Purchase Orders & Invoices** — status workflows with nested line items
- **Shipment Management** — carrier tracking (DHL, FedEx, UPS, Aramex) with auto-generated tracking numbers
- **Customer Management** — Individual and Business customer types
- **Dashboard Analytics** — role-specific KPI cards and chart data
- **Reports & CSV Export** — summary reports across all entities
- **AI Chat Assistant** — natural-language SQL queries via LangChain + Groq with automatic data scoping
- **Registration Workflow** — supplier self-registration with admin approval and email notifications
- **JWT Auth** — Bearer token authentication with role-based access control

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Runtime | Python 3.12+ |
| Database | PostgreSQL (Neon serverless) |
| DB Driver | asyncpg (raw SQL, no ORM) |
| AI Agent | LangChain |
| LLM | Groq (Llama 3.3 70B) |
| Auth | JWT + bcrypt |
| Validation | Pydantic v2 |
| Package Manager | uv |
| Formatter | Black |

---

## Quick Start

```bash
# Clone & install
git clone https://github.com/umerfaisall/Inventory-and-logistic-ERP-System.git
cd Inventory-and-logistic-ERP-System
uv sync

# Set up environment
cp .env.example .env
# Edit .env with your DATABASE_URL, GROQ_API_KEY, SMTP credentials

# Run database migrations
psql $DATABASE_URL -f Database/database_Code.sql
psql $DATABASE_URL -f Database/chat_conversations.sql

# Start the server
python main.py
```

API docs available at **http://localhost:8000/docs**

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `SECRET_KEY` | No | JWT signing secret (change in production) |
| `GROQ_API_KEY` | No | Required for AI chat feature |
| `SMTP_HOST` / `SMTP_PORT` / `SMTP_USER` / `SMTP_PASSWORD` | No | SMTP config for email notifications |

---

## Project Structure

```
├── main.py                # App entry point, CORS, middleware
├── pyproject.toml         # Dependencies
├── Database/              # SQL schema & migrations
└── app/
    ├── routes/            # API route definitions
    ├── controllers/       # Business logic
    ├── repositories/      # Raw SQL data access
    ├── dto/               # Pydantic request/response models
    ├── langchain_agent/   # AI chat agent (LangChain + Groq)
    └── utils/             # Auth, email, CSV export, tracking numbers
```

---

## Architecture

```
Routes → Controllers → Repositories → PostgreSQL
```

Fully async. No ORM — raw SQL via asyncpg. Soft deletes everywhere. Role-based query injection for data scoping.

---

## API Endpoints

All routes under `/api/v1`:

`/auth` · `/admin` · `/users` · `/suppliers` · `/categories` · `/warehouses` · `/products` · `/inventory` · `/purchase-order` · `/poi` · `/invoice` · `/customers` · `/shipments` · `/dashboard` · `/reports` · `/chat`

---

## License

Not yet specified.