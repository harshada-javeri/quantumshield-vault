"""CRUD operations for database models."""

from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models import User, Wallet, MigrationLog, AttackLog
from schemas import UserCreate, WalletCreate


# ============================================================================
# User CRUD
# ============================================================================


def create_user(db: Session, user: UserCreate) -> User:
    """Create new user."""
    db_user = User(username=user.username, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username."""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def list_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """List all users with pagination."""
    return db.query(User).offset(skip).limit(limit).all()


# ============================================================================
# Wallet CRUD
# ============================================================================


def create_wallet(
    db: Session,
    user_id: int,
    wallet: WalletCreate,
    ecdsa_private_key: str,
    ecdsa_public_key: str,
    ecdsa_address: str,
) -> Wallet:
    """Create new ECDSA wallet for user."""
    db_wallet = Wallet(
        user_id=user_id,
        name=wallet.name,
        ecdsa_private_key=ecdsa_private_key,
        ecdsa_public_key=ecdsa_public_key,
        ecdsa_address=ecdsa_address,
        balance_qsv=1.0,  # Initial balance
    )
    db.add(db_wallet)
    db.commit()
    db.refresh(db_wallet)
    return db_wallet


def get_wallet(db: Session, wallet_id: int) -> Optional[Wallet]:
    """Get wallet by ID."""
    return db.query(Wallet).filter(Wallet.id == wallet_id).first()


def get_wallet_by_address(db: Session, address: str) -> Optional[Wallet]:
    """Get wallet by ECDSA address."""
    return db.query(Wallet).filter(Wallet.ecdsa_address == address).first()


def get_user_wallets(db: Session, user_id: int) -> List[Wallet]:
    """Get all wallets for a user."""
    return db.query(Wallet).filter(Wallet.user_id == user_id).all()


def update_wallet_migration(
    db: Session,
    wallet_id: int,
    dilithium_public_key: str,
    dilithium_seed: str,
) -> Wallet:
    """Update wallet with post-quantum keys after migration."""
    wallet = get_wallet(db, wallet_id)
    if wallet:
        wallet.dilithium_public_key = dilithium_public_key
        wallet.dilithium_seed = dilithium_seed
        wallet.is_migrated = True
        wallet.migrated_at = datetime.utcnow()
        wallet.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(wallet)
    return wallet


def list_wallets(db: Session, skip: int = 0, limit: int = 100) -> List[Wallet]:
    """List all wallets with pagination."""
    return db.query(Wallet).offset(skip).limit(limit).all()


def get_migrated_wallets(db: Session) -> List[Wallet]:
    """Get all migrated wallets."""
    return db.query(Wallet).filter(Wallet.is_migrated == True).all()


def get_vulnerable_wallets(db: Session) -> List[Wallet]:
    """Get all non-migrated (vulnerable) wallets."""
    return db.query(Wallet).filter(Wallet.is_migrated == False).all()


# ============================================================================
# Migration Log CRUD
# ============================================================================


def create_migration_log(
    db: Session,
    user_id: int,
    wallet_id: int,
    old_key_hash: str,
    new_key_hash: str,
    transferred_balance: float,
    agent_plan: Optional[str] = None,
) -> MigrationLog:
    """Create migration log entry."""
    migration_log = MigrationLog(
        user_id=user_id,
        wallet_id=wallet_id,
        old_key_hash=old_key_hash,
        new_key_hash=new_key_hash,
        transferred_balance=transferred_balance,
        status="completed",
        agent_plan=agent_plan,
    )
    db.add(migration_log)
    db.commit()
    db.refresh(migration_log)
    return migration_log


def get_migration_logs_for_user(db: Session, user_id: int) -> List[MigrationLog]:
    """Get all migration logs for a user."""
    return (
        db.query(MigrationLog)
        .filter(MigrationLog.user_id == user_id)
        .order_by(desc(MigrationLog.created_at))
        .all()
    )


def get_migration_logs_for_wallet(db: Session, wallet_id: int) -> List[MigrationLog]:
    """Get all migration logs for a wallet."""
    return (
        db.query(MigrationLog)
        .filter(MigrationLog.wallet_id == wallet_id)
        .order_by(desc(MigrationLog.created_at))
        .all()
    )


def get_scheduled_migrations(db: Session) -> List[MigrationLog]:
    """Get migrations scheduled for future execution."""
    now = datetime.utcnow()
    return (
        db.query(MigrationLog)
        .filter(MigrationLog.scheduled_for > now, MigrationLog.status == "scheduled")
        .order_by(MigrationLog.scheduled_for)
        .all()
    )


# ============================================================================
# Attack Log CRUD
# ============================================================================


def create_attack_log(
    db: Session,
    wallet_id: int,
    vulnerable: bool,
    signature_broken: bool,
    estimated_time_seconds: float = 30.0,
) -> AttackLog:
    """Create attack simulation log."""
    attack_log = AttackLog(
        wallet_id=wallet_id,
        attack_type="shor_algorithm",
        vulnerable=vulnerable,
        signature_broken=signature_broken,
        estimated_time_seconds=estimated_time_seconds,
    )
    db.add(attack_log)
    db.commit()
    db.refresh(attack_log)
    return attack_log


def get_attack_logs_for_wallet(db: Session, wallet_id: int) -> List[AttackLog]:
    """Get all attack simulation logs for a wallet."""
    return (
        db.query(AttackLog)
        .filter(AttackLog.wallet_id == wallet_id)
        .order_by(desc(AttackLog.created_at))
        .all()
    )


def get_recent_attacks(db: Session, hours: int = 24) -> List[AttackLog]:
    """Get attacks from the last N hours."""
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    return db.query(AttackLog).filter(AttackLog.created_at >= cutoff).all()
