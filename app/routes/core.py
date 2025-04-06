from flask import Blueprint, request, jsonify
import logging
from app.services.classifier import classify_email
from app.services.model_loader import get_model, get_class_mapping

# Configurar logging
logger = logging.getLogger("mail_classifier_api.routes.core")

# Crear blueprint
bp = Blueprint('core', __name__)

@bp.route("/", methods=["GET"])
def read_root():
    """Endpoint raíz para verificar que la API está funcionando"""
    return jsonify({
        "status": "online", 
        "message": "API de Clasificación de Correos Maliciosos",
        "version": "2.0"
    })

@bp.route("/health", methods=["GET"])
def health_check():
    """Endpoint para verificar la salud del servicio"""
    model_loaded = get_model() is not None
    return jsonify({
        "status": "healthy" if model_loaded else "degraded",
        "model_loaded": model_loaded
    })

@bp.route("/predict", methods=["POST"])
def predict_email():
    """Endpoint para clasificar un correo electrónico"""
    try:
        email = request.get_json()
        if not email or "subject" not in email or "body" not in email:
            return jsonify({"error": "Se requieren los campos 'subject' y 'body'"}), 400
            
        subject = email["subject"]
        body = email["body"]

        result = classify_email(subject, body)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error en endpoint /predict: {str(e)}")
        return jsonify({"error": f"Error al procesar la solicitud: {str(e)}"}), 500

@bp.route("/batch-predict", methods=["POST"])
def batch_predict():
    """Endpoint para clasificar múltiples correos electrónicos"""
    try:
        emails = request.get_json()
        if not isinstance(emails, list):
            return jsonify({"error": "Se espera una lista de correos"}), 400
            
        results = []
        for email in emails:
            if "subject" not in email or "body" not in email:
                continue  # Omitir correos sin los campos requeridos
                
            subject = email["subject"]
            body = email["body"]
            result = classify_email(subject, body)
            results.append({
                "id": email.get("id", None),  # Opcional para seguimiento del cliente
                "subject": subject[:50] + "..." if len(subject) > 50 else subject,
                "prediction": result
            })
        
        return jsonify({
            "results": results, 
            "count": len(results),
            "processed": len(results),
            "total": len(emails)
        })
    except Exception as e:
        logger.error(f"Error en endpoint /batch-predict: {str(e)}")
        return jsonify({"error": f"Error al procesar la solicitud por lotes: {str(e)}"}), 500

@bp.route("/classes", methods=["GET"])
def get_classes():
    """Endpoint para obtener las clases disponibles"""
    try:
        class_mapping = get_class_mapping()
        if not class_mapping:
            return jsonify({"error": "Información de clases no disponible"}), 503
            
        return jsonify({
            "classes": list(class_mapping.keys()), 
            "total": len(class_mapping),
            "mapping": class_mapping
        })
    except Exception as e:
        logger.error(f"Error en endpoint /classes: {str(e)}")
        return jsonify({"error": f"Error al obtener clases: {str(e)}"}), 500