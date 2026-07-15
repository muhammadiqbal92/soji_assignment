def check_msn_in_constraints(msn: str, constraints: list) -> bool:
    """Checks whether the aircraft serial number (MSN) falls within the AD constraint list."""
    if not constraints:
        return True # If there are no MSN constraints, it applies to all MSNs
    
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
    Determines aircraft status based on extracted JSON.
    Expected returns: "Affected", "Not affected", or "Not applicable"
    """
    rules = ad_rules_json["applicability_rules"]
    
    # 1. Check aircraft model match
    if aircraft["model"] not in rules["aircraft_models"]:
        return "Not applicable"
        
    # 2. Check exclusion modifications
    # If the aircraft has a mod that exempts it from this AD
    if rules["excluded_if_modifications"]:
        for mod in aircraft["modifications"]:
            if mod in rules["excluded_if_modifications"]:
                return "Not affected"
                
    # 3. Check MSN requirements
    if rules["msn_constraints"] is not None:
        if not check_msn_in_constraints(str(aircraft["msn"]), rules["msn_constraints"]):
            return "Not applicable"
            
    # 4. Check required modification inclusions
    # If the AD ONLY applies to aircraft with specific modifications
    if rules["required_modifications"]:
        has_required = any(mod in rules["required_modifications"] for mod in aircraft["modifications"])
        if not has_required:
            return "Not applicable"

    # If all checks pass, the aircraft is affected
    return "Affected"