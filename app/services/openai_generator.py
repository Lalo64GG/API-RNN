import logging
from flask import current_app
from openai_response_generator import OpenAIResponseGenerator

# Configurar logging
logger = logging.getLogger("mail_classifier_api.services.openai_generator")

# Variable global para la instancia del generador
_generator = None

def get_generator():
    """
    Devuelve una instancia del generador de respuestas de OpenAI.
    Se asegura de que solo exista una instancia en toda la aplicación.
    
    Returns:
        Instancia de OpenAIResponseGenerator
    """
    global _generator
    
    if _generator is None:
        # Creamos una nueva instancia
        _generator = OpenAIResponseGenerator()
        
        # Configuramos el modelo desde las variables de la aplicación
        from app.config import Config
        if Config.OPENAI_MODEL:
            _generator.set_model(Config.OPENAI_MODEL)
            
        logger.info(f"Generador de respuestas OpenAI inicializado con modelo: {_generator.model}")
        
        # Verificamos la API key
        if not _generator.api_key:
            logger.warning("No se encontró OPENAI_API_KEY. Las respuestas utilizarán el modo de fallback.")
    
    return _generator

def generate_security_analysis(email_class: str, confidence: float = 0.9) -> dict:
    """
    Genera un análisis de seguridad para un tipo específico de correo malicioso.
    
    Args:
        email_class: Tipo de correo malicioso
        confidence: Nivel de confianza (0-1)
        
    Returns:
        Diccionario con el análisis y metadatos
    """
    try:
        generator = get_generator()
        response = generator.generate_security_response(email_class, confidence)
        
        return {
            "email_class": email_class,
            "confidence": confidence,
            "analysis": response,
            "generated_by": generator.model,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error al generar análisis de seguridad: {str(e)}")
        return {
            "email_class": email_class,
            "confidence": confidence,
            "error": f"Error al generar análisis: {str(e)}",
            "status": "error"
        }