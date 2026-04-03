# Fele Backend

FastAPI backend for the Fele SaaS inventory system.

## Database

- Local PostgreSQL
- Shared platform tables in `public`
- One schema per company tenant

## Default Super Admin

- Email: `admin@fele.local`
- Password: `Admin@123456`

## Run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
copy .env.example .env
uvicorn app.main:app --reload
```

Default local database URL:

```bash
postgresql+psycopg://postgres:aa123456@127.0.0.1:5432/fele_erp
```

## Provision A Tenant

```bash
python scripts/provision_tenant.py --company "Acme Trading" --owner-email owner@acme.local --owner-password "Owner@123456" --owner-name "Acme Owner"
```
