"""Database configuration and session management."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from models import Base

# ============================================================================
# Database Configuration
# ============================================================================

# Use SQLite for development, PostgreSQL for production
DATABASE_ENV = os.getenv("DATABASE_ENV", "development")

if DATABASE_ENV == "production":
    # PostgreSQL connection string
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@db:5432/quantumshield",
    )
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        echo=False,
    )
else:
    # SQLite for development
    DB_PATH = os.getenv("SQLITE_DB_PATH", "./data/quantumshield.db")
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    
    DATABASE_URL = f"sqlite:///{DB_PATH}"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Get database session dependency for FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables and create seed data."""
    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Seed initial data
    db = SessionLocal()
    try:
        from crud import get_user_by_username, create_user, create_wallet
        from schemas import UserCreate, WalletCreate
        from crypto.ecdsa_wallet import ECDSAWallet

        # Create demo user if not exists
        demo_user = get_user_by_username(db, "demo_user")
        if not demo_user:
            user_create = UserCreate(username="demo_user", email="demo@quantumshield.local")
            demo_user = create_user(db, user_create)

            # Create demo wallet
            priv, pub, addr = ECDSAWallet.generate_keypair()
            wallet_create = WalletCreate(name="Demo ECDSA Wallet")
            create_wallet(db, demo_user.id, wallet_create, priv, pub, addr)

            print(f"✓ Created demo user: {demo_user.username}")
            print(f"✓ Created demo wallet: {addr}")

    except Exception as e:
        print(f"⚠ Could not seed data: {e}")
    finally:
        db.close()
