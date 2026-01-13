"""Main FastAPI application with routes and MCP integration."""

import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database import get_db, init_db
from models import Wallet, User
from schemas import (
    UserCreate,
    UserResponse,
    WalletCreate,
    WalletResponse,
    MigrationResponse,
    MigrationLogResponse,
    AttackSimulationResponse,
    DashboardResponse,
    CryptoAuditResponse,
    HealthCheckResponse,
)
from crypto.ecdsa_wallet import ECDSAWallet
from crypto.dilithium_wallet import Dilithium
import crud


# ============================================================================
# Lifespan Management
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    print("🚀 Initializing QuantumShield Vault...")
    init_db()
    print("✓ Database initialized")
    yield
    print("🛑 Shutting down QuantumShield Vault")


# ============================================================================
# FastAPI Application
# ============================================================================


app = FastAPI(
    title="QuantumShield Vault API",
    description="Post-quantum cryptographic wallet protecting against quantum attacks",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Health & Status Endpoints
# ============================================================================


@app.get("/health", response_model=HealthCheckResponse)
async def health_check(db: Session = Depends(get_db)):
    """Check API and database health."""
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"

    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        database=db_status,
        mcp_server="enabled",
        version="1.0.0",
    )


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "QuantumShield Vault API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "description": "Post-quantum cryptographic wallet API",
    }


# ============================================================================
# User Management Endpoints
# ============================================================================


@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create new user."""
    # Check if user exists
    existing = crud.get_user_by_username(db, user.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    existing_email = crud.get_user_by_email(db, user.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    db_user = crud.create_user(db, user)
    return db_user


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID."""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


# ============================================================================
# Wallet Management Endpoints
# ============================================================================


@app.post("/wallet", response_model=WalletResponse, status_code=status.HTTP_201_CREATED)
async def create_wallet(
    user_id: int,
    wallet: WalletCreate,
    db: Session = Depends(get_db),
):
    """Create new ECDSA wallet for user."""
    # Verify user exists
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Generate ECDSA keypair
    private_key, public_key, address = ECDSAWallet.generate_keypair()

    # Create wallet in database
    db_wallet = crud.create_wallet(
        db, user_id, wallet, private_key, public_key, address
    )

    return db_wallet


@app.get("/wallet/{wallet_id}", response_model=WalletResponse)
async def get_wallet(wallet_id: int, db: Session = Depends(get_db)):
    """Get wallet details."""
    wallet = crud.get_wallet(db, wallet_id)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )
    return wallet


@app.get("/user/{user_id}/wallets", response_model=List[WalletResponse])
async def get_user_wallets(user_id: int, db: Session = Depends(get_db)):
    """Get all wallets for a user."""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    wallets = crud.get_user_wallets(db, user_id)
    return wallets


@app.get("/wallet/{wallet_id}/crypto-audit", response_model=CryptoAuditResponse)
async def get_crypto_audit(wallet_id: int, db: Session = Depends(get_db)):
    """Get cryptographic audit for a wallet."""
    wallet = crud.get_wallet(db, wallet_id)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )

    current_algo = "Dilithium" if wallet.is_migrated else "ECDSA-secp256k1"
    current_status = (
        "Quantum-resistant" if wallet.is_migrated else "Vulnerable to quantum attacks"
    )

    return CryptoAuditResponse(
        wallet_id=wallet_id,
        current_algorithm=current_algo,
        current_algorithm_status=current_status,
        post_quantum_algorithm="Dilithium (NIST PQC standard)",
        signature_verification={
            "ecdsa_signature": ECDSAWallet.verify_signature(
                wallet.ecdsa_public_key,
                "test_message",
                ECDSAWallet.sign_message(wallet.ecdsa_private_key, "test_message"),
            ),
            "dilithium_signature": (
                Dilithium.verify(
                    "test_message",
                    Dilithium.sign("test_message", wallet.dilithium_seed),
                    wallet.dilithium_public_key,
                )
                if wallet.is_migrated
                else None
            ),
        },
        quantum_threat_status="NONE" if wallet.is_migrated else "CRITICAL (2027)",
        migration_recommendation=(
            "Already migrated ✓" if wallet.is_migrated else "MIGRATE IMMEDIATELY"
        ),
    )


# ============================================================================
# Migration Endpoints
# ============================================================================


@app.post("/migrate/{wallet_id}", response_model=MigrationResponse)
async def migrate_wallet(wallet_id: int, db: Session = Depends(get_db)):
    """Migrate wallet from ECDSA to Dilithium post-quantum signatures."""
    wallet = crud.get_wallet(db, wallet_id)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )

    if wallet.is_migrated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wallet already migrated",
        )

    # Generate Dilithium keys
    dilithium_pub, dilithium_seed = Dilithium.generate_keypair()

    # Get key fingerprints for migration log
    old_fingerprint = ECDSAWallet.get_key_fingerprint(wallet.ecdsa_public_key)
    new_fingerprint = Dilithium.get_key_fingerprint(dilithium_pub)

    # Update wallet
    updated_wallet = crud.update_wallet_migration(
        db, wallet_id, dilithium_pub, dilithium_seed
    )

    # Create migration log
    migration_log = crud.create_migration_log(
        db,
        wallet.user_id,
        wallet_id,
        old_fingerprint,
        new_fingerprint,
        wallet.balance_qsv,
        agent_plan="User-initiated migration via POST /migrate",
    )

    return MigrationResponse(
        success=True,
        wallet_id=wallet_id,
        new_keys={
            "algorithm": "Dilithium",
            "public_key_fingerprint": new_fingerprint,
            "quantum_resistant": True,
        },
        old_balance_transferred=wallet.balance_qsv,
        migration_id=migration_log.id,
    )


@app.get("/user/{user_id}/migrations", response_model=List[MigrationLogResponse])
async def get_user_migrations(user_id: int, db: Session = Depends(get_db)):
    """Get migration history for a user."""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    migrations = crud.get_migration_logs_for_user(db, user_id)
    return migrations


# ============================================================================
# Attack Simulation Endpoints
# ============================================================================


@app.post("/simulate-attack/{wallet_id}", response_model=AttackSimulationResponse)
async def simulate_quantum_attack(wallet_id: int, db: Session = Depends(get_db)):
    """Simulate Shor's algorithm quantum attack on ECDSA keys."""
    wallet = crud.get_wallet(db, wallet_id)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )

    # Determine vulnerability
    is_vulnerable = not wallet.is_migrated
    signature_broken = is_vulnerable  # If vulnerable, attack breaks signature

    # Log attack simulation
    attack_log = crud.create_attack_log(
        db, wallet_id, is_vulnerable, signature_broken, estimated_time_seconds=30.0
    )

    message = ""
    recommendation = ""

    if is_vulnerable:
        message = (
            "⚠️  VULNERABLE: Shor's algorithm broke your ECDSA keys in ~30 seconds! "
            "Attacker gained access to your funds."
        )
        recommendation = "URGENT: Migrate to Dilithium (post-quantum) immediately"
    else:
        message = (
            "✓ PROTECTED: Your Dilithium keys resisted the attack. "
            "No known quantum algorithm can break them."
        )
        recommendation = "Your keys are quantum-safe. Continue monitoring for updates."

    return AttackSimulationResponse(
        wallet_id=wallet_id,
        attack_successful=signature_broken,
        quantum_vulnerable=is_vulnerable,
        signature_broken=signature_broken,
        estimated_break_time_seconds=30.0 if is_vulnerable else float("inf"),
        message=message,
        recommendation=recommendation,
    )


# ============================================================================
# Dashboard Endpoints
# ============================================================================


@app.get("/user/{user_id}/dashboard", response_model=DashboardResponse)
async def get_dashboard(user_id: int, db: Session = Depends(get_db)):
    """Get comprehensive dashboard for user."""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    wallets = crud.get_user_wallets(db, user_id)
    migrations = crud.get_migration_logs_for_user(db, user_id)

    total_balance = sum(w.balance_qsv for w in wallets)
    migrated_count = sum(1 for w in wallets if w.is_migrated)
    vulnerable_count = sum(1 for w in wallets if not w.is_migrated)

    return DashboardResponse(
        user=user,
        wallets=wallets,
        migration_logs=migrations,
        total_balance_qsv=total_balance,
        migrated_count=migrated_count,
        vulnerable_count=vulnerable_count,
    )


# ============================================================================
# Statistics Endpoints
# ============================================================================


@app.get("/stats/migration")
async def get_migration_stats(db: Session = Depends(get_db)):
    """Get global migration statistics."""
    all_wallets = crud.list_wallets(db, skip=0, limit=10000)
    migrated = crud.get_migrated_wallets(db)
    vulnerable = crud.get_vulnerable_wallets(db)

    return {
        "total_wallets": len(all_wallets),
        "migrated_wallets": len(migrated),
        "vulnerable_wallets": len(vulnerable),
        "migration_percentage": (
            len(migrated) / len(all_wallets) * 100 if all_wallets else 0
        ),
    }


@app.get("/stats/attacks")
async def get_attack_stats(db: Session = Depends(get_db)):
    """Get attack simulation statistics."""
    recent_attacks = crud.get_recent_attacks(db, hours=24)
    successful = sum(1 for a in recent_attacks if a.signature_broken)

    return {
        "total_simulations": len(recent_attacks),
        "successful_attacks": successful,
        "vulnerable_wallets_attacked": len(
            set(a.wallet_id for a in recent_attacks if a.vulnerable)
        ),
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("ENV", "development") == "development",
    )
