"""Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# ============================================================================
# User Schemas
# ============================================================================


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=255)
    email: EmailStr


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Wallet Schemas
# ============================================================================


class WalletBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class WalletCreate(WalletBase):
    pass


class WalletResponse(WalletBase):
    id: int
    user_id: int
    ecdsa_address: str
    ecdsa_public_key: str
    balance_qsv: float
    is_migrated: bool
    dilithium_public_key: Optional[str]
    migrated_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WalletDetailResponse(WalletResponse):
    """Full wallet details including migration history."""

    pass


# ============================================================================
# Migration Schemas
# ============================================================================


class MigrationLogBase(BaseModel):
    transferred_balance: float


class MigrationLogResponse(MigrationLogBase):
    id: int
    user_id: int
    wallet_id: int
    old_key_hash: str
    new_key_hash: str
    status: str
    scheduled_for: Optional[datetime]
    agent_plan: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MigrationPlanResponse(BaseModel):
    """Response for AI-planned migration."""

    wallet_id: int
    old_ecdsa_address: str
    new_dilithium_public_key: str
    transferred_balance: float
    migration_id: int
    plan_details: str


class MigrationResponse(BaseModel):
    """Response after migration execution."""

    success: bool
    wallet_id: int
    new_keys: dict
    old_balance_transferred: float
    migration_id: int


# ============================================================================
# Attack Simulation Schemas
# ============================================================================


class AttackSimulationResponse(BaseModel):
    """Response for quantum attack simulation."""

    wallet_id: int
    attack_successful: bool
    quantum_vulnerable: bool
    signature_broken: bool
    estimated_break_time_seconds: float
    message: str
    recommendation: str


# ============================================================================
# Dashboard Schemas
# ============================================================================


class CryptoAuditResponse(BaseModel):
    """Security audit showing crypto primitives used."""

    wallet_id: int
    current_algorithm: str
    current_algorithm_status: str
    post_quantum_algorithm: str
    signature_verification: dict
    quantum_threat_status: str
    migration_recommendation: str


class DashboardResponse(BaseModel):
    """Comprehensive dashboard response."""

    user: UserResponse
    wallets: List[WalletResponse]
    migration_logs: List[MigrationLogResponse]
    total_balance_qsv: float
    migrated_count: int
    vulnerable_count: int

    class Config:
        from_attributes = True


# ============================================================================
# Health Check Schemas
# ============================================================================


class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    database: str
    mcp_server: str
    version: str = "1.0.0"
