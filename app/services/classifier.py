"""
Funciones para clasificar correos electrónicos utilizando el modelo cargado.
"""

import numpy as np
import logging
from tensorflow.keras.preprocessing.sequence import pad_sequences
from app.services.model_loader import (
    get_model, get_tokenizer_subject, get_tokenizer_body, 
    get_label_encoder, get_max_sequence_length
)
from app.utils.risk_level import determine_risk_level

# Configurar logging
logger = logging.getLogger("mail_classifier_api.services.classifier")

def classify_email(subject: str, body: str) -> dict:

    # Obtenemos los componentes necesarios
    model = get_model()
    tokenizer_subject = get_tokenizer_subject()
    tokenizer_body = get_tokenizer_body()
    label_encoder = get_label_encoder()
    max_sequence_length = get_max_sequence_length()
    
    # Verificamos que todos los componentes estén disponibles
    if not all([model, tokenizer_subject, tokenizer_body, label_encoder]):
        logger.error("No se pueden realizar predicciones: componentes no disponibles")
        return {
            "error": "El modelo o componentes no están disponibles",
            "status": "error"
        }
    
    try:
        # Preprocesamiento del asunto
        subject_sequence = tokenizer_subject.texts_to_sequences([subject])
        subject_padded = pad_sequences(subject_sequence, maxlen=max_sequence_length)

        # Preprocesamiento del cuerpo
        body_sequence = tokenizer_body.texts_to_sequences([body])
        body_padded = pad_sequences(body_sequence, maxlen=max_sequence_length)

        # Realizamos la predicción
        prediction = model.predict([subject_padded, body_padded])[0]
        predicted_class_idx = np.argmax(prediction)
        predicted_class = label_encoder.inverse_transform([predicted_class_idx])[0]
        confidence = float(prediction[predicted_class_idx])

        # Obtenemos el mapeo de clases para todas las probabilidades
        class_mapping = {}
        for i, class_label in enumerate(label_encoder.classes_):
            class_mapping[class_label] = i

        # Construimos un diccionario con las probabilidades de todas las clases
        all_probs = {
            class_name: float(prediction[idx])
            for class_name, idx in class_mapping.items()
        }

        # Determinamos el nivel de riesgo
        risk_level = determine_risk_level(predicted_class, confidence)

        # Preparamos la respuesta
        result = {
            "predicted_class": predicted_class,
            "confidence": confidence,
            "all_probabilities": all_probs,
            "risk_level": risk_level,
            "status": "success"
        }
        
        logger.debug(f"Correo clasificado como {predicted_class} con confianza {confidence:.4f}")
        return result
    
    except Exception as e:
        logger.error(f"Error al clasificar correo: {str(e)}")
        return {
            "error": f"Error al clasificar el correo: {str(e)}",
            "status": "error"
        }