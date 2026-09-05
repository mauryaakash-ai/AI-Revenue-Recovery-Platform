import os
import asyncio
import edge_tts

OUTPUT_DIR = "frontend/public/audio/voices"
os.makedirs(OUTPUT_DIR, exist_ok=True)

VOICES = {
    "priya": "en-IN-NeerjaExpressiveNeural",
    "rahul": "en-IN-PrabhatNeural",
    "swara": "hi-IN-SwaraNeural",
    "madhur": "hi-IN-MadhurNeural",
    "kavya": "mr-IN-AarohiNeural"
}

SCRIPTS = {
    # 1. Payment Retry
    "priya_payment_retry.mp3": (
        "Namaste! Main UrbanKart Priority Care desk se Priya baat kar rahi hoon. "
        "Aapka recent payment bank connectivity timeout ki wajah se hold pe tha. "
        "Aap ise one-click UPI ke through turant bina kisi hassle ke complete kar sakte hain. "
        "WhatsApp par instant payment link paane ke liye kripya keypad par 1 dabayein, ya payment schedule karne ke liye 2 dabayein.",
        VOICES["priya"]
    ),
    "rahul_payment_retry.mp3": (
        "Namaste! Main UrbanKart Accounts team se Rahul baat kar raha hoon. "
        "Aapka pending transaction instant retry ke liye ready hai. "
        "Instant UPI link ke liye keypad par 1 dabayein, ya payment schedule karne ke liye 2 dabayein.",
        VOICES["rahul"]
    ),
    "swara_payment_retry.mp3": (
        "Namaste ji! Main UrbanKart recovery desk se Swara baat kar rahi hoon. "
        "Aapka payment gateway par interrupt ho gaya tha. "
        "Agar aap WhatsApp par link chahte hain toh 1 dabayein, ya payment postpone karne ke liye 2 dabayein.",
        VOICES["swara"]
    ),
    "madhur_payment_retry.mp3": (
        "Namaste ji! Main UrbanKart priority support desk se Madhur bol raha hoon. "
        "Aapka online order payment bank timeout ki wajah se pending hai. "
        "Kripya keypad par 1 dabayein aur 1-click link se turant payment complete karein.",
        VOICES["madhur"]
    ),
    "kavya_payment_retry.mp3": (
        "Namaste! Main Kavya bol rahi hoon UrbanKart se. "
        "Aapka payment successfully recover ho sakta hai. "
        "WhatsApp payment link ke liye 1 dabayein ya Promise to Pay ke liye 2 dabayein.",
        VOICES["kavya"]
    ),

    # 2. Salary Pending
    "priya_salary_pending.mp3": (
        "Namaste ji! Main payment recovery desk se Priya bol rahi hoon. "
        "Aapka payment bank decline ki wajah se pending tha. "
        "Kya aap ise abhi settle karna chahenge ya salary aane tak schedule karein? "
        "Instant link ke liye 1 dabayein, ya agle teen din baad payment karne ke liye 2 dabayein.",
        VOICES["priya"]
    ),
    "rahul_salary_pending.mp3": (
        "Namaste ji! Main Accounts desk se Rahul baat kar raha hoon. "
        "Humein maloom hai ki salary cycle pending ho sakti hai. "
        "Aapka Promise to Pay schedule karne ke liye kripya 2 dabayein, ya abhi pay karne ke liye 1 dabayein.",
        VOICES["rahul"]
    ),
    "swara_salary_pending.mp3": (
        "Namaste! Agar salary credit pending hai toh fikar mat kijiye. "
        "Keypad par 2 dabayein aur hum aapka payment aage ke liye schedule kar denge. Dhanyawad!",
        VOICES["swara"]
    ),
    "madhur_salary_pending.mp3": (
        "Namaste ji! Madhur baat kar raha hoon. "
        "Salary pending hone par aap apna payment aage postpone kar sakte hain. "
        "Agle teen din baad payment karne ke liye keypad par 2 dabayein.",
        VOICES["madhur"]
    ),
    "kavya_salary_pending.mp3": (
        "Namaste! Kavya yahan. "
        "Salary cycle ke according apna payment commitment confirm karne ke liye kripya keypad par 2 dabayein.",
        VOICES["kavya"]
    ),

    # 3. Mandate Failure
    "priya_mandate_failure.mp3": (
        "Namaste! Aapka monthly subscription mandate auto-debit decline ho gaya hai. "
        "Apni services uninterrupted continue rakhne ke liye kripya keypad par 1 dabayein aur apna payment complete karein.",
        VOICES["priya"]
    ),
    "rahul_mandate_failure.mp3": (
        "Namaste! Rahul baat kar raha hoon. "
        "Aapka recurring mandate payment process nahi ho paya. "
        "Services active rakhne ke liye keypad par 1 dabayein aur UPI se pay karein.",
        VOICES["rahul"]
    ),
    "swara_mandate_failure.mp3": (
        "Namaste ji! Aapka mandate debit fail ho gaya tha. "
        "Service band hone se bachane ke liye kripya abhi 1 dabayein aur UPI se pay karein.",
        VOICES["swara"]
    ),
    "madhur_mandate_failure.mp3": (
        "Namaste! Madhur from subscription care. "
        "Auto-debit retry ke liye 1 dabayein aur payment turant complete karein.",
        VOICES["madhur"]
    ),
    "kavya_mandate_failure.mp3": (
        "Namaste! Subscription auto-debit pending hai. "
        "1-click payment link paane ke liye keypad par 1 dabayein.",
        VOICES["kavya"]
    ),

    # 4. Failed Call
    "priya_failed_call.mp3": (
        "Namaste! Main Priya baat kar rahi hoon. "
        "Aapka transaction bank network error ki wajah se fail ho gaya tha. "
        "Humne transaction safely pause kar diya hai. Instant secure retry ke liye keypad par 1 dabayein.",
        VOICES["priya"]
    ),
    "rahul_failed_call.mp3": (
        "Namaste! Rahul from Recovery team. "
        "Aapka payment fail hua tha par aapke paise safe hain. "
        "Quick retry link ke liye keypad par 1 dabayein.",
        VOICES["rahul"]
    ),
    "swara_failed_call.mp3": (
        "Namaste ji! Aapka transaction fail ho gaya tha. "
        "Kya main aapko WhatsApp par alternate payment link bhej doon? Kripya 1 dabayein.",
        VOICES["swara"]
    ),
    "madhur_failed_call.mp3": (
        "Namaste! Madhur bol raha hoon. "
        "Failed transaction ko UPI ya card se retry karne ke liye keypad par 1 dabayein.",
        VOICES["madhur"]
    ),
    "kavya_failed_call.mp3": (
        "Namaste! Transaction failure solve karne ke liye hum aapki help karenge. "
        "Instant link ke liye keypad par 1 dabayein.",
        VOICES["kavya"]
    ),

    # 5. Pending Call
    "priya_pending_call.mp3": (
        "Namaste! Main Priya baat kar rahi hoon. "
        "Aapka payment verification stage par pending hai. "
        "Ise bina double charge ke confirm karne ke liye keypad par 1 dabayein.",
        VOICES["priya"]
    ),
    "rahul_pending_call.mp3": (
        "Namaste! Rahul yahan. "
        "Aapka pending order payment complete karne ke liye instant link WhatsApp par ready hai. "
        "Keypad par 1 dabayein.",
        VOICES["rahul"]
    ),
    "swara_pending_call.mp3": (
        "Namaste ji! Pending transaction ko safely complete karne ke liye kripya keypad par 1 dabayein.",
        VOICES["swara"]
    ),
    "madhur_pending_call.mp3": (
        "Namaste! Madhur bol raha hoon. "
        "Pending payment clear karne ke liye keypad par 1 dabayein.",
        VOICES["madhur"]
    ),
    "kavya_pending_call.mp3": (
        "Namaste! Aapka pending checkout complete karne ke liye keypad par 1 dabayein.",
        VOICES["kavya"]
    ),

    # 6. DTMF Acknowledgements
    "dtmf_key1_ack_female.mp3": (
        "Bahut bahut dhanyawad! Humne aapke WhatsApp aur SMS par secure one-click UPI link bhej diya hai. "
        "Kripya apna message check karein aur payment complete karein. Have a wonderful day!",
        VOICES["priya"]
    ),
    "dtmf_key1_ack_male.mp3": (
        "Thank you very much! Aapke mobile par instant 1-click payment link send kar diya gaya hai. "
        "Kripya link open karke payment complete karein. Aapka din shubh ho!",
        VOICES["rahul"]
    ),
    "dtmf_key2_ack_female.mp3": (
        "Aapka Promise-to-Pay confirmation register ho gaya hai. "
        "Hum aapko scheduled date par reminder bhej denge. UrbanKart par vishwas rakhne ke liye dhanyawad!",
        VOICES["priya"]
    ),
    "dtmf_key2_ack_male.mp3": (
        "Aapka Promise-to-Pay commitment successfully record ho gaya hai. "
        "Hum aapko scheduled date par morning mein reminder send karenge. Thank you and have a great day!",
        VOICES["rahul"]
    ),
}

async def generate_file(filename, text, voice):
    filepath = os.path.join(OUTPUT_DIR, filename)
    print(f"Generating {filename} with voice {voice}...")
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filepath)
    size_kb = os.path.getsize(filepath) / 1024
    print(f"✓ Created {filename} ({size_kb:.1f} KB)")

async def main():
    tasks = []
    for filename, (text, voice) in SCRIPTS.items():
        tasks.append(generate_file(filename, text, voice))
    await asyncio.gather(*tasks)
    print(f"\n🎉 Successfully generated all {len(SCRIPTS)} studio neural audio files in {OUTPUT_DIR}!")

if __name__ == "__main__":
    asyncio.run(main())

