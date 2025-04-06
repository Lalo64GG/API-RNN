"""
Script de diagnóstico para la API de clasificación de correos maliciosos.
Usado para identificar problemas de inicialización.
"""

import logging
import traceback
import sys
from app import create_app
from app.config import Config

# Configurar logging más detallado
logging.basicConfig(
    level=logging.DEBUG,  
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout) 
    ]
)
logger = logging.getLogger("mail_classifier_api_debug")

try:
    logger.info("Iniciando creación de la aplicación...")
    app = create_app()
    logger.info("Aplicación creada correctamente")
    
    logger.info(f"Configurado para iniciar en {Config.HOST}:{Config.FLASK_PORT}")
    logger.info(f"Modo DEBUG: {Config.DEBUG_MODE}")
    
    logger.info("Iniciando servidor Flask...")
    app.run(
        host=Config.HOST,
        port=Config.FLASK_PORT,
        debug=True, 
        use_reloader=False  
    )
except Exception as e:
    logger.error("ERROR AL INICIAR LA APLICACIÓN:")
    logger.error(str(e))
    logger.error(traceback.format_exc())
    
    logger.info("Información de diagnóstico:")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Host configurado: {Config.HOST}")
    logger.info(f"Puerto configurado: {Config.FLASK_PORT}")
    
    logger.info("Presiona Ctrl+C para salir...")
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Saliendo del modo de diagnóstico.")