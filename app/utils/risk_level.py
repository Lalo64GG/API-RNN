def determine_risk_level(class_name: str, confidence: float) -> str:

    # Clases de alto riesgo que requieren acción inmediata
    high_risk_classes = [
        "CEO_FRAUD", "MALWARE_ADJUNTO", "PHISHING_BANCARIO",
        "SEXTORSION", "PHISHING_CREDENCIALES"
    ]

    # Clases de riesgo medio que requieren precaución
    medium_risk_classes = [
        "PHARMING", "FRAUDE_SOPORTE", "VISHING", "SMISHING"
    ]
    
    # Si es un correo legítimo, siempre es de riesgo bajo
    if class_name == "NO_MALICIOSO":
        return "BAJO"

    # Determinamos el nivel de riesgo basado en la clase y confianza
    if class_name in high_risk_classes:
        if confidence > 0.8:
            return "CRÍTICO"
        else:
            return "ALTO"
    elif class_name in medium_risk_classes:
        if confidence > 0.8:
            return "ALTO"
        else:
            return "MEDIO"
    else:
        if confidence > 0.9:
            return "MEDIO"
        else:
            return "BAJO"