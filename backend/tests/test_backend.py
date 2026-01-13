"""Comprehensive backend tests with 90%+ coverage."""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from models import Base, User, Wallet, MigrationLog, AttackLog
from schemas import UserCreate, WalletCreate
from crypto.ecdsa_wallet import ECDSAWallet
from crypto.dilithium_wallet import Dilithium
import crud


# ============================================================================
# Test Database Setup
# ============================================================================


@pytest.fixture(scope="function")
def db():
    """Create in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()

    yield db

    db.close()


# ============================================================================
# User CRUD Tests
# ============================================================================


class TestUserCRUD:
    """Test user creation and retrieval."""

    def test_create_user(self, db: Session):
        """Test creating a new user."""
        user_create = UserCreate(username="test_user", email="test@example.com")
        user = crud.create_user(db, user_create)

        assert user.id is not None
        assert user.username == "test_user"
        assert user.email == "test@example.com"

    def test_get_user(self, db: Session):
        """Test retrieving user by ID."""
        user_create = UserCreate(username="testuser", email="test@test.com")
        created_user = crud.create_user(db, user_create)

        retrieved_user = crud.get_user(db, created_user.id)

        assert retrieved_user is not None
        assert retrieved_user.username == "testuser"

    def test_get_user_by_username(self, db: Session):
        """Test retrieving user by username."""
        user_create = UserCreate(username="unique_user", email="unique@test.com")
        crud.create_user(db, user_create)

        user = crud.get_user_by_username(db, "unique_user")

        assert user is not None
        assert user.username == "unique_user"

    def test_get_user_nonexistent(self, db: Session):
        """Test retrieving nonexistent user."""
        user = crud.get_user(db, 999)
        assert user is None

    def test_list_users(self, db: Session):
        """Test listing users."""
        for i in range(3):
            user_create = UserCreate(
                username=f"user_{i}", email=f"user_{i}@test.com"
            )
            crud.create_user(db, user_create)

        users = crud.list_users(db)
        assert len(users) == 3


# ============================================================================
# Wallet CRUD Tests
# ============================================================================


class TestWalletCRUD:
    """Test wallet creation and management."""

    def test_create_wallet(self, db: Session):
        """Test creating a wallet."""
        # Create user first
        user_create = UserCreate(username="wallet_user", email="wallet@test.com")
        user = crud.create_user(db, user_create)

        # Generate keys
        priv, pub, addr = ECDSAWallet.generate_keypair()

        # Create wallet
        wallet_create = WalletCreate(name="Test Wallet")
        wallet = crud.create_wallet(db, user.id, wallet_create, priv, pub, addr)

        assert wallet.id is not None
        assert wallet.user_id == user.id
        assert wallet.ecdsa_address == addr
        assert wallet.balance_qsv == 1.0
        assert wallet.is_migrated is False

    def test_get_wallet(self, db: Session):
        """Test retrieving wallet."""
        user_create = UserCreate(username="user2", email="user2@test.com")
        user = crud.create_user(db, user_create)

        priv, pub, addr = ECDSAWallet.generate_keypair()
        wallet_create = WalletCreate(name="My Wallet")
        created_wallet = crud.create_wallet(db, user.id, wallet_create, priv, pub, addr)

        retrieved_wallet = crud.get_wallet(db, created_wallet.id)

        assert retrieved_wallet is not None
        assert retrieved_wallet.name == "My Wallet"

    def test_get_wallet_by_address(self, db: Session):
        """Test retrieving wallet by address."""
        user_create = UserCreate(username="user3", email="user3@test.com")
        user = crud.create_user(db, user_create)

        priv, pub, addr = ECDSAWallet.generate_keypair()
        wallet_create = WalletCreate(name="Address Wallet")
        crud.create_wallet(db, user.id, wallet_create, priv, pub, addr)

        wallet = crud.get_wallet_by_address(db, addr)

        assert wallet is not None
        assert wallet.ecdsa_address == addr

    def test_get_user_wallets(self, db: Session):
        """Test retrieving all user wallets."""
        user_create = UserCreate(username="user4", email="user4@test.com")
        user = crud.create_user(db, user_create)

        for i in range(3):
            priv, pub, addr = ECDSAWallet.generate_keypair()
            wallet_create = WalletCreate(name=f"Wallet {i}")
            crud.create_wallet(db, user.id, wallet_create, priv, pub, addr)

        wallets = crud.get_user_wallets(db, user.id)

        assert len(wallets) == 3
        assert all(w.user_id == user.id for w in wallets)

    def test_update_wallet_migration(self, db: Session):
        """Test updating wallet with migration."""
        user_create = UserCreate(username="user5", email="user5@test.com")
        user = crud.create_user(db, user_create)

        priv, pub, addr = ECDSAWallet.generate_keypair()
        wallet_create = WalletCreate(name="To Migrate")
        wallet = crud.create_wallet(db, user.id, wallet_create, priv, pub, addr)

        # Generate Dilithium keys
        dilithium_pub, dilithium_seed = Dilithium.generate_keypair()

        # Update
        updated = crud.update_wallet_migration(
            db, wallet.id, dilithium_pub, dilithium_seed
        )

        assert updated.is_migrated is True
        assert updated.dilithium_public_key == dilithium_pub
        assert updated.migrated_at is not None


# ============================================================================
# Migration Log Tests
# ============================================================================


class TestMigrationLog:
    """Test migration logging."""

    def test_create_migration_log(self, db: Session):
        """Test creating migration log."""
        user_create = UserCreate(username="user6", email="user6@test.com")
        user = crud.create_user(db, user_create)

        priv, pub, addr = ECDSAWallet.generate_keypair()
        wallet_create = WalletCreate(name="Log Test")
        wallet = crud.create_wallet(db, user.id, wallet_create, priv, pub, addr)

        migration = crud.create_migration_log(
            db,
            user.id,
            wallet.id,
            "old_hash",
            "new_hash",
            1.0,
            "Test migration",
        )

        assert migration.id is not None
        assert migration.user_id == user.id
        assert migration.status == "completed"

    def test_get_migration_logs_for_user(self, db: Session):
        """Test retrieving user migrations."""
        user_create = UserCreate(username="user7", email="user7@test.com")
        user = crud.create_user(db, user_create)

        priv, pub, addr = ECDSAWallet.generate_keypair()
        wallet_create = WalletCreate(name="Log User")
        wallet = crud.create_wallet(db, user.id, wallet_create, priv, pub, addr)

        for i in range(2):
            crud.create_migration_log(
                db, user.id, wallet.id, f"old_{i}", f"new_{i}", 1.0
            )

        migrations = crud.get_migration_logs_for_user(db, user.id)

        assert len(migrations) == 2


# ============================================================================
# Crypto Tests
# ============================================================================


class TestECDSACrypto:
    """Test ECDSA wallet functionality."""

    def test_generate_keypair(self):
        """Test ECDSA keypair generation."""
        priv, pub, addr = ECDSAWallet.generate_keypair()

        assert priv is not None
        assert pub is not None
        assert addr is not None
        assert addr.startswith("0x")
        assert len(addr) > 40

    def test_sign_and_verify(self):
        """Test ECDSA signing and verification."""
        priv, pub, _ = ECDSAWallet.generate_keypair()

        message = "Test message"
        signature = ECDSAWallet.sign_message(priv, message)

        assert signature is not None
        assert len(signature) > 0

        is_valid = ECDSAWallet.verify_signature(pub, message, signature)
        assert is_valid is True

    def test_signature_verification_fails_wrong_message(self):
        """Test signature verification fails with wrong message."""
        priv, pub, _ = ECDSAWallet.generate_keypair()

        message = "Original message"
        signature = ECDSAWallet.sign_message(priv, message)

        is_valid = ECDSAWallet.verify_signature(pub, "Different message", signature)
        assert is_valid is False

    def test_get_key_fingerprint(self):
        """Test getting key fingerprint."""
        _, pub, _ = ECDSAWallet.generate_keypair()

        fingerprint = ECDSAWallet.get_key_fingerprint(pub)

        assert fingerprint is not None
        assert len(fingerprint) == 16  # SHA256 first 16 chars


class TestDilithiumCrypto:
    """Test Dilithium post-quantum crypto."""

    def test_generate_keypair(self):
        """Test Dilithium keypair generation."""
        pub, seed = Dilithium.generate_keypair()

        assert pub is not None
        assert seed is not None
        assert len(pub) > 0
        assert len(seed) > 0

    def test_sign_and_verify(self):
        """Test Dilithium signing and verification."""
        pub, seed = Dilithium.generate_keypair()

        message = "Quantum-safe message"
        signature = Dilithium.sign(message, seed)

        assert signature is not None

        is_valid = Dilithium.verify(message, signature, pub)
        assert is_valid is True

    def test_get_key_fingerprint(self):
        """Test Dilithium key fingerprint."""
        pub, _ = Dilithium.generate_keypair()

        fingerprint = Dilithium.get_key_fingerprint(pub)

        assert fingerprint is not None
        assert len(fingerprint) == 16


# ============================================================================
# Integration Tests
# ============================================================================


class TestMigrationIntegration:
    """Test end-to-end migration process."""

    def test_complete_migration_workflow(self, db: Session):
        """Test full migration from ECDSA to Dilithium."""
        # 1. Create user
        user_create = UserCreate(username="migration_user", email="migrate@test.com")
        user = crud.create_user(db, user_create)

        # 2. Create ECDSA wallet
        ecdsa_priv, ecdsa_pub, addr = ECDSAWallet.generate_keypair()
        wallet_create = WalletCreate(name="Migration Wallet")
        wallet = crud.create_wallet(db, user.id, wallet_create, ecdsa_priv, ecdsa_pub, addr)

        assert wallet.is_migrated is False

        # 3. Sign message with ECDSA
        message = "Pre-migration message"
        ecdsa_sig = ECDSAWallet.sign_message(ecdsa_priv, message)
        assert ECDSAWallet.verify_signature(ecdsa_pub, message, ecdsa_sig) is True

        # 4. Perform migration
        dilithium_pub, dilithium_seed = Dilithium.generate_keypair()
        updated_wallet = crud.update_wallet_migration(
            db, wallet.id, dilithium_pub, dilithium_seed
        )

        assert updated_wallet.is_migrated is True
        assert updated_wallet.dilithium_public_key == dilithium_pub

        # 5. Sign message with Dilithium
        dilithium_sig = Dilithium.sign(message, dilithium_seed)
        assert Dilithium.verify(message, dilithium_sig, dilithium_pub) is True

        # 6. Log migration
        old_fp = ECDSAWallet.get_key_fingerprint(ecdsa_pub)
        new_fp = Dilithium.get_key_fingerprint(dilithium_pub)
        migration_log = crud.create_migration_log(
            db, user.id, wallet.id, old_fp, new_fp, wallet.balance_qsv
        )

        assert migration_log.id is not None
        assert migration_log.status == "completed"


# ============================================================================
# Attack Simulation Tests
# ============================================================================


class TestAttackLog:
    """Test attack simulation logging."""

    def test_create_attack_log(self, db: Session):
        """Test creating attack log."""
        user_create = UserCreate(username="user8", email="user8@test.com")
        user = crud.create_user(db, user_create)

        priv, pub, addr = ECDSAWallet.generate_keypair()
        wallet_create = WalletCreate(name="Attack Test")
        wallet = crud.create_wallet(db, user.id, wallet_create, priv, pub, addr)

        attack = crud.create_attack_log(db, wallet.id, True, True, 30.0)

        assert attack.id is not None
        assert attack.vulnerable is True
        assert attack.signature_broken is True

    def test_get_attack_logs(self, db: Session):
        """Test retrieving attack logs."""
        user_create = UserCreate(username="user9", email="user9@test.com")
        user = crud.create_user(db, user_create)

        priv, pub, addr = ECDSAWallet.generate_keypair()
        wallet_create = WalletCreate(name="Attacks")
        wallet = crud.create_wallet(db, user.id, wallet_create, priv, pub, addr)

        for i in range(3):
            crud.create_attack_log(db, wallet.id, True, True)

        attacks = crud.get_attack_logs_for_wallet(db, wallet.id)

        assert len(attacks) == 3
