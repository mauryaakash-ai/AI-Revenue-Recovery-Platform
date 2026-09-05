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
    sms_logs = relationship("SMSLog", back_populates="merchant", cascade="all, delete-orphan")
    users = relationship("User", back_populates="merchant", cascade="all, delete-orphan")
    webhook_events = relationship("WebhookEvent", back_populates="merchant", cascade="all, delete-orphan")
    policies = relationship("MerchantPolicy", back_populates="merchant", cascade="all, delete-orphan")
    bandit_logs = relationship("BanditArmLog", back_populates="merchant", cascade="all, delete-orphan")


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
    recovery_profile = relationship("CustomerRecoveryProfile", back_populates="customer", uselist=False, cascade="all, delete-orphan")

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
    voice_persona = Column(String(50), default="priya", nullable=True)  # priya, rahul, swara, madhur, kavya
    transaction_id = Column(String(36), nullable=True)
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


class SMSLog(Base):
    __tablename__ = "sms_logs"

    id = Column(String(36), primary_key=True)
    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=False)
    recipient_phone = Column(String(30), nullable=False)
    message_body = Column(Text, nullable=False)
    template_name = Column(String(100), default="custom", nullable=False)  # cart_recovery, payment_retry, login_otp, ptp_reminder, mandate_pre_debit, custom
    provider = Column(String(100), default="textbelt_free", nullable=False)  # textbelt_free, ntfy_stream, twilio, rzrpay_sandbox
    status = Column(String(50), default="delivered", nullable=False)  # queued, sent, delivered, failed, clicked
    dlt_template_id = Column(String(100), default="1407161829038102938", nullable=False)
    carrier_msg_id = Column(String(100), nullable=True)
    delivery_latency_ms = Column(Integer, default=1240, nullable=False)
    cost_inr = Column(Float, default=0.0, nullable=False)  # Free for demo!
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    merchant = relationship("Merchant", back_populates="sms_logs")

    __table_args__ = (
        Index("idx_sms_merchant_id", "merchant_id"),
        Index("idx_sms_status", "status"),
        Index("idx_sms_created_at", "created_at"),
        Index("idx_sms_recipient", "recipient_phone"),
    )


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(30), nullable=True)
    role = Column(String(50), default="Revenue Operations", nullable=False)  # Admin, Revenue Operations, Finance, Operations, Analyst, Support
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    merchant = relationship("Merchant", back_populates="users")

    __table_args__ = (
        Index("idx_user_merchant_id", "merchant_id"),
        Index("idx_user_email", "email"),
    )


class WebhookEvent(Base):
    """Raw and normalized webhook events from payment gateways (Razorpay, Stripe, Generic)"""
    __tablename__ = "webhook_events"

    id = Column(String(64), primary_key=True)
    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=False)
    provider = Column(String(50), nullable=False)  # razorpay, stripe, generic
    event_type = Column(String(100), nullable=False)  # payment.failed, charge.failed, payment_intent.payment_failed
    event_id = Column(String(100), nullable=True)  # Provider event id
    idempotency_key = Column(String(128), unique=True, nullable=False)
    signature = Column(String(255), nullable=True)
    payload = Column(Text, nullable=False)  # Raw JSON payload
    status = Column(String(50), default="received", nullable=False)  # received, processed, duplicate, failed
    error_message = Column(Text, nullable=True)
    normalized_transaction_id = Column(String(36), nullable=True)
    received_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True)

    merchant = relationship("Merchant", back_populates="webhook_events")

    __table_args__ = (
        Index("idx_webhook_merchant", "merchant_id"),
        Index("idx_webhook_status", "status"),
        Index("idx_webhook_idempotency", "idempotency_key"),
        Index("idx_webhook_provider", "provider"),
    )


class MerchantPolicy(Base):
    """Merchant-specific governance, risk policies, quiet hours, and retry thresholds"""
    __tablename__ = "merchant_policies"

    id = Column(String(36), primary_key=True)
    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=False)
    confidence_threshold = Column(Float, default=0.85, nullable=False)  # >= 85% auto-executes
    max_retry_attempts = Column(Integer, default=3, nullable=False)
    cooldown_hours = Column(Float, default=4.0, nullable=False)
    max_communication_cost_inr = Column(Float, default=15.0, nullable=False)
    max_auto_recovery_amount = Column(Float, default=25000.0, nullable=False)
    min_expected_roi = Column(Float, default=2.0, nullable=False)  # Minimum 2x Net ROI
    quiet_hours_start_ist = Column(Integer, default=21, nullable=False)  # 9 PM IST
    quiet_hours_end_ist = Column(Integer, default=8, nullable=False)     # 8 AM IST
    allowed_channels = Column(Text, default='["whatsapp", "sms", "upi_intent", "card_retry"]', nullable=False)
    kill_switch_active = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    merchant = relationship("Merchant", back_populates="policies")

    __table_args__ = (
        Index("idx_policy_merchant", "merchant_id"),
    )


class BankHealthRecord(Base):
    """Real-time issuer bank health, ACS degradation, and anomaly monitoring"""
    __tablename__ = "bank_health_records"

    id = Column(String(36), primary_key=True)
    bank_name = Column(String(100), nullable=False)  # HDFC Bank, SBI, ICICI Bank, Axis Bank, Kotak Mahindra
    success_rate = Column(Float, default=0.92, nullable=False)
    failure_rate = Column(Float, default=0.08, nullable=False)
    timeout_rate = Column(Float, default=0.02, nullable=False)
    avg_latency_ms = Column(Integer, default=1450, nullable=False)
    anomaly_score = Column(Float, default=0.05, nullable=False)
    degradation_status = Column(String(50), default="healthy", nullable=False)  # healthy, degraded, critical
    recommended_action = Column(String(255), default="NORMAL_ROUTING", nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_bank_health_name", "bank_name"),
        Index("idx_bank_health_status", "degradation_status"),
        Index("idx_bank_health_recorded", "recorded_at"),
    )


class GatewayHealthRecord(Base):
    """Real-time payment gateway health, failure spikes, and routing telemetry"""
    __tablename__ = "gateway_health_records"

    id = Column(String(36), primary_key=True)
    gateway_name = Column(String(100), nullable=False)  # Razorpay Optimizer, Stripe, PayU, BillDesk, Cashfree
    success_rate = Column(Float, default=0.94, nullable=False)
    failure_rate = Column(Float, default=0.06, nullable=False)
    timeout_rate = Column(Float, default=0.015, nullable=False)
    avg_latency_ms = Column(Integer, default=980, nullable=False)
    anomaly_score = Column(Float, default=0.03, nullable=False)
    degradation_status = Column(String(50), default="healthy", nullable=False)  # healthy, degraded, critical
    recommended_action = Column(String(255), default="OPTIMAL_ROUTING", nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_gateway_health_name", "gateway_name"),
        Index("idx_gateway_health_status", "degradation_status"),
    )


class BanditArmLog(Base):
    """Safe contextual multi-armed bandit audit trail and learning loop updates"""
    __tablename__ = "bandit_arm_logs"

    id = Column(String(36), primary_key=True)
    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=False)
    transaction_id = Column(String(36), nullable=False)
    arm_name = Column(String(100), nullable=False)  # upi_intent, delayed_card_retry, whatsapp_recovery, etc.
    context_features = Column(Text, nullable=False)  # JSON representation of state
    expected_reward = Column(Float, nullable=False)
    actual_reward = Column(Float, nullable=True)  # Net recovered revenue upon completion
    channel_cost = Column(Float, default=1.85, nullable=False)
    is_exploration = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)

    merchant = relationship("Merchant", back_populates="bandit_logs")

    __table_args__ = (
        Index("idx_bandit_merchant", "merchant_id"),
        Index("idx_bandit_arm", "arm_name"),
        Index("idx_bandit_created", "created_at"),
    )


class RiskAssessment(Base):
    """Dedicated pre-recovery risk engine evaluation and anti-fraud verification"""
    __tablename__ = "risk_assessments"

    id = Column(String(36), primary_key=True)
    transaction_id = Column(String(36), nullable=False)
    merchant_id = Column(String(36), nullable=False)
    customer_id = Column(String(36), nullable=True)
    risk_score = Column(Float, default=15.0, nullable=False)  # 0 to 100
    risk_tier = Column(String(50), default="LOW_RISK", nullable=False)  # LOW_RISK, MEDIUM_RISK, HIGH_RISK, BLOCKED
    velocity_1h = Column(Integer, default=1, nullable=False)
    velocity_24h = Column(Integer, default=1, nullable=False)
    amount_deviation_score = Column(Float, default=0.1, nullable=False)
    instrument_switch_count = Column(Integer, default=0, nullable=False)
    risk_factors = Column(Text, default="[]", nullable=False)  # JSON array of detected risk signals
    is_eligible_for_recovery = Column(Boolean, default=True, nullable=False)
    evaluated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_risk_txn", "transaction_id"),
        Index("idx_risk_tier", "risk_tier"),
    )


class FailureClassificationCorrection(Base):
    """Hierarchical failure taxonomy corrections and human-in-the-loop feedback"""
    __tablename__ = "failure_classification_corrections"

    id = Column(String(36), primary_key=True)
    transaction_id = Column(String(36), nullable=False)
    merchant_id = Column(String(36), nullable=False)
    predicted_category = Column(String(50), nullable=False)  # Issuer, Gateway, Authentication, Customer, Permanent
    predicted_subcategory = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    corrected_category = Column(String(50), nullable=False)
    corrected_subcategory = Column(String(100), nullable=False)
    operator_id = Column(String(100), default="revops_lead", nullable=False)
    feedback_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_fail_correction_txn", "transaction_id"),
        Index("idx_fail_correction_cat", "corrected_category"),
    )


class CustomerRecoveryProfile(Base):
    """Deep customer affinity, conversion benchmarks, and active recovery windows"""
    __tablename__ = "customer_recovery_profiles"

    id = Column(String(36), primary_key=True)
    customer_id = Column(String(36), ForeignKey("customers.id"), unique=True, nullable=False)
    merchant_id = Column(String(36), nullable=False)
    total_transactions = Column(Integer, default=10, nullable=False)
    failed_transactions = Column(Integer, default=2, nullable=False)
    recovered_transactions = Column(Integer, default=2, nullable=False)
    recovery_success_rate = Column(Float, default=0.85, nullable=False)
    preferred_channel = Column(String(50), default="upi", nullable=False)
    channel_conversion_rates = Column(Text, default='{"upi": 0.88, "whatsapp": 0.74, "card": 0.42, "sms": 0.58}', nullable=False)
    best_window_start_hour = Column(Integer, default=19, nullable=False)  # 7 PM IST
    best_window_end_hour = Column(Integer, default=22, nullable=False)    # 10 PM IST
    avg_recovery_latency_minutes = Column(Float, default=6.5, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    customer = relationship("Customer", back_populates="recovery_profile")

    __table_args__ = (
        Index("idx_cust_prof_cust", "customer_id"),
        Index("idx_cust_prof_channel", "preferred_channel"),
    )

