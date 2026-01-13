"""SQLAlchemy ORM models for QuantumShield Vault."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """User model storing wallet owner information."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    wallets = relationship("Wallet", back_populates="owner", cascade="all, delete-orphan")
    migration_logs = relationship(
        "MigrationLog", back_populates="user", cascade="all, delete-orphan"
    )


class Wallet(Base):
    """Wallet model storing ECDSA and Dilithium keypairs."""

    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)

    # ECDSA Keys (secp256k1)
    ecdsa_private_key = Column(Text, nullable=False)
    ecdsa_public_key = Column(Text, nullable=False)
    ecdsa_address = Column(String(255), unique=True, nullable=False, index=True)

    # Dilithium Keys (Post-quantum)
    dilithium_public_key = Column(Text, nullable=True)
    dilithium_seed = Column(Text, nullable=True)

    # Balance and Migration Status
    balance_qsv = Column(Float, default=1.0, nullable=False)
    migrated_at = Column(DateTime, nullable=True)
    is_migrated = Column(Boolean, default=False, index=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="wallets")
    attack_logs = relationship(
        "AttackLog", back_populates="wallet", cascade="all, delete-orphan"
    )


class MigrationLog(Base):
    """Track wallet migration events from ECDSA to Dilithium."""

    __tablename__ = "migration_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    wallet_id = Column(Integer, nullable=False, index=True)

    # Migration Details
    old_key_hash = Column(String(255), nullable=False)
    new_key_hash = Column(String(255), nullable=False)
    transferred_balance = Column(Float, nullable=False)

    # Status
    status = Column(String(50), default="completed")
    scheduled_for = Column(DateTime, nullable=True)

    # AI Agent Info
    agent_plan = Column(Text, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="migration_logs")


class AttackLog(Base):
    """Track quantum attack simulation events."""

    __tablename__ = "attack_logs"

    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False, index=True)

    # Attack Details
    attack_type = Column(String(50), default="shor_algorithm")
    vulnerable = Column(Boolean, nullable=False)
    signature_broken = Column(Boolean, nullable=False)
    estimated_time_seconds = Column(Float, default=30.0)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    wallet = relationship("Wallet", back_populates="attack_logs")
