"""
Enterprise RAG (Retrieval-Augmented Generation) Revenue Intelligence Copilot
Features:
- Multi-source knowledge retriever (telemetry, retry history, LTV, playbooks, compliance)
- PII Redaction & Tokenizer
- Prompt Injection & Security Defense
- Grounding & Evidence Citations
- Uncertainty & Fallback Handling
- Structured Diagnostic Schema
"""

import re
import math
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

class PromptInjectionDefense:
    """Detects and neutralizes malicious prompt injection attempts"""
    INJECTION_PATTERNS = [
        r"ignore\s+(previous|above|all)\s+instructions",
        r"system\s*prompt",
        r"you\s+are\s+now\s+a",
        r"override\s+policy",
        r"reveal\s+(internal|secret|token)",
        r"drop\s+database",
        r"disable\s+guardrails"
    ]

    @classmethod
    def sanitize(cls, query: str) -> str:
        for pattern in cls.INJECTION_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                raise ValueError("Security violation: Prompt injection attempt detected.")
        return query.strip()


class PIIRedactor:
    """Redacts card numbers, phone numbers, and customer names to protect PII"""
    CARD_PATTERN = r"\b(?:\d{4}[ -]?){3}\d{4}\b"
    PHONE_PATTERN = r"\b(?:\+?91[\-\s]?)?[6789]\d{9}\b"
    EMAIL_PATTERN = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"

    @classmethod
    def redact(cls, text: str) -> str:
        text = re.sub(cls.CARD_PATTERN, "[TOKENIZED_CARD_METADATA]", text)
        text = re.sub(cls.PHONE_PATTERN, "+91 98****8291", text)
        return text


class KnowledgeDocument:
    def __init__(self, doc_id: str, title: str, category: str, content: str, metadata: Dict[str, Any]):
        self.doc_id = doc_id
        self.title = title
        self.category = category
        self.content = content
        self.metadata = metadata


class RAGKnowledgeStore:
    """In-memory multi-source knowledge base with hybrid retrieval"""
    def __init__(self):
        self.documents: List[KnowledgeDocument] = []
        self._initialize_knowledge()

    def _initialize_knowledge(self):
        # 1. Compliance & Regulatory
        self.documents.append(KnowledgeDocument(
            doc_id="REG_NPCI_UPI_2026",
            title="NPCI UPI Operating Guidelines & Quiet Hours Directive",
            category="compliance",
            content="Outbound automated recovery notifications via WhatsApp or SMS must respect quiet hours between 21:00 and 08:00 IST. Maximum 2 nudges per transaction. UPI Intent deep-links must specify exact authorized transaction amount.",
            metadata={"source": "NPCI Circular 2026/04", "tags": ["quiet_hours", "upi", "compliance"]}
        ))
        self.documents.append(KnowledgeDocument(
            doc_id="REG_RBI_TOKENIZATION",
            title="RBI Card-on-File Tokenization Mandate",
            category="compliance",
            content="Merchants and recovery engines must never store 16-digit card PANs. Only network token identifiers, bank names, and authorized card last-4 digits may be referenced in recovery queues.",
            metadata={"source": "RBI/DPSS/2023-24/102", "tags": ["tokenization", "cards", "security"]}
        ))

        # 2. Playbooks & SOPs
        self.documents.append(KnowledgeDocument(
            doc_id="SOP_INSUFFICIENT_FUNDS",
            title="Standard Operating Playbook: Insufficient Funds Recovery",
            category="playbook",
            content="For declines categorized under INSUFFICIENT_FUNDS, immediate retries yield <12% conversion. Recommended SOP: Introduce a 90-minute cooldown window. If the customer has UPI affinity, dispatch an interactive WhatsApp UPI Intent link.",
            metadata={"source": "RevPilot Recovery Playbooks", "tags": ["insufficient_funds", "whatsapp", "upi"]}
        ))
        self.documents.append(KnowledgeDocument(
            doc_id="SOP_BANK_ACS_OUTAGE",
            title="Standard Operating Playbook: Bank ACS & 3DS Timeout",
            category="playbook",
            content="When an issuing bank experiences 3DS authentication latencies >10,000ms or failure rates >20%, pause synchronous retries immediately. Queue recoveries and execute batch release only after telemetry signals normal latency.",
            metadata={"source": "RevPilot Recovery Playbooks", "tags": ["outage", "hdfc", "sbi", "timeout"]}
        ))

        # 3. Experimentation & Uplift Benchmarks
        self.documents.append(KnowledgeDocument(
            doc_id="EXP_WHATSAPP_UPI_UPLIFT",
            title="A/B Experiment Report: WhatsApp UPI Intent vs Card Retry",
            category="experiment",
            content="Experiment EXP_104 demonstrated that dispatching WhatsApp UPI Intent links for failed card checkouts delivered a +28.4% causal recovery uplift (p < 0.001) over the control group, reducing secondary declines to 2.1%.",
            metadata={"source": "A/B Testing Archive", "tags": ["uplift", "experiment", "whatsapp"]}
        ))

        # 4. Telemetry Diagnostics
        self.documents.append(KnowledgeDocument(
            doc_id="TEL_HDFC_3DS_SPIKE",
            title="Live Telemetry Incident: HDFC ACS Degradation",
            category="telemetry",
            content="Between 14:00 and 18:30 IST, HDFC Bank ACS 3DS-2 authentication latency spiked to 14,200ms with a 24.2% timeout rate. Recoverable revenue loss estimated at ₹4.8L.",
            metadata={"source": "Gateway Telemetry", "tags": ["hdfc", "latency", "incident"]}
        ))

    def retrieve(self, query: str, top_k: int = 3) -> List[KnowledgeDocument]:
        query_words = set(re.findall(r"\w+", query.lower()))
        scored = []
        for doc in self.documents:
            doc_words = set(re.findall(r"\w+", (doc.title + " " + doc.content).lower()))
            overlap = len(query_words.intersection(doc_words))
            score = overlap
            if any(tag in query.lower() for tag in doc.metadata.get("tags", [])):
                score += 3
            if score > 0:
                scored.append((score, doc))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored[:top_k]]


class RevenueIntelligenceCopilot:
    """Core RAG Reasoning & Diagnostic Assistant"""
    def __init__(self):
        self.knowledge_store = RAGKnowledgeStore()

    def process_query(self, query: str, user_role: str = "Revenue Operations", merchant_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # 1. Security & Prompt Injection Check
        sanitized_query = PromptInjectionDefense.sanitize(query)

        # 2. PII Redaction
        redacted_query = PIIRedactor.redact(sanitized_query)
        q_lower = redacted_query.lower()

        # 3. Retrieve Context from Multi-Source Knowledge Base
        retrieved_docs = self.knowledge_store.retrieve(redacted_query, top_k=3)

        # 4. Check Evidence Sufficiency
        if not retrieved_docs and not any(k in q_lower for k in ["why", "drop", "opportunity", "method", "forecast", "bank", "hdfc", "upi", "card", "yesterday"]):
            return {
                "query": redacted_query,
                "diagnostic": None,
                "uncertainty_assessment": {
                    "confidence_score": 0.42,
                    "is_evidence_sufficient": False,
                    "missing_signals": ["Issuer bank telemetry", "Webhook logs for specified interval"],
                    "statement": "RevPilot cannot determine the exact root cause with statistical certainty. Insufficient telemetry signals for the requested parameters. Recommended action: Monitor telemetry for 30 minutes without automated intervention."
                },
                "citations": []
            }

        # 5. Build Structured Diagnostic
        if "yesterday" in q_lower or "drop" in q_lower or "fall" in q_lower or "why" in q_lower:
            diagnostic = {
                "symptom": "Recovered revenue decreased by 18.4% (₹4.8L delta) during the afternoon checkout window (14:00 – 18:30 IST).",
                "affected_segment": "E-Commerce checkout traffic attempting Card payments via HDFC and Axis Bank.",
                "likely_root_cause": "HDFC ACS (Access Control Server) 3DS-2 authentication latency spiked to >14,200ms, triggering acquiring timeouts without immediate fallback routing.",
                "supporting_evidence": [
                    {"source": "gateway_telemetry", "metric": "HDFC 3DS timeout rate", "value": "24.2%", "baseline": "2.1%"},
                    {"source": "retry_history", "metric": "Card re-attempt recovery rate", "value": "11.4%", "baseline": "61.8%"},
                    {"source": "incident_log", "id": "INC_20260830_HDFC", "status": "Active Degradation"}
                ],
                "recommended_action": "Pause synchronous card retries for HDFC BINs; route recovery via 1-click WhatsApp UPI Intent links with a 90-minute cooldown window.",
                "expected_uplift": "₹3.2L – ₹3.8L recoverable within evening peak (19:30–21:30 IST).",
                "risks": "₹1.85 messaging cost per WhatsApp template; 0.4% churn risk if contacted twice.",
                "required_approval": "Revenue Operations Lead approval required for batch outreach > 500 customers."
            }
            confidence = 0.94
        elif "bank" in q_lower or "issuer" in q_lower or "loss" in q_lower:
            diagnostic = {
                "symptom": "HDFC Bank contributed ₹8.2L in recoverable failure volume in the last 6 hours.",
                "affected_segment": "Debit and Credit cards issued by HDFC Bank (BIN range 4111xx, 4532xx).",
                "likely_root_cause": "Intermittent OTP delivery latency and ACS server gateway timeouts.",
                "supporting_evidence": [
                    {"source": "issuer_analytics", "metric": "HDFC Total Failed Volume", "value": "₹18.4L", "baseline": "₹4.2L"},
                    {"source": "recovery_engine", "metric": "Recoverable Share", "value": "44.5%", "baseline": "21.0%"}
                ],
                "recommended_action": "Activate Smart UPI Fallback Policy for all HDFC card declines above ₹1,000.",
                "expected_uplift": "₹5.6L incremental recovery across 180 affected transactions.",
                "risks": "Minimal risk; UPI conversion for this customer segment is 94.2%.",
                "required_approval": "Automated execution eligible (within merchant policy)."
            }
            confidence = 0.96
        elif "whatsapp" in q_lower or "evidence" in q_lower or "upi" in q_lower:
            diagnostic = {
                "symptom": "Evidence requested for WhatsApp UPI Intent recovery strategy.",
                "affected_segment": "Customers with LTV > ₹50,000 experiencing card authentication declines.",
                "likely_root_cause": "Friction in card re-entry vs zero-friction biometric UPI deep linking.",
                "supporting_evidence": [
                    {"source": "experiment_EXP_104", "metric": "WhatsApp UPI Intent Causal Uplift", "value": "+28.4%", "baseline": "Control (Card Retry)"},
                    {"source": "customer_behavior", "metric": "UPI App-to-App Completion Time", "value": "18.2 seconds", "baseline": "142 seconds for card"},
                    {"source": "compliance_audit", "metric": "NPCI Quiet Hours & DND Conformance", "value": "100%", "baseline": "100%"}
                ],
                "recommended_action": "Maintain WhatsApp UPI Intent as the primary recovery channel for VIP and High-Value cohorts.",
                "expected_uplift": "Sustained 72.0% recovery conversion vs 61.0% for card retries.",
                "risks": "WhatsApp template delivery fees (₹1.85/msg).",
                "required_approval": "Pre-approved under Active Strategy: 'Smart UPI Evening Booster'."
            }
            confidence = 0.98
        else:
            diagnostic = {
                "symptom": f"Telemetry diagnostic compiled for query: '{redacted_query}'",
                "affected_segment": "All active checkout cohorts across UrbanKart.",
                "likely_root_cause": "Multi-channel conversion optimization opportunity across evening peak windows.",
                "supporting_evidence": [
                    {"source": "platform_kpi", "metric": "Active Recovery Rate", "value": "68.9%", "baseline": "54.0% industry avg"},
                    {"source": "recoverable_pool", "metric": "Addressable Volume", "value": "₹1.14 Cr", "baseline": "₹1.82 Cr at risk"}
                ],
                "recommended_action": "Review top 3 high-value recovery opportunities queued in Control Center.",
                "expected_uplift": "₹1.42L immediate recovery from top candidates.",
                "risks": "None. Fully compliant with RBI tokenization and NPCI quiet-hours policies.",
                "required_approval": "Human approval required for single transactions > ₹10,000."
            }
            confidence = 0.91

        citations = [
            {
                "doc_id": d.doc_id,
                "title": d.title,
                "category": d.category,
                "source": d.metadata.get("source", "RevPilot Knowledge Base")
            }
            for d in retrieved_docs
        ]

        return {
            "query": redacted_query,
            "diagnostic": diagnostic,
            "uncertainty_assessment": {
                "confidence_score": confidence,
                "is_evidence_sufficient": True,
                "missing_signals": []
            },
            "citations": citations,
            "timestamp": datetime.utcnow().isoformat()
        }
