from __future__ import annotations

import argparse

from app.core.bootstrap import provision_tenant
from app.core.database import SessionLocal, create_platform_tables
from app.services.auth_service import generate_company_id


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a company tenant and owner account.")
    parser.add_argument("--company", required=True, help="Company name")
    parser.add_argument("--owner-email", required=True, help="Owner email")
    parser.add_argument("--owner-password", required=True, help="Owner password")
    parser.add_argument("--owner-name", required=True, help="Owner full name")
    parser.add_argument("--slug", required=False, help="Optional company slug")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    create_platform_tables()
    with SessionLocal.begin() as session:
        company_id = generate_company_id(session)
        tenant = provision_tenant(
            session,
            company_name=args.company,
            company_id=company_id,
            owner_email=args.owner_email,
            owner_password=args.owner_password,
            owner_full_name=args.owner_name,
            slug=args.slug,
        )
        print(f"tenant={tenant.slug}")
        print(f"company_id={tenant.company_id}")
        print(f"schema={tenant.schema_name}")
        print(f"owner={args.owner_email}")


if __name__ == "__main__":
    main()
