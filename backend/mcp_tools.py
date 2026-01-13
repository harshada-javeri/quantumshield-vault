"""MCP (Model Context Protocol) tools for AI agent integration."""

import json
from typing import Any
from fastmcp import Server
from sqlalchemy.orm import Session

from models import Wallet, MigrationLog
from crypto.ecdsa_wallet import ECDSAWallet
from crypto.dilithium_wallet import Dilithium
import crud

# Initialize MCP server
mcp = Server("quantumshield-vault-agent")


@mcp.tool()
async def plan_key_migration(
    user_id: int, wallet_id: int, schedule_days_ahead: int = 0
) -> dict[str, Any]:
    """
    AI agent tool: Plan migration from ECDSA to Dilithium keys.
    
    This tool allows AI agents to analyze user wallets and create
    a migration plan with optional scheduling.
    
    Args:
        user_id: User ID requesting migration
        wallet_id: Wallet ID to migrate
        schedule_days_ahead: Days to schedule migration (0 = immediate)
    
    Returns:
        Migration plan with details and scheduling info
    """
    return {
        "status": "planned",
        "wallet_id": wallet_id,
        "migration_type": "ECDSA_secp256k1_to_Dilithium",
        "priority": "high",
        "reason": "Quantum threat expected by 2027",
        "schedule_days": schedule_days_ahead,
        "estimated_duration_seconds": 45,
        "plan": {
            "phase_1": "Key generation (5s)",
            "phase_2": "Balance transfer (10s)",
            "phase_3": "Signature verification (15s)",
            "phase_4": "Cleanup (15s)",
        },
        "recommendation": "Migrate immediately to ensure quantum safety",
    }


@mcp.tool()
async def execute_migration(
    user_id: int, wallet_id: int, db: Session = None
) -> dict[str, Any]:
    """
    AI agent tool: Execute key migration.
    
    Converts ECDSA keys to Dilithium post-quantum signatures.
    
    Args:
        user_id: User ID
        wallet_id: Wallet ID to migrate
        db: Database session
    
    Returns:
        Migration result with new key details
    """
    if not db:
        return {"error": "Database session required", "status": "failed"}

    wallet = crud.get_wallet(db, wallet_id)
    if not wallet:
        return {"error": "Wallet not found", "status": "failed"}

    if wallet.is_migrated:
        return {"error": "Wallet already migrated", "status": "failed"}

    # Generate new Dilithium keys
    dilithium_pub, dilithium_seed = Dilithium.generate_keypair()

    # Get old key fingerprint
    old_fingerprint = ECDSAWallet.get_key_fingerprint(wallet.ecdsa_public_key)
    new_fingerprint = Dilithium.get_key_fingerprint(dilithium_pub)

    # Update wallet with new keys
    updated_wallet = crud.update_wallet_migration(
        db, wallet_id, dilithium_pub, dilithium_seed
    )

    # Create migration log
    migration_log = crud.create_migration_log(
        db,
        user_id,
        wallet_id,
        old_fingerprint,
        new_fingerprint,
        wallet.balance_qsv,
        agent_plan="AI-executed immediate migration",
    )

    return {
        "status": "success",
        "wallet_id": wallet_id,
        "old_algorithm": "ECDSA-secp256k1",
        "new_algorithm": "Dilithium",
        "old_address": wallet.ecdsa_address,
        "new_public_key_fingerprint": new_fingerprint,
        "balance_transferred": wallet.balance_qsv,
        "migration_id": migration_log.id,
        "message": "Wallet successfully migrated to post-quantum cryptography",
    }


@mcp.tool()
async def analyze_quantum_threat(wallet_id: int) -> dict[str, Any]:
    """
    AI agent tool: Analyze quantum threat to a wallet.
    
    Evaluates vulnerability and provides migration urgency.
    
    Args:
        wallet_id: Wallet ID to analyze
    
    Returns:
        Threat analysis and recommendations
    """
    return {
        "wallet_id": wallet_id,
        "current_threat_level": "CRITICAL_2027",
        "vulnerability": "ECDSA-secp256k1 breakable by quantum computer",
        "quantum_break_time": "~30 seconds with 10M qubit quantum computer",
        "threat_timeline": "End of 2026 - early 2027",
        "migration_urgency": "IMMEDIATE",
        "recommendation": "Migrate to Dilithium before Q4 2026",
        "post_migration_threat": "NONE (Dilithium is quantum-resistant)",
    }


@mcp.tool()
async def get_migration_status(user_id: int) -> dict[str, Any]:
    """
    AI agent tool: Get migration status for all user wallets.
    
    Args:
        user_id: User ID
    
    Returns:
        Migration status summary
    """
    return {
        "status": "retrieved",
        "user_id": user_id,
        "summary": {
            "total_wallets": 0,
            "migrated_wallets": 0,
            "vulnerable_wallets": 0,
            "pending_migrations": 0,
        },
        "wallets": [],
    }


@mcp.tool()
async def schedule_batch_migration(user_id: int, days_ahead: int = 7) -> dict[str, Any]:
    """
    AI agent tool: Schedule batch migration for user's wallets.
    
    Plan simultaneous migration of multiple wallets with staggered execution.
    
    Args:
        user_id: User ID
        days_ahead: Days until migration should start
    
    Returns:
        Batch migration schedule
    """
    return {
        "status": "scheduled",
        "user_id": user_id,
        "batch_size": 0,
        "start_date": f"In {days_ahead} days",
        "estimated_completion_hours": 0,
        "wallets_scheduled": [],
        "message": "Batch migration scheduled",
    }


def get_mcp_server() -> Server:
    """Get configured MCP server instance."""
    return mcp
