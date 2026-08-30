"""
Payment provider abstraction layer.
Supports MockProvider (synthetic) and RazorpayProvider (test mode).
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, List
import uuid
import random
from datetime import datetime, timedelta


class PaymentProvider(ABC):
    """Abstract base class for payment providers"""
    
    @abstractmethod
    def get_payments(self, limit: int = 100, offset: int = 0) -> Dict:
        """Get list of payments"""
        pass
    
    @abstractmethod
    def get_payment(self, payment_id: str) -> Dict:
        """Get a specific payment"""
        pass
    
    @abstractmethod
    def create_payment_link(self, amount: float, customer_email: str, description: str) -> Dict:
        """Create a payment link for recovery"""
        pass
    
    @abstractmethod
    def get_refunds(self, limit: int = 100, offset: int = 0) -> Dict:
        """Get list of refunds"""
        pass
    
    @abstractmethod
    def refund_payment(self, payment_id: str, amount: float, reason: str) -> Dict:
        """Issue a refund"""
        pass
    
    @abstractmethod
    def get_settlements(self, limit: int = 100, offset: int = 0) -> Dict:
        """Get settlement records"""
        pass
    
    @abstractmethod
    def create_payout(self, account_number: str, amount: float, description: str) -> Dict:
        """Create a payout"""
        pass


class MockProvider(PaymentProvider):
    """Mock payment provider for testing and demo"""
    
    def __init__(self):
        self.name = "mock"
        self.payments = {}
        self.refunds = {}
        self.settlements = {}
    
    def get_payments(self, limit: int = 100, offset: int = 0) -> Dict:
        """Return mock payments"""
        return {
            "provider": self.name,
            "count": 0,
            "payments": [],
            "note": "Mock provider returns empty list"
        }
    
    def get_payment(self, payment_id: str) -> Dict:
        """Get mock payment"""
        if payment_id in self.payments:
            return self.payments[payment_id]
        
        return {
            "provider": self.name,
            "payment_id": payment_id,
            "status": "mock",
            "amount": 0.0,
            "note": "Mock payment"
        }
    
    def create_payment_link(self, amount: float, customer_email: str, description: str) -> Dict:
        """Create mock payment link"""
        link_id = str(uuid.uuid4())
        short_url = f"rzp.io/{link_id[:8]}"
        
        return {
            "provider": self.name,
            "link_id": link_id,
            "short_url": short_url,
            "amount": float(amount),
            "customer_email": customer_email,
            "description": description,
            "status": "created",
            "created_at": datetime.utcnow().isoformat(),
            "note": "Mock payment link created. This is a test link and will not process real payments."
        }
    
    def get_refunds(self, limit: int = 100, offset: int = 0) -> Dict:
        """Return mock refunds"""
        return {
            "provider": self.name,
            "count": 0,
            "refunds": [],
            "note": "Mock provider returns empty list"
        }
    
    def refund_payment(self, payment_id: str, amount: float, reason: str) -> Dict:
        """Mock refund"""
        refund_id = str(uuid.uuid4())
        
        return {
            "provider": self.name,
            "refund_id": refund_id,
            "payment_id": payment_id,
            "amount": float(amount),
            "reason": reason,
            "status": "mock_processed",
            "created_at": datetime.utcnow().isoformat(),
            "note": "Mock refund. No actual funds processed."
        }
    
    def get_settlements(self, limit: int = 100, offset: int = 0) -> Dict:
        """Return mock settlements"""
        return {
            "provider": self.name,
            "count": 0,
            "settlements": [],
            "note": "Mock provider returns empty list"
        }
    
    def create_payout(self, account_number: str, amount: float, description: str) -> Dict:
        """Mock payout"""
        payout_id = str(uuid.uuid4())
        
        return {
            "provider": self.name,
            "payout_id": payout_id,
            "account_number": account_number[-4:],  # Redact
            "amount": float(amount),
            "description": description,
            "status": "mock_queued",
            "created_at": datetime.utcnow().isoformat(),
            "note": "Mock payout. No actual funds transferred."
        }


class RazorpayProvider(PaymentProvider):
    """Razorpay provider for test mode"""
    
    def __init__(self, api_key: str, api_secret: str):
        self.name = "razorpay"
        self.api_key = api_key
        self.api_secret = api_secret
        # In production, initialize with: import razorpay; self.client = razorpay.Client(auth=(api_key, api_secret))
        # For now, this is a stub that returns mock responses
        self.client = None
    
    def get_payments(self, limit: int = 100, offset: int = 0) -> Dict:
        """Get payments from Razorpay test API"""
        # In production:
        # response = self.client.payment.all({"count": limit, "skip": offset})
        # return response
        
        return {
            "provider": self.name,
            "count": 0,
            "payments": [],
            "note": "Razorpay test mode. Configure API key to fetch real test payments."
        }
    
    def get_payment(self, payment_id: str) -> Dict:
        """Get a payment from Razorpay"""
        # In production:
        # response = self.client.payment.fetch(payment_id)
        # return response
        
        return {
            "provider": self.name,
            "payment_id": payment_id,
            "status": "test_mode",
            "note": "Razorpay test mode. Configure API key to fetch real test payments."
        }
    
    def create_payment_link(self, amount: float, customer_email: str, description: str) -> Dict:
        """Create a payment link via Razorpay"""
        link_id = str(uuid.uuid4())
        short_url = f"rzp.io/{link_id[:8]}"
        
        # In production:
        # payload = {"amount": int(amount * 100), "currency": "INR", "email": customer_email, "description": description}
        # response = self.client.invoice.create(payload)
        
        return {
            "provider": self.name,
            "link_id": link_id,
            "short_url": short_url,
            "amount": float(amount),
            "customer_email": customer_email,
            "description": description,
            "status": "created",
            "created_at": datetime.utcnow().isoformat(),
            "note": "Razorpay test mode. Configure API key for real test mode links."
        }
    
    def get_refunds(self, limit: int = 100, offset: int = 0) -> Dict:
        """Get refunds from Razorpay"""
        # In production:
        # response = self.client.refund.all({"count": limit, "skip": offset})
        # return response
        
        return {
            "provider": self.name,
            "count": 0,
            "refunds": [],
            "note": "Razorpay test mode"
        }
    
    def refund_payment(self, payment_id: str, amount: float, reason: str) -> Dict:
        """Refund a payment via Razorpay"""
        refund_id = str(uuid.uuid4())
        
        # In production:
        # response = self.client.payment.refund(payment_id, {"amount": int(amount * 100)})
        
        return {
            "provider": self.name,
            "refund_id": refund_id,
            "payment_id": payment_id,
            "amount": float(amount),
            "reason": reason,
            "status": "processed",
            "created_at": datetime.utcnow().isoformat(),
            "note": "Razorpay test mode"
        }
    
    def get_settlements(self, limit: int = 100, offset: int = 0) -> Dict:
        """Get settlements from Razorpay"""
        # In production:
        # response = self.client.settlement.all({"count": limit, "skip": offset})
        # return response
        
        return {
            "provider": self.name,
            "count": 0,
            "settlements": [],
            "note": "Razorpay test mode"
        }
    
    def create_payout(self, account_number: str, amount: float, description: str) -> Dict:
        """Create a payout via Razorpay"""
        payout_id = str(uuid.uuid4())
        
        # In production:
        # payload = {"account_number": account_number, "amount": int(amount * 100), "currency": "INR", "mode": "NEFT"}
        # response = self.client.payout.create(payload)
        
        return {
            "provider": self.name,
            "payout_id": payout_id,
            "account_number": account_number[-4:],  # Redact
            "amount": float(amount),
            "description": description,
            "status": "queued",
            "created_at": datetime.utcnow().isoformat(),
            "note": "Razorpay test mode"
        }


class ProviderFactory:
    """Factory for creating payment provider instances"""
    
    _providers = {
        "mock": MockProvider,
        "razorpay": RazorpayProvider,
    }
    
    @staticmethod
    def create(provider_name: str, **kwargs) -> PaymentProvider:
        """Create a payment provider instance"""
        if provider_name not in ProviderFactory._providers:
            raise ValueError(f"Unknown provider: {provider_name}. Available: {list(ProviderFactory._providers.keys())}")
        
        provider_class = ProviderFactory._providers[provider_name]
        
        if provider_name == "mock":
            return provider_class()
        elif provider_name == "razorpay":
            api_key = kwargs.get("api_key")
            api_secret = kwargs.get("api_secret")
            if not api_key or not api_secret:
                raise ValueError("Razorpay provider requires api_key and api_secret")
            return provider_class(api_key, api_secret)
        else:
            return provider_class()
    
    @staticmethod
    def get_default_provider() -> PaymentProvider:
        """Get the default provider (mock)"""
        return ProviderFactory.create("mock")
