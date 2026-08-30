from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, DateTime, ForeignKey, 
    Enum, Text, Boolean, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.database import Base
import enum as python_enum


class TransactionStatus(str, python_enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RefundStatus(str, python_enum.Enum):
    INITIATED = "initiated"
    COMPLETED = "completed"
    FAILED = "failed"
    PENDING = "pending"


class SettlementStatus(str, python_enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class ActionStatus(str, python_enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    FAILED = "failed"


class ActionTier(str, python_enum.Enum):
    READ = "read"
    ANALYZE = "analyze"
    RECOMMEND = "recommend"
    LOW_RISK_ACTION = "low_risk_action"
    SENSITIVE_ACTION = "sensitive_action"


class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    api_key = Column(String(255), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    customers = relationship("Customer", back_populates="merchant", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="merchant", cascade="all, delete-orphan")
    refunds = relationship("Refund", back_populates="merchant", cascade="all, delete-orphan")
    settlements = relationship("Settlement", back_populates="merchant", cascade="all, delete-orphan")
    agent_actions = relationship("AgentAction", back_populates="merchant", cascade="all, delete-orphan")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String(36), primary_key=True)
    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    segment = Column(String(100), default="standard", nullable=False)
    lifetime_value = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    merchant = relationship("Merchant", back_populates="customers")
    transactions = relationship("Transaction", back_populates="customer", cascade="all, delete-orphan")
    checkout_events = relationship("CheckoutEvent", back_populates="customer", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_customer_merchant_id", "merchant_id"),
        Index("idx_customer_merchant", "merchant_id", "id"),
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True)
    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=False)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="INR", nullable=False)
    payment_method = Column(String(50), nullable=False)  # card, upi, netbanking, wallet
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False)
    failure_reason = Column(String(255), nullable=True)
    product_id = Column(String(36), nullable=True)
    order_id = Column(String(36), nullable=True)
    device_type = Column(String(50), nullable=True)  # mobile, desktop, tablet
    location = Column(String(100), nullable=True)  # city/region
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    merchant = relationship("Merchant", back_populates="transactions")
    customer = relationship("Customer", back_populates="transactions")
    refunds = relationship("Refund", back_populates="transaction", cascade="all, delete-orphan")
    recovery_predictions = relationship("RecoveryPrediction", back_populates="transaction", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_transaction_merchant_id", "merchant_id"),
        Index("idx_transaction_customer_id", "customer_id"),
        Index("idx_transaction_status", "status"),
        Index("idx_transaction_created_at", "created_at"),
        Index("idx_transaction_payment_method", "payment_method"),
        Index("idx_transaction_merchant_status_time", "merchant_id", "status", "created_at"),
    )


class Refund(Base):
    __tablename__ = "refunds"

    id = Column(String(36), primary_key=True)
    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=False)
    transaction_id = Column(String(36), ForeignKey("transactions.id"), nullable=False)
    amount = Column(Float, nullable=False)
    reason = Column(String(255), nullable=False)
    status = Column(Enum(RefundStatus), default=RefundStatus.INITIATED, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    merchant = relationship("Merchant", back_populates="refunds")
    transaction = relationship("Transaction", back_populates="refunds")

    __table_args__ = (
        Index("idx_refund_merchant_id", "merchant_id"),
        Index("idx_refund_transaction_id", "transaction_id"),
        Index("idx_refund_created_at", "created_at"),
    )


class Settlement(Base):
    __tablename__ = "settlements"

    id = Column(String(36), primary_key=True)
    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(Enum(SettlementStatus), default=SettlementStatus.PENDING, nullable=False)
    settlement_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    merchant = relationship("Merchant", back_populates="settlements")

    __table_args__ = (
        Index("idx_settlement_merchant_id", "merchant_id"),
        Index("idx_settlement_date", "settlement_date"),
    )


class CheckoutEvent(Base):
    __tablename__ = "checkout_events"

    id = Column(String(36), primary_key=True)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    session_id = Column(String(255), nullable=False)
    event = Column(String(100), nullable=False)  # initiated, abandoned, completed
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    customer = relationship("Customer", back_populates="checkout_events")

    __table_args__ = (
        Index("idx_checkout_customer_id", "customer_id"),
        Index("idx_checkout_session_id", "session_id"),
        Index("idx_checkout_timestamp", "timestamp"),
    )


class RecoveryPrediction(Base):
    __tablename__ = "recovery_predictions"

    id = Column(String(36), primary_key=True)
    transaction_id = Column(String(36), ForeignKey("transactions.id"), nullable=False)
    probability = Column(Float, nullable=False)  # 0-1
    expected_recovery = Column(Float, nullable=False)  # amount expected to recover
    model_version = Column(String(50), default="v1.0", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    transaction = relationship("Transaction", back_populates="recovery_predictions")

    __table_args__ = (
        Index("idx_recovery_transaction_id", "transaction_id"),
        Index("idx_recovery_probability", "probability"),
    )


class AgentAction(Base):
    __tablename__ = "agent_actions"

    id = Column(String(36), primary_key=True)
    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=False)
    agent = Column(String(100), default="revpilot", nullable=False)
    action = Column(String(255), nullable=False)  # action name
    tool = Column(String(255), nullable=False)  # tool name
    tool_tier = Column(Enum(ActionTier), default=ActionTier.READ, nullable=False)
    input_data = Column(Text, nullable=True)  # JSON string
    result = Column(Text, nullable=True)  # JSON string
    status = Column(Enum(ActionStatus), default=ActionStatus.PENDING, nullable=False)
    approval = Column(String(255), nullable=True)  # approved_by, rejected_by, auto_approved, etc.
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    executed_at = Column(DateTime, nullable=True)

    merchant = relationship("Merchant", back_populates="agent_actions")

    __table_args__ = (
        Index("idx_agent_merchant_id", "merchant_id"),
        Index("idx_agent_status", "status"),
        Index("idx_agent_created_at", "created_at"),
        Index("idx_agent_tool", "tool"),
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=True)
    agent_id = Column(String(36), nullable=True)
    merchant_id = Column(String(36), nullable=True)
    action = Column(String(255), nullable=False)
    action_data = Column(Text, nullable=True)  # JSON string
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    result = Column(String(50), nullable=False)  # success, failure
    approval_status = Column(String(50), nullable=True)  # approved, rejected, pending

    __table_args__ = (
        Index("idx_audit_timestamp", "timestamp"),
        Index("idx_audit_merchant_id", "merchant_id"),
        Index("idx_audit_action", "action"),
    )
