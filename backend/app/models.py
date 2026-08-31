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
    slug = Column(String(100), nullable=True)
    industry = Column(String(100), default="E-commerce", nullable=False)
    api_key = Column(String(255), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    customers = relationship("Customer", back_populates="merchant", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="merchant", cascade="all, delete-orphan")
    refunds = relationship("Refund", back_populates="merchant", cascade="all, delete-orphan")
    settlements = relationship("Settlement", back_populates="merchant", cascade="all, delete-orphan")
    agent_actions = relationship("AgentAction", back_populates="merchant", cascade="all, delete-orphan")
    recovery_opportunities = relationship("RecoveryOpportunity", back_populates="merchant", cascade="all, delete-orphan")
    recovery_actions = relationship("RecoveryAction", back_populates="merchant", cascade="all, delete-orphan")
    recovery_strategies = relationship("RecoveryStrategy", back_populates="merchant", cascade="all, delete-orphan")
    experiments = relationship("Experiment", back_populates="merchant", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="merchant", cascade="all, delete-orphan")
    ai_insights = relationship("AIInsight", back_populates="merchant", cascade="all, delete-orphan")
    checkout_dropoffs = relationship("CheckoutDropoff", back_populates="merchant", cascade="all, delete-orphan")
    subscription_dunnings = relationship("SubscriptionDunning", back_populates="merchant", cascade="all, delete-orphan")
    b2b_invoices = relationship("B2BInvoice", back_populates="merchant", cascade="all, delete-orphan")
    mandate_retries = relationship("MandateRetry", back_populates="merchant", cascade="all, delete-orphan")
    voice_call_logs = relationship("VoiceCallLog", back_populates="merchant", cascade="all, delete-orphan")
    promise_to_pays = relationship("PromiseToPay", back_populates="merchant", cascade="all, delete-orphan")
    compliance_rule_logs = relationship("ComplianceRuleLog", back_populates="merchant", cascade="all, delete-orphan")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String(36), primary_key=True)
    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(30), nullable=True)
    segment = Column(String(100), default="standard", nullable=False)  # standard, premium, vip
    lifetime_value = Column(Float, default=0.0, nullable=False)
    preferred_payment_method = Column(String(50), default="upi", nullable=False)
    typical_hour_start = Column(Integer, default=19, nullable=False)  # 7 PM
    typical_hour_end = Column(Integer, default=22, nullable=False)    # 10 PM
    historical_recovery_rate = Column(Float, default=0.83, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    merchant = relationship("Merchant", back_populates="customers")
    transactions = relationship("Transaction", back_populates="customer", cascade="all, delete-orphan")
    checkout_events = relationship("CheckoutEvent", back_populates="customer", cascade="all, delete-orphan")
    recovery_opportunities = relationship("RecoveryOpportunity", back_populates="customer", cascade="all, delete-orphan")

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
    payment_method = Column(String(50), nullable=False)  # card, upi, netbanking, wallet, emi
    bank_name = Column(String(100), nullable=True)      # HDFC, ICICI, SBI, Axis, Kotak
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False)
    failure_reason = Column(String(255), nullable=True)
    failure_code = Column(String(100), nullable=True)    # BAD_REQUEST_PAYMENT_DECLINED, GATEWAY_TIMEOUT, etc.
    failure_type = Column(String(100), nullable=True)    # temporary, issuer_declined, technical, insufficient_funds
    risk_score = Column(Float, default=0.1, nullable=False)
    product_id = Column(String(36), nullable=True)
    order_id = Column(String(36), nullable=True)
    device_type = Column(String(50), nullable=True)      # mobile, desktop, tablet
    location = Column(String(100), nullable=True)        # city/region
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    merchant = relationship("Merchant", back_populates="transactions")
    customer = relationship("Customer", back_populates="transactions")
    refunds = relationship("Refund", back_populates="transaction", cascade="all, delete-orphan")
    recovery_predictions = relationship("RecoveryPrediction", back_populates="transaction", cascade="all, delete-orphan")
    recovery_opportunity = relationship("RecoveryOpportunity", back_populates="transaction", uselist=False, cascade="all, delete-orphan")
    recovery_actions = relationship("RecoveryAction", back_populates="transaction", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_transaction_merchant_id", "merchant_id"),
        Index("idx_transaction_customer_id", "customer_id"),
        Index("idx_transaction_status", "status"),
        Index("idx_transaction_created_at", "created_at"),
        Index("idx_transaction_payment_method", "payment_method"),
        Index("idx_transaction_merchant_status_time", "merchant_id", "status", "created_at"),
    )


class RecoveryOpportunity(Base):
    __tablename__ = "recovery_opportunities"

    id = Column(String(36), primary_key=True)
    transaction_id = Column(String(36), ForeignKey("transactions.id"), nullable=False)
    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=False)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    amount = Column(Float, nullable=False)
    recovery_probability = Column(Float, nullable=False)   # 0.0 to 1.0 (e.g. 0.91)
    expected_recovery = Column(Float, nullable=False)      # amount * probability
    priority = Column(String(20), default="high", nullable=False)  # critical, high, medium, low
    recommended_action = Column(String(100), nullable=False)       # Retry UPI, Retry in 30m, WhatsApp + Retry, etc.
    recommended_time = Column(DateTime, nullable=True)
    confidence_score = Column(Float, default=0.85, nullable=False)
    explainability_reasons = Column(Text, nullable=True)  # JSON array of reasons
    status = Column(String(50), default="identified", nullable=False) # identified, scheduled, recovered, abandoned, dismissed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    transaction = relationship("Transaction", back_populates="recovery_opportunity")
    merchant = relationship("Merchant", back_populates="recovery_opportunities")
    customer = relationship("Customer", back_populates="recovery_opportunities")
    actions = relationship("RecoveryAction", back_populates="opportunity", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_opp_merchant_id", "merchant_id"),
        Index("idx_opp_priority", "priority"),
        Index("idx_opp_status", "status"),
        Index("idx_opp_probability", "recovery_probability"),
    )


class RecoveryAction(Base):
    __tablename__ = "recovery_actions"

    id = Column(String(36), primary_key=True)
    opportunity_id = Column(String(36), ForeignKey("recovery_opportunities.id"), nullable=True)
    transaction_id = Column(String(36), ForeignKey("transactions.id"), nullable=False)
    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=False)
    action_type = Column(String(100), nullable=False)  # smart_retry, upi_link, whatsapp_nudge, sms_fallback, smart_routing
    channel = Column(String(50), default="upi", nullable=False) # upi, whatsapp, sms, email, routing
    status = Column(String(50), default="scheduled", nullable=False) # scheduled, executing, recovered, failed, cancelled
    scheduled_for = Column(DateTime, nullable=True)
    executed_at = Column(DateTime, nullable=True)
    cost = Column(Float, default=1.5, nullable=False)  # Recovery / messaging cost in INR
    recovered_amount = Column(Float, default=0.0, nullable=False)
    net_recovered = Column(Float, default=0.0, nullable=False)
    execution_log = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    opportunity = relationship("RecoveryOpportunity", back_populates="actions")
    transaction = relationship("Transaction", back_populates="recovery_actions")
    merchant = relationship("Merchant", back_populates="recovery_actions")

    __table_args__ = (
        Index("idx_action_merchant_id", "merchant_id"),
        Index("idx_action_status", "status"),
        Index("idx_action_scheduled", "scheduled_for"),
    )


class RecoveryStrategy(Base):
    __tablename__ = "recovery_strategies"

    id = Column(String(36), primary_key=True)
    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    trigger_conditions = Column(Text, nullable=True)  # JSON
    wait_delay_minutes = Column(Integer, default=90, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    retry_methods = Column(Text, nullable=True)        # JSON array: ["upi", "card"]
    communication_channels = Column(Text, nullable=True) # JSON array: ["whatsapp", "sms"]
    min_amount = Column(Float, default=100.0, nullable=False)
    max_amount = Column(Float, default=500000.0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    recovery_rate_baseline = Column(Float, default=0.61, nullable=False)
    recovery_rate_optimized = Column(Float, default=0.71, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    merchant = relationship("Merchant", back_populates="recovery_strategies")


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(String(36), primary_key=True)
    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    hypothesis = Column(String(500), nullable=True)
    control_name = Column(String(100), default="Control", nullable=False)
    control_config = Column(Text, nullable=True)  # JSON
    variant_name = Column(String(100), default="Variant", nullable=False)
    variant_config = Column(Text, nullable=True)  # JSON
    status = Column(String(50), default="running", nullable=False) # running, completed, draft
    sample_size = Column(Integer, default=18420, nullable=False)
    control_conversions = Column(Integer, default=5655, nullable=False)
    control_rate = Column(Float, default=0.614, nullable=False)
    variant_conversions = Column(Integer, default=6189, nullable=False)
    variant_rate = Column(Float, default=0.672, nullable=False)
    uplift_pct = Column(Float, default=9.4, nullable=False)
    statistical_confidence = Column(Float, default=98.6, nullable=False) # 98.6%
    winner = Column(String(50), nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)

    merchant = relationship("Merchant", back_populates="experiments")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True)
    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    alert_type = Column(String(50), default="failure_spike", nullable=False) # failure_spike, revenue_opportunity, recovery_decline, model_anomaly, bank_outage
    severity = Column(String(20), default="high", nullable=False) # critical, high, medium, low
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    potential_impact = Column(String(100), nullable=True) # e.g. "₹6.4L/hour"
    ai_assessment = Column(Text, nullable=True)
    status = Column(String(50), default="active", nullable=False) # active, snoozed, resolved, acknowledged
    resolved_at = Column(DateTime, nullable=True)

    merchant = relationship("Merchant", back_populates="alerts")


class AIInsight(Base):
    __tablename__ = "ai_insights"

    id = Column(String(36), primary_key=True)
    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=False)
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    category = Column(String(50), default="timing", nullable=False) # timing, payment_method, customer_behavior, opportunity
    impact_amount_min = Column(Float, default=0.0, nullable=False)
    impact_amount_max = Column(Float, default=0.0, nullable=False)
    recommended_action = Column(String(255), nullable=False)
    explainability = Column(Text, nullable=True) # JSON array
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    merchant = relationship("Merchant", back_populates="ai_insights")


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
    user_role = Column(String(50), default="Revenue Operations", nullable=False)
    agent_id = Column(String(36), nullable=True)
    merchant_id = Column(String(36), nullable=True)
    action = Column(String(255), nullable=False)
    target_type = Column(String(50), nullable=True) # transaction, opportunity, strategy, experiment, setting
    target_id = Column(String(100), nullable=True)
    action_data = Column(Text, nullable=True)  # JSON string
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    result = Column(String(50), nullable=False)  # success, failure
    approval_status = Column(String(50), nullable=True)  # approved, rejected, pending

    __table_args__ = (
        Index("idx_audit_timestamp", "timestamp"),
        Index("idx_audit_merchant_id", "merchant_id"),
        Index("idx_audit_action", "action"),
    )


class CheckoutDropoff(Base):
    __tablename__ = "checkout_dropoffs"

    id = Column(String(36), primary_key=True)
    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=False)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=True)
    customer_name = Column(String(255), nullable=False)
    customer_email = Column(String(255), nullable=False)
    customer_phone = Column(String(30), nullable=True)
    session_id = Column(String(255), nullable=False)
    cart_value = Column(Float, nullable=False)
    items_summary = Column(Text, nullable=True)
    dropoff_stage = Column(String(50), default="payment_page", nullable=False)  # cart_page, payment_method_select, 3ds_redirect
    cause = Column(String(50), default="price_hesitation", nullable=False)  # price_hesitation, form_friction, otp_delay, session_expiry
    cause_confidence = Column(Float, default=0.88, nullable=False)
    nudge_channel = Column(String(50), default="whatsapp", nullable=False)  # whatsapp, sms, email
    nudge_status = Column(String(50), default="pending", nullable=False)  # pending, sent, opened, converted
    resume_token = Column(String(100), unique=True, nullable=False)
    discount_code_applied = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    converted_at = Column(DateTime, nullable=True)

    merchant = relationship("Merchant", back_populates="checkout_dropoffs")

    __table_args__ = (
        Index("idx_dropoff_merchant_id", "merchant_id"),
        Index("idx_dropoff_cause", "cause"),
        Index("idx_dropoff_status", "nudge_status"),
        Index("idx_dropoff_created_at", "created_at"),
    )


class SubscriptionDunning(Base):
    __tablename__ = "subscription_dunnings"

    id = Column(String(36), primary_key=True)
    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=False)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    customer_name = Column(String(255), nullable=False)
    customer_email = Column(String(255), nullable=False)
    plan_name = Column(String(100), nullable=False)
    recurring_amount = Column(Float, nullable=False)
    billing_cycle = Column(String(50), default="monthly", nullable=False)
    failure_reason = Column(String(100), default="insufficient_balance", nullable=False)  # expired_card, insufficient_balance, mandate_revoked, bank_decline
    dunning_stage = Column(String(50), default="day_0_in_app", nullable=False)  # day_0_in_app, day_3_email, day_7_whatsapp, day_14_final, suspended
    retry_count = Column(Integer, default=0, nullable=False)
    next_retry_at = Column(DateTime, nullable=True)
    salary_cycle_day = Column(Integer, default=1, nullable=False)  # estimated salary credit day (e.g. 1st or 5th)
    update_payment_token = Column(String(100), unique=True, nullable=False)
    is_involuntary = Column(Boolean, default=True, nullable=False)  # True = involuntary decline, False = intentional cancellation
    status = Column(String(50), default="recovering", nullable=False)  # recovering, recovered, churned_involuntary, cancelled_voluntary
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    recovered_at = Column(DateTime, nullable=True)

    merchant = relationship("Merchant", back_populates="subscription_dunnings")

    __table_args__ = (
        Index("idx_dunning_merchant_id", "merchant_id"),
        Index("idx_dunning_stage", "dunning_stage"),
        Index("idx_dunning_status", "status"),
    )


class B2BInvoice(Base):
    __tablename__ = "b2b_invoices"

    id = Column(String(36), primary_key=True)
    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=False)
    invoice_number = Column(String(100), unique=True, nullable=False)
    buyer_name = Column(String(255), nullable=False)
    buyer_email = Column(String(255), nullable=False)
    buyer_phone = Column(String(30), nullable=True)
    buyer_gstin = Column(String(30), nullable=True)
    amount = Column(Float, nullable=False)
    due_date = Column(DateTime, nullable=False)
    days_past_due = Column(Integer, default=0, nullable=False)
    risk_tier = Column(String(50), default="medium", nullable=False)  # low, medium, high, critical
    payment_terms = Column(String(50), default="Net 30", nullable=False)
    expected_recovery_prob = Column(Float, default=0.75, nullable=False)
    current_stage = Column(String(50), default="friendly_nudge", nullable=False)  # friendly_nudge, formal_notice, account_owner_escalation, collections_handoff
    settlement_link = Column(String(255), nullable=False)
    status = Column(String(50), default="pending", nullable=False)  # pending, partially_paid, settled, in_collections, written_off
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    settled_at = Column(DateTime, nullable=True)

    merchant = relationship("Merchant", back_populates="b2b_invoices")
    reminders = relationship("B2BReminder", back_populates="invoice", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_b2b_merchant_id", "merchant_id"),
        Index("idx_b2b_dpd", "days_past_due"),
        Index("idx_b2b_risk_tier", "risk_tier"),
        Index("idx_b2b_status", "status"),
    )


class B2BReminder(Base):
    __tablename__ = "b2b_reminders"

    id = Column(String(36), primary_key=True)
    invoice_id = Column(String(36), ForeignKey("b2b_invoices.id"), nullable=False)
    stage = Column(String(50), nullable=False)
    channel = Column(String(50), default="email", nullable=False)  # email, whatsapp, phone_call
    recipient = Column(String(255), nullable=False)
    subject_or_template = Column(String(255), nullable=False)
    content_preview = Column(Text, nullable=True)
    sent_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String(50), default="sent", nullable=False)

    invoice = relationship("B2BInvoice", back_populates="reminders")

    __table_args__ = (
        Index("idx_reminder_invoice_id", "invoice_id"),
    )


class MandateRetry(Base):
    __tablename__ = "mandate_retries"

    id = Column(String(36), primary_key=True)
    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=False)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    customer_name = Column(String(255), nullable=False)
    mandate_id = Column(String(100), nullable=False)
    mandate_type = Column(String(50), default="upi_autopay", nullable=False)  # upi_autopay, enach
    amount = Column(Float, nullable=False)
    bank_name = Column(String(100), nullable=False)
    failure_code = Column(String(100), default="BANK_AUTH_TIMEOUT", nullable=False)
    attempt_count = Column(Integer, default=1, nullable=False)  # 1 to 3
    max_attempts = Column(Integer, default=3, nullable=False)   # RBI limit = 3
    rbi_retry_window_start = Column(DateTime, nullable=False)
    rbi_retry_window_end = Column(DateTime, nullable=False)
    next_retry_at = Column(DateTime, nullable=True)
    status = Column(String(50), default="scheduled", nullable=False)  # scheduled, retrying, succeeded, exhausted, fallback_link_sent
    fallback_payment_link = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    merchant = relationship("Merchant", back_populates="mandate_retries")

    __table_args__ = (
        Index("idx_mandate_merchant_id", "merchant_id"),
        Index("idx_mandate_status", "status"),
        Index("idx_mandate_type", "mandate_type"),
    )


class VoiceCallLog(Base):
    __tablename__ = "voice_call_logs"

    id = Column(String(36), primary_key=True)
    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=False)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=True)
    customer_name = Column(String(255), nullable=False)
    customer_phone = Column(String(30), nullable=False)
    call_sid = Column(String(100), unique=True, nullable=False)
    language = Column(String(50), default="hinglish", nullable=False)
    duration_seconds = Column(Integer, default=45, nullable=False)
    call_status = Column(String(50), default="completed", nullable=False)  # completed, busy, no_answer, voicemail
    transcript_hinglish = Column(Text, nullable=False)
    transcript_english = Column(Text, nullable=False)
    detected_intent = Column(String(100), nullable=False)
    detected_objection = Column(String(100), default="salary_pending", nullable=False)  # salary_pending, retry_link_needed, disputed_amount, technical_glitch, will_pay_online
    captured_ptp_date = Column(DateTime, nullable=True)
    captured_ptp_amount = Column(Float, nullable=True)
    audio_simulation_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    merchant = relationship("Merchant", back_populates="voice_call_logs")

    __table_args__ = (
        Index("idx_voice_merchant_id", "merchant_id"),
        Index("idx_voice_status", "call_status"),
        Index("idx_voice_created_at", "created_at"),
    )


class PromiseToPay(Base):
    __tablename__ = "promise_to_pays"

    id = Column(String(36), primary_key=True)
    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=False)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    customer_name = Column(String(255), nullable=False)
    reference_type = Column(String(50), default="transaction", nullable=False)  # transaction, invoice, subscription
    reference_id = Column(String(100), nullable=False)
    promised_amount = Column(Float, nullable=False)
    promised_date = Column(DateTime, nullable=False)
    channel_source = Column(String(50), default="voice_agent", nullable=False)  # voice_agent, whatsapp, chat, email
    fulfillment_status = Column(String(50), default="pending", nullable=False)  # pending, kept, broken, rescheduled
    reliability_score = Column(Float, default=85.0, nullable=False)  # 0 to 100 based on historical kept/broken
    reminded_at = Column(DateTime, nullable=True)
    fulfilled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    merchant = relationship("Merchant", back_populates="promise_to_pays")

    __table_args__ = (
        Index("idx_ptp_merchant_id", "merchant_id"),
        Index("idx_ptp_status", "fulfillment_status"),
        Index("idx_ptp_promised_date", "promised_date"),
    )


class ComplianceRuleLog(Base):
    __tablename__ = "compliance_rule_logs"

    id = Column(String(36), primary_key=True)
    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=True)
    customer_id = Column(String(36), nullable=True)
    target_type = Column(String(50), default="transaction", nullable=False)  # transaction, invoice, mandate, dropoff
    target_id = Column(String(100), nullable=False)
    channel = Column(String(50), default="whatsapp", nullable=False)  # sms, whatsapp, voice_call, card_retry
    rule_applied = Column(String(100), nullable=False)  # rbi_retry_limit, npci_quiet_hours, dnd_registry_block, customer_opt_out, auto_halt_on_payment
    action_taken = Column(String(50), nullable=False)   # dispatched, blocked_quiet_hours, blocked_dnd, halted_recovered, throttled_max_attempts
    rationale = Column(Text, nullable=False)
    regulatory_citation = Column(String(255), default="NPCI Circular 2026/04", nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    merchant = relationship("Merchant", back_populates="compliance_rule_logs")

    __table_args__ = (
        Index("idx_compliance_merchant_id", "merchant_id"),
        Index("idx_compliance_action", "action_taken"),
        Index("idx_compliance_timestamp", "timestamp"),
    )

