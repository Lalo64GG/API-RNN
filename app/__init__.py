from flask import Flask
from app.config import Config
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mail_classifier_api")

def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(config_class)
    
      # Configurar CORS
    try:
        print("Configurando CORS...")
        from flask_cors import CORS
        CORS(app, resources={r"/*": {"origins": config_class.CORS_ORIGINS}})
        logger.info(f"CORS configurado para orígenes: {config_class.CORS_ORIGINS}")
    except Exception as e:
        logger.error(f"Error al configurar CORS: {str(e)}")

    # Importar y registrar rutas
    from app.routes import core, openai_routes
    app.register_blueprint(core.bp)
    app.register_blueprint(openai_routes.bp)
    
    # Inicializar componentes necesarios
    from app.services.model_loader import load_model_and_components
    try:
        load_model_and_components()
        logger.info("Modelo y componentes cargados exitosamente al iniciar la aplicación")
    except Exception as e:
        logger.error(f"Error al cargar el modelo al iniciar: {str(e)}")
    
    return app