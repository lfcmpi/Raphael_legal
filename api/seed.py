"""Seed script to create admin user."""

import os
import sys

from dotenv import load_dotenv

load_dotenv()

from api.database import SessionLocal, engine
from api.db_models import Base, User


def seed_admin() -> None:
    """Create admin user if not exists."""
    email = os.getenv("ADMIN_EMAIL", "raphael@email.com")
    password = os.getenv("ADMIN_PASSWORD", "change-me")
    nome = os.getenv("ADMIN_NOME", "Raphael")

    Base.metadata.create_all(bind=engine)

    from api.auth import hash_password

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"Usuário admin já existe: {email}")
            return

        user = User(
            email=email,
            hashed_password=hash_password(password),
            nome=nome,
            role="admin",
        )
        db.add(user)
        db.commit()
        print(f"Usuário admin criado: {email}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()
