def analyze_health(systolic, diastolic, sugar):
    # Blood Pressure Logic based on provided ranges
    if systolic >= 160 or diastolic >= 100:
        bp_status = "High: Stage 2 Hypertension"
    elif systolic >= 140 or diastolic >= 90:
        bp_status = "High: Stage 1 Hypertension"
    elif systolic >= 120 or diastolic >= 80:
        bp_status = "Pre Hypertension detected"
    elif systolic < 90 or diastolic < 60:
        bp_status = "Low blood pressure detected"
    else:
        bp_status = "Normal"

    # Sugar Logic (Kept existing as no specific range was provided for sugar)
    if sugar > 200:
        sugar_status = "Very high sugar"
    elif sugar > 140:
        sugar_status = "Elevated sugar"
    elif sugar < 70:
        sugar_status = "Low sugar"
    else:
        sugar_status = "Normal"

    # Combine results
    if bp_status == "Normal" and sugar_status == "Normal":
        return "Health normal"
    
    status_parts = []
    if bp_status != "Normal":
        status_parts.append(bp_status)
    if sugar_status != "Normal":
        status_parts.append(sugar_status)
        
    return " & ".join(status_parts)
