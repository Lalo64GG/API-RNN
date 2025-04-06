"""
Funciones para cargar y gestionar el modelo de clasificación y sus componentes.
"""

import os
import json
import pickle
import logging
from tensorflow.keras.models import load_model
from flask import current_app

# Configurar logging
logger = logging.getLogger("mail_classifier_api.services.model_loader")

# Variables globales para almacenar el modelo y componentes
model = None
tokenizer_subject = None
tokenizer_body = None
label_encoder = None
class_mapping = None
max_sequence_length = 200

def load_model_and_components():
    """
    Carga el modelo y sus componentes desde los archivos guardados.
    Esta función debe llamarse antes de utilizar el modelo.
    """
    global model, tokenizer_subject, tokenizer_body, label_encoder, class_mapping, max_sequence_length
    
    try:
        # Utilizamos la configuración para obtener la ruta del modelo
        from app.config import Config
        model_dir = Config.MODEL_DIR
        max_sequence_length = Config.MAX_SEQUENCE_LENGTH
        
        # Carga el modelo
        model_path = os.path.join(model_dir, 'best_model.h5')
        logger.info(f"Cargando modelo desde: {model_path}")
        model = load_model(model_path)

        # Carga los tokenizers
        with open(os.path.join(model_dir, 'tokenizer_subject.pickle'), 'rb') as f:
            tokenizer_subject = pickle.load(f)

        with open(os.path.join(model_dir, 'tokenizer_body.pickle'), 'rb') as f:
            tokenizer_body = pickle.load(f)

        # Carga el label encoder
        with open(os.path.join(model_dir, 'label_encoder.pickle'), 'rb') as f:
            label_encoder = pickle.load(f)

        # Carga el mapeo de clases
        with open(os.path.join(model_dir, 'class_mapping.json'), 'r') as f:
            class_mapping = json.load(f)

        logger.info(f"Modelo y componentes cargados exitosamente. Clases disponibles: {len(class_mapping)}")
        return True
    except Exception as e:
        logger.error(f"Error al cargar el modelo o componentes: {str(e)}")
        raise e

def get_model():
    """
    Devuelve el modelo cargado, garantizando que esté disponible.
    
    Returns:
        El modelo de TensorFlow o None si no se pudo cargar
    """
    global model
    if model is None:
        try:
            load_model_and_components()
        except Exception as e:
            logger.error(f"Error al intentar cargar el modelo: {str(e)}")
            return None
    return model

def get_tokenizer_subject():
    """Devuelve el tokenizer para asuntos."""
    global tokenizer_subject
    if tokenizer_subject is None:
        try:
            load_model_and_components()
        except Exception:
            return None
    return tokenizer_subject

def get_tokenizer_body():
    """Devuelve el tokenizer para cuerpos de correo."""
    global tokenizer_body
    if tokenizer_body is None:
        try:
            load_model_and_components()
        except Exception:
            return None
    return tokenizer_body

def get_label_encoder():
    """Devuelve el encoder de etiquetas."""
    global label_encoder
    if label_encoder is None:
        try:
            load_model_and_components()
        except Exception:
            return None
    return label_encoder

def get_class_mapping():
    """Devuelve el mapeo de clases."""
    global class_mapping
    if class_mapping is None:
        try:
            load_model_and_components()
        except Exception:
            return None
    return class_mapping

def get_max_sequence_length():
    """Devuelve la longitud máxima de secuencia."""
    global max_sequence_length
    return max_sequence_length