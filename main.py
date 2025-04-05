import os
import json
import pickle
import numpy as np
from typing import Optional, Dict, List
from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import tensorflow as tf

# Configura la sesión de TensorFlow para gestionar la memoria
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        print(e)

app = Flask(__name__)

# Variables globales para almacenar el modelo cargado y componentes
model = None
tokenizer_subject = None
tokenizer_body = None
label_encoder = None
class_mapping = None
max_sequence_length = 200


def load_model_and_components():
    """Carga el modelo y sus componentes"""
    global model, tokenizer_subject, tokenizer_body, label_encoder, class_mapping, max_sequence_length

    # Configura la ruta a los archivos del modelo
    model_dir = "modelos_rnn_cv/fold_1"  # Ajusta según la ubicación de tu modelo

    try:
        # Carga el modelo
        model = load_model(os.path.join(model_dir, 'best_model.h5'))

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

        print("Modelo y componentes cargados exitosamente.")
    except Exception as e:
        print(f"Error al cargar el modelo o componentes: {e}")
        raise e


def get_model():
    """Garantiza que el modelo esté cargado antes de usarlo"""
    if model is None:
        load_model_and_components()
    return model


def classify_email(subject: str, body: str):
    """Clasifica un correo electrónico usando el modelo cargado"""
    get_model()  # Asegura que el modelo está cargado

    # Preprocesamiento del asunto
    subject_sequence = tokenizer_subject.texts_to_sequences([subject])
    subject_padded = pad_sequences(subject_sequence, maxlen=max_sequence_length)

    # Preprocesamiento del cuerpo
    body_sequence = tokenizer_body.texts_to_sequences([body])
    body_padded = pad_sequences(body_sequence, maxlen=max_sequence_length)

    # Predicción
    prediction = model.predict([subject_padded, body_padded])[0]
    predicted_class_idx = np.argmax(prediction)
    predicted_class = label_encoder.inverse_transform([predicted_class_idx])[0]
    confidence = float(prediction[predicted_class_idx])

    # Mapeo de todas las probabilidades
    all_probs = {
        class_name: float(prediction[idx])
        for class_name, idx in class_mapping.items()
    }

    # Determinar nivel de riesgo basado en la confianza y tipo de amenaza
    risk_level = determine_risk_level(predicted_class, confidence)

    return {
        "predicted_class": predicted_class,
        "confidence": confidence,
        "all_probabilities": all_probs,
        "risk_level": risk_level
    }


def determine_risk_level(class_name: str, confidence: float) -> str:
    """Determina el nivel de riesgo basado en la clase y confianza"""
    # Categorías de alto riesgo
    high_risk_classes = [
        "CEO_FRAUD", "MALWARE_ADJUNTO", "PHISHING_BANCARIO",
        "SEXTORSION", "PHISHING_CREDENCIALES"
    ]

    # Categorías de riesgo medio
    medium_risk_classes = [
        "PHARMING", "FRAUDE_SOPORTE", "VISHING", "SMISHING"
    ]

    # Las demás categorías se consideran de riesgo bajo por defecto

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


@app.route("/", methods=["GET"])
def read_root():
    """Endpoint raíz para verificar que la API está funcionando"""
    return jsonify({"status": "online", "message": "API de Clasificación de Correos Maliciosos"})


@app.route("/health", methods=["GET"])
def health_check():
    """Endpoint para verificar la salud del servicio"""
    return jsonify({"status": "healthy", "model_loaded": model is not None})


@app.route("/predict", methods=["POST"])
def predict_email():
    """Endpoint para clasificar un correo electrónico"""
    try:
        email = request.get_json()
        subject = email["subject"]
        body = email["body"]

        result = classify_email(subject, body)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Error al procesar la solicitud: {str(e)}"}), 500


@app.route("/batch-predict", methods=["POST"])
def batch_predict():
    """Endpoint para clasificar múltiples correos electrónicos"""
    try:
        emails = request.get_json()
        results = []
        for email in emails:
            subject = email["subject"]
            body = email["body"]
            result = classify_email(subject, body)
            results.append({
                "subject": subject[:50] + "..." if len(subject) > 50 else subject,
                "prediction": result
            })
        return jsonify({"results": results, "count": len(results)})
    except Exception as e:
        return jsonify({"error": f"Error al procesar la solicitud por lotes: {str(e)}"}), 500


@app.route("/classes", methods=["GET"])
def get_classes():
    """Endpoint para obtener las clases disponibles"""
    get_model()  # Asegura que el modelo está cargado
    return jsonify({"classes": list(class_mapping.keys()), "total": len(class_mapping)})


if __name__ == "__main__":
    # Carga el modelo al iniciar
    load_model_and_components()
    # Inicia el servidor Flask
    app.run(host="0.0.0.0", port=4000)
