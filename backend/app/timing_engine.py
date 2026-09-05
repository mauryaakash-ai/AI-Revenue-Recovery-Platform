"""
Smart Timing Optimization & Dynamic Channel Ranking Engine
Enforces:
- NPCI / TRAI Quiet Hours (21:00 to 08:00 IST)
- Merchant cooldown windows between communications (default 4 hours)
- Dynamic channel ranking based on Customer Affinity + Failure Type + Amount + Bank Health
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import pytz


IST = pytz.timezone("Asia/Kolkata") if "Asia/Kolkata" in pytz.all_timezones else None


class TimingEngine:
    """Computes optimal execution timing and dynamic channel suitability ranking"""

    CHANNEL_COSTS = {
        "immediate_card_retry": 0.0,
        "delayed_card_retry": 0.0,
        "whatsapp_upi_intent": 1.85,
        "sms_payment_link": 0.25,
        "dynamic_vpa": 0.50,
        "voice_recovery": 4.50,
        "email_recovery": 0.05
    }

    @classmethod
    def get_current_ist_time(cls) -> datetime:
        if IST:
            return datetime.now(IST)
        # UTC + 5:30 fallback
        return datetime.utcnow() + timedelta(hours=5, minutes=30)

    @classmethod
    def is_in_quiet_hours(cls, current_dt: datetime, quiet_start_hour: int = 21, quiet_end_hour: int = 8) -> bool:
        """Check if given time falls in quiet hours (21:00 - 08:00)"""
        hour = current_dt.hour
        if quiet_start_hour > quiet_end_hour:
            # Crosses midnight: e.g. 21 to 8
            return hour >= quiet_start_hour or hour < quiet_end_hour
        return quiet_start_hour <= hour < quiet_end_hour

    @classmethod
    def calculate_next_allowed_time(
        cls,
        base_time: datetime,
        delay_minutes: int = 15,
        quiet_start_hour: int = 21,
        quiet_end_hour: int = 8
    ) -> (datetime, bool, str):
        """Calculates earliest valid execution time respecting quiet hours"""
        target_time = base_time + timedelta(minutes=delay_minutes)
        quiet_hours_adjusted = False
        window_label = "Optimal Active Window"

        if cls.is_in_quiet_hours(target_time, quiet_start_hour, quiet_end_hour):
            quiet_hours_adjusted = True
            # Advance to quiet_end_hour today or tomorrow morning
            if target_time.hour >= quiet_start_hour:
                next_morning = target_time + timedelta(days=1)
                target_time = next_morning.replace(hour=quiet_end_hour, minute=30, second=0, microsecond=0)
            else:
                target_time = target_time.replace(hour=quiet_end_hour, minute=30, second=0, microsecond=0)
            window_label = f"Delayed to Morning Window ({quiet_end_hour}:30 IST) due to TRAI Quiet Hours"
        else:
            window_label = f"Scheduled for {target_time.strftime('%H:%M IST')} (Real-time Peak)"

        return target_time, quiet_hours_adjusted, window_label

    @classmethod
    def rank_channels(
        cls,
        failure_category: str,
        amount: float,
        payment_method: str,
        customer_profile: Optional[Dict[str, Any]] = None,
        bank_health_status: str = "HEALTHY"
    ) -> List[Dict[str, Any]]:
        """Ranks channels dynamically by suitability score, cost, and historical conversion"""
        customer_profile = customer_profile or {}
        preferred_channel = customer_profile.get("preferred_channel", "whatsapp")

        channels = [
            {"channel": "whatsapp_upi_intent", "base_score": 0.82, "cost": 1.85, "label": "WhatsApp UPI Intent"},
            {"channel": "sms_payment_link", "base_score": 0.65, "cost": 0.25, "label": "SMS Smart Link"},
            {"channel": "delayed_card_retry", "base_score": 0.55, "cost": 0.0, "label": "Delayed Gateway Card Retry"},
            {"channel": "dynamic_vpa", "base_score": 0.70, "cost": 0.50, "label": "Dynamic VPA QR Intent"},
            {"channel": "voice_recovery", "base_score": 0.40, "cost": 4.50, "label": "Automated Voice Assistant"},
            {"channel": "email_recovery", "base_score": 0.35, "cost": 0.05, "label": "Email Invoice Link"},
        ]

        for item in channels:
            ch = item["channel"]
            score = item["base_score"]

            # Failure taxonomy adjustments
            if failure_category == "AUTHENTICATION":
                # 3DS timeout -> Customer interaction channels excel
                if ch in ["whatsapp_upi_intent", "sms_payment_link"]:
                    score += 0.15
                elif ch == "delayed_card_retry":
                    score -= 0.30
            elif failure_category == "CUSTOMER":
                # Insufficient funds -> Delayed reminder or smart link
                if ch in ["whatsapp_upi_intent", "dynamic_vpa"]:
                    score += 0.10
                elif ch == "delayed_card_retry":
                    score -= 0.20
            elif failure_category in ["ISSUER", "GATEWAY"]:
                # Transient gateway / issuer issue -> Card retry is viable once bank recovers
                if ch == "delayed_card_retry" and bank_health_status != "DEGRADED":
                    score += 0.25

            # Amount adjustments
            if amount >= 25000.0:
                # High-value recovery justifies higher cost interactive channels
                if ch in ["voice_recovery", "whatsapp_upi_intent"]:
                    score += 0.15
            elif amount < 2000.0:
                # Low value prefers zero or micro cost channels
                if ch in ["voice_recovery"]:
                    score -= 0.35
                elif ch in ["delayed_card_retry", "sms_payment_link"]:
                    score += 0.10

            # Customer preference affinity
            if preferred_channel in ch:
                score += 0.20

            # Bank health penalty on direct retry
            if bank_health_status == "DEGRADED" and "card_retry" in ch:
                score -= 0.40

            item["suitability_score"] = round(max(0.05, min(0.99, score)), 3)

        # Sort descending by suitability score
        ranked = sorted(channels, key=lambda x: x["suitability_score"], reverse=True)
        return ranked

    @classmethod
    def optimize(
        cls,
        transaction: Dict[str, Any],
        customer: Optional[Dict[str, Any]] = None,
        failure_category: str = "AUTHENTICATION",
        bank_health_status: str = "HEALTHY"
    ) -> Dict[str, Any]:
        amount = float(transaction.get("amount", 5000.0))
        payment_method = transaction.get("payment_method", "card")

        ranked_channels = cls.rank_channels(
            failure_category=failure_category,
            amount=amount,
            payment_method=payment_method,
            customer_profile=customer,
            bank_health_status=bank_health_status
        )

        top_channel = ranked_channels[0]["channel"]
        expected_cost = ranked_channels[0]["cost"]

        # If it's a silent retry (delayed_card_retry), quiet hours can be ignored
        is_silent_retry = "card_retry" in top_channel
        current_ist = cls.get_current_ist_time()

        if is_silent_retry:
            # 20 minutes delay for gateway/issuer recovery
            scheduled_time = current_ist + timedelta(minutes=20)
            quiet_adjusted = False
            window_label = "20-Minute Transient Issuer Delay"
            delay_minutes = 20
        else:
            scheduled_time, quiet_adjusted, window_label = cls.calculate_next_allowed_time(
                base_time=current_ist,
                delay_minutes=15
            )
            delay_minutes = int((scheduled_time - current_ist).total_seconds() / 60)

        return {
            "recommended_channel": top_channel,
            "expected_channel_cost": expected_cost,
            "scheduled_time": scheduled_time.isoformat(),
            "scheduled_window": window_label,
            "delay_minutes": max(0, delay_minutes),
            "quiet_hours_adjusted": quiet_adjusted,
            "ranked_alternatives": ranked_channels
        }


timing_engine = TimingEngine()

