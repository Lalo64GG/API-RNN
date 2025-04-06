"""
Rutas de la API relacionadas con la generación de texto con OpenAI.
"""

from flask import Blueprint, request, jsonify, current_app
import logging
from app.services.openai_generator import get_generator
from app.services.classifier import classify_email

# Configurar logging
logger = logging.getLogger("mail_classifier_api.routes.openai")

# Crear blueprint
bp = Blueprint('openai', __name__, url_prefix='/openai')

@bp.route("/status", methods=["GET"])
def openai_status():
    """Verifica el estado de la conexión con OpenAI"""
    generator = get_generator()
    has_api_key = generator.api_key is not None and len(generator.api_key) > 0
    
    return jsonify({
        "status": "ready" if has_api_key else "unavailable",
        "api_key_configured": has_api_key,
        "model": generator.model
    })

@bp.route("/analyze", methods=["POST"])
def analyze_email():
    """
    Analiza un correo electrónico, lo clasifica y genera una respuesta detallada
    usando el modelo de OpenAI.
    """
    try:
        email = request.get_json()
        if not email or "subject" not in email or "body" not in email:
            return jsonify({"error": "Se requieren los campos 'subject' y 'body'"}), 400
            
        # Primero clasificamos el correo
        subject = email["subject"]
        body = email["body"]
        
        classification = classify_email(subject, body)
        email_class = classification["predicted_class"]
        confidence = classification["confidence"]
        
        # Generamos la respuesta con OpenAI
        generator = get_generator()
        response = generator.generate_security_response(email_class, confidence)
        
        # Devolvemos la clasificación y el análisis
        return jsonify({
            "classification": classification,
            "analysis": response,
            "email": {
                "subject": subject,
                "body_preview": body[:100] + "..." if len(body) > 100 else body
            }
        })
    except Exception as e:
        logger.error(f"Error en endpoint /openai/analyze: {str(e)}")
        return jsonify({"error": f"Error al analizar el correo: {str(e)}"}), 500

@bp.route("/generate-response", methods=["POST"])
def generate_response():
    """
    Genera una respuesta detallada para un tipo específico de correo malicioso
    sin necesidad de clasificar un correo específico.
    """
    try:
        data = request.get_json()
        if not data or "email_class" not in data:
            return jsonify({"error": "Se requiere el campo 'email_class'"}), 400
            
        email_class = data["email_class"]
        confidence = data.get("confidence", 0.9)  # Valor por defecto alto
        
        # Validamos la confianza
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
            return jsonify({"error": "El campo 'confidence' debe ser un número entre 0 y 1"}), 400
            
        # Generamos la respuesta
        generator = get_generator()
        response = generator.generate_security_response(email_class, confidence)
        
        return jsonify({
            "email_class": email_class,
            "confidence": confidence,
            "analysis": response
        })
    except Exception as e:
        logger.error(f"Error en endpoint /openai/generate-response: {str(e)}")
        return jsonify({"error": f"Error al generar respuesta: {str(e)}"}), 500

@bp.route("/set-model", methods=["POST"])
def set_model():
    """Cambia el modelo de OpenAI utilizado"""
    try:
        data = request.get_json()
        if not data or "model" not in data:
            return jsonify({"error": "Se requiere el campo 'model'"}), 400
            
        model_name = data["model"]
        
        # Cambiamos el modelo
        generator = get_generator()
        generator.set_model(model_name)
        
        return jsonify({
            "status": "success",
            "message": f"Modelo cambiado a: {model_name}",
            "current_model": generator.model
        })
    except Exception as e:
        logger.error(f"Error en endpoint /openai/set-model: {str(e)}")
        return jsonify({"error": f"Error al cambiar el modelo: {str(e)}"}), 500

@bp.route("/clear-cache", methods=["POST"])
def clear_cache():
    """Limpia la caché de respuestas de OpenAI"""
    try:
        generator = get_generator()
        generator.clear_cache()
        
        return jsonify({
            "status": "success",
            "message": "Caché de respuestas limpiada correctamente"
        })
    except Exception as e:
        logger.error(f"Error en endpoint /openai/clear-cache: {str(e)}")
        return jsonify({"error": f"Error al limpiar la caché: {str(e)}"}), 500