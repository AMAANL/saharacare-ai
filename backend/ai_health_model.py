def analyze_health(systolic, diastolic, sugar):
    if systolic > 180 or diastolic > 120:
        return "Hypertensive crisis detected"

    if systolic > 150 or diastolic > 90:
        return "High blood pressure detected"

    if systolic < 90 or diastolic < 60:
        return "Low blood pressure detected"

    if sugar > 200:
        return "Very high blood sugar detected"

    if sugar > 140:
        return "Elevated blood sugar"

    if sugar < 70:
        return "Low blood sugar detected"

    return "Health normal"
