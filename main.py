import time
import os
from extractor import extract_text_from_pdf, parse_ad_rules
from evaluator import evaluate_aircraft

# Masukkan API Key Anda di sini
API_KEY = "YOUR_API_KEY_HERE"

test_fleet = [
    {"model": "MD-11F", "msn": "48400", "modifications": ["None"]},
    {"model": "A320-214", "msn": "4500", "modifications": ["mod 24591 (production)"]},
    {"model": "A320-214", "msn": "4500", "modifications": ["None"]}
]

def main():
    if not os.path.exists("FAA-2025-23-53.pdf") or not os.path.exists("EASA-2025-0254.pdf"):
        print("ERROR: File PDF tidak ditemukan.")
        return

    print("Mengekstrak FAA AD...")
    faa_text = extract_text_from_pdf("FAA-2025-23-53.pdf")
    faa_rules = parse_ad_rules(faa_text, API_KEY)
    
    # Tambahkan jeda 20 detik agar tidak terkena rate limit
    print("Menunggu sebentar untuk kuota API...")
    time.sleep(20) 
    
    print("Mengekstrak EASA AD...")
    easa_text = extract_text_from_pdf("EASA-2025-0254.pdf")
    easa_rules = parse_ad_rules(easa_text, API_KEY)
    
    print("\n" + "="*50)
    print("              HASIL EVALUASI PESAWAT              ")
    print("="*50 + "\n")
    
    for aircraft in test_fleet:
        print(f"Pesawat: {aircraft['model']} | MSN: {aircraft['msn']} | Mods: {aircraft['modifications'][0]}")
        
        faa_status = evaluate_aircraft(aircraft, faa_rules)
        print(f"--> Status FAA AD 2025-23-53 : {faa_status}")
        
        easa_status = evaluate_aircraft(aircraft, easa_rules)
        print(f"--> Status EASA AD 2025-0254 : {easa_status}")
        print("-" * 50)

if __name__ == "__main__":
    main()