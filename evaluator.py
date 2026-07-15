def check_msn_in_constraints(msn: str, constraints: list) -> bool:
    """Mengecek apakah nomor seri pesawat (MSN) masuk dalam daftar batasan AD."""
    if not constraints:
        return True # Jika tidak ada batasan MSN, berarti berlaku untuk semua MSN
    
    try:
        msn_int = int(msn)
    except ValueError:
        return msn in constraints

    for constraint in constraints:
        if "-" in constraint: 
            try:
                start, end = map(int, constraint.split("-"))
                if start <= msn_int <= end:
                    return True
            except ValueError:
                pass
        elif constraint.strip() == str(msn):
            return True
            
    return False

def evaluate_aircraft(aircraft: dict, ad_rules_json: dict) -> str:
    """
    Menentukan status pesawat berdasarkan JSON hasil ekstraksi.
    Kembalian yang diharapkan: "Affected", "Not affected", atau "Not applicable"
    """
    rules = ad_rules_json["applicability_rules"]
    
    # 1. Cek Kesesuaian Model Pesawat
    if aircraft["model"] not in rules["aircraft_models"]:
        return "Not applicable"
        
    # 2. Cek Modifikasi Pengecualian (Exclusions)
    # Jika pesawat memiliki mod yang membebaskannya dari AD ini
    if rules["excluded_if_modifications"]:
        for mod in aircraft["modifications"]:
            if mod in rules["excluded_if_modifications"]:
                return "Not affected"
                
    # 3. Cek Syarat MSN
    if rules["msn_constraints"] is not None:
        if not check_msn_in_constraints(str(aircraft["msn"]), rules["msn_constraints"]):
            return "Not applicable"
            
    # 4. Cek Syarat Modifikasi Inklusi
    # Jika AD HANYA berlaku untuk pesawat dengan modifikasi tertentu
    if rules["required_modifications"]:
        has_required = any(mod in rules["required_modifications"] for mod in aircraft["modifications"])
        if not has_required:
            return "Not applicable"

    # Jika semua pemeriksaan lolos, pesawat terkena dampak
    return "Affected"