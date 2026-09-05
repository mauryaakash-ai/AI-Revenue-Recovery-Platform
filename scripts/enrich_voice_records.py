import sqlite3
import random
import uuid
from datetime import datetime, timedelta

def enrich_voice_data():
    conn = sqlite3.connect("revenue_recovery.db")
    cursor = conn.cursor()

    # 1. Add voice_persona and transaction_id columns if not present
    cursor.execute("PRAGMA table_info(voice_call_logs)")
    existing_cols = [row[1] for row in cursor.fetchall()]
    
    if "voice_persona" not in existing_cols:
        cursor.execute("ALTER TABLE voice_call_logs ADD COLUMN voice_persona VARCHAR(50) DEFAULT 'priya'")
        print("✓ Added column voice_persona to voice_call_logs")
        
    if "transaction_id" not in existing_cols:
        cursor.execute("ALTER TABLE voice_call_logs ADD COLUMN transaction_id VARCHAR(36)")
        print("✓ Added column transaction_id to voice_call_logs")

    # 2. Add some PENDING transactions (currently all are FAILED)
    # Update ~120 transactions to 'PENDING' with clear pending reasons
    pending_reasons = [
        ("UPI Collect Mandate Pending Customer Authorization", "upi_collect_pending", "temporary"),
        ("3DS OTP Authentication Pending Delivery", "otp_pending", "temporary"),
        ("Checkout Abandoned - Cart Awaiting Finalization", "cart_abandoned", "temporary"),
        ("Netbanking Bank Gateway Handshake In-Progress", "bank_handshake_pending", "temporary"),
        ("Mandate Auto-Debit Pre-Notification Window", "mandate_prenotification", "temporary")
    ]

    cursor.execute("SELECT id FROM transactions LIMIT 150")
    tx_ids = [row[0] for row in cursor.fetchall()]
    
    for i, tx_id in enumerate(tx_ids):
        reason, code, ftype = pending_reasons[i % len(pending_reasons)]
        cursor.execute("""
            UPDATE transactions 
            SET status = 'PENDING', failure_reason = ?, failure_code = ?, failure_type = ?
            WHERE id = ?
        """, (reason, code, ftype, tx_id))
    print(f"✓ Converted {len(tx_ids)} transactions to PENDING status with realistic pending reasons")

    # 3. Update existing voice_call_logs to point to actual playable neural audio assets
    audio_map = {
        "priya": [
            "/audio/voices/priya_payment_retry.mp3",
            "/audio/voices/priya_salary_pending.mp3",
            "/audio/voices/priya_mandate_failure.mp3",
            "/audio/voices/priya_failed_call.mp3",
            "/audio/voices/priya_pending_call.mp3"
        ],
        "rahul": [
            "/audio/voices/rahul_payment_retry.mp3",
            "/audio/voices/rahul_salary_pending.mp3",
            "/audio/voices/rahul_mandate_failure.mp3",
            "/audio/voices/rahul_failed_call.mp3",
            "/audio/voices/rahul_pending_call.mp3"
        ],
        "swara": [
            "/audio/voices/swara_payment_retry.mp3",
            "/audio/voices/swara_salary_pending.mp3",
            "/audio/voices/swara_mandate_failure.mp3",
            "/audio/voices/swara_failed_call.mp3",
            "/audio/voices/swara_pending_call.mp3"
        ],
        "madhur": [
            "/audio/voices/madhur_payment_retry.mp3",
            "/audio/voices/madhur_salary_pending.mp3",
            "/audio/voices/madhur_mandate_failure.mp3",
            "/audio/voices/madhur_failed_call.mp3",
            "/audio/voices/madhur_pending_call.mp3"
        ],
        "kavya": [
            "/audio/voices/kavya_payment_retry.mp3",
            "/audio/voices/kavya_salary_pending.mp3",
            "/audio/voices/kavya_mandate_failure.mp3",
            "/audio/voices/kavya_failed_call.mp3",
            "/audio/voices/kavya_pending_call.mp3"
        ]
    }

    personas = list(audio_map.keys())
    statuses = ["recovered", "ptp_committed", "failed_unreachable", "completed", "pending_retry"]

    cursor.execute("SELECT id FROM voice_call_logs")
    call_ids = [row[0] for row in cursor.fetchall()]

    for i, cid in enumerate(call_ids):
        persona = personas[i % len(personas)]
        audio_clip = random.choice(audio_map[persona])
        status = statuses[i % len(statuses)]
        cursor.execute("""
            UPDATE voice_call_logs
            SET audio_simulation_url = ?, voice_persona = ?, call_status = ?
            WHERE id = ?
        """, (audio_clip, persona, status, cid))
    print(f"✓ Updated {len(call_ids)} voice call logs with real neural audio paths, personas, and statuses")

    conn.commit()
    conn.close()
    print("✅ Database enrichment complete!")

if __name__ == "__main__":
    enrich_voice_data()

