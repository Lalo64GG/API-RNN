"""
Generador de respuestas para correos maliciosos utilizando la API de OpenAI.
Este módulo reemplaza la funcionalidad de transformer local y proporciona
respuestas de alta calidad mediante la API de OpenAI.
"""

import os
import time
import json
import logging
import requests
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("openai_response_generator")

# Cargar variables de entorno desde .env
load_dotenv()


class OpenAIResponseGenerator:
    """
    Generador de respuestas utilizando la API de OpenAI.
    Proporciona análisis detallados y recomendaciones para diferentes tipos de correos maliciosos.
    """

    def __init__(self):
        """
        Inicializa el generador de respuestas de OpenAI.
        Requiere que la API_KEY esté configurada en el archivo .env
        """
        self.api_key = os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            logger.warning("No se encontró OPENAI_API_KEY en las variables de entorno.")
            logger.warning("Las respuestas no podrán generarse hasta que se configure una clave válida.")
        else:
            logger.info("OpenAI Response Generator inicializado correctamente.")

        self.api_endpoint = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-3.5-turbo"  # Modelo predeterminado
        self.cache = {}  # Caché simple para respuestas

    def _create_prompt(self, email_class: str, confidence: float) -> str:
        """
        Crea un prompt optimizado para obtener respuestas detalladas sobre el tipo de correo malicioso.

        Args:
            email_class: Tipo de correo malicioso detectado
            confidence: Nivel de confianza de la clasificación (0-1)

        Returns:
            Prompt estructurado para la API de OpenAI
        """
        # Crear un prompt estructurado que obtenga la mejor respuesta posible
        return f"""Como experto en seguridad informática, proporciona un análisis detallado sobre correos maliciosos 
de tipo {email_class} que han sido detectados con un nivel de confianza del {confidence * 100:.1f}%.

Estructura tu respuesta en los siguientes apartados:

1. DESCRIPCIÓN DE LA AMENAZA:
   - Define en qué consiste un ataque de tipo {email_class}
   - Explica cómo funciona y cuáles son sus objetivos
   - Indica su nivel de peligrosidad

2. IDENTIFICACIÓN:
   - Proporciona 3-5 indicadores clave para reconocer este tipo de ataque
   - Señala elementos específicos a los que prestar atención

3. RECOMENDACIONES DE SEGURIDAD:
   - Detalla 4-6 acciones específicas para protegerse
   - Incluye medidas preventivas

4. PASOS SI YA ES VÍCTIMA:
   - Indica 3-4 pasos inmediatos a seguir si ya se ha interactuado con el correo
   - Explica cómo mitigar posibles daños

Tu respuesta debe ser técnicamente precisa pero comprensible para usuarios no expertos.
Utiliza un tono formal pero accesible."""

    def _call_openai_api(self, prompt: str) -> Optional[str]:
        """
        Realiza la llamada a la API de OpenAI.

        Args:
            prompt: Texto del prompt a enviar

        Returns:
            Respuesta generada o None si hay un error
        """
        if not self.api_key:
            logger.error("No se puede llamar a la API sin una clave API configurada")
            return None

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        data = {
            "model": self.model,
            "messages": [
                {"role": "system",
                 "content": "Eres un experto en seguridad informática especializado en análisis de correos maliciosos."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }

        try:
            response = requests.post(self.api_endpoint, headers=headers, json=data)
            response.raise_for_status()  # Lanzar excepción para códigos de error HTTP

            result = response.json()
            return result["choices"][0]["message"]["content"]

        except requests.exceptions.RequestException as e:
            logger.error(f"Error en la llamada a la API de OpenAI: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Detalles: {e.response.text}")
            return None

    def generate_security_response(self, email_class: str, confidence: float) -> str:
        """
        Genera una respuesta de seguridad detallada para un tipo específico de correo malicioso.

        Args:
            email_class: Tipo de correo malicioso detectado
            confidence: Nivel de confianza de la clasificación (0-1)

        Returns:
            Respuesta generada o mensaje de error
        """
        # Verificar si tenemos la respuesta en caché
        cache_key = f"{email_class}_{int(confidence * 100)}"
        if cache_key in self.cache:
            logger.info(f"Respuesta recuperada de caché para {email_class}")
            return self.cache[cache_key]

        # Si no hay API key configurada, devolver respuesta genérica
        if not self.api_key:
            return self._generate_fallback_response(email_class, confidence)

        # Crear el prompt y llamar a la API
        prompt = self._create_prompt(email_class, confidence)
        response = self._call_openai_api(prompt)

        if response:
            # Añadir un footer a la respuesta
            response += f"\n\n---\nAnálisis generado para correo de tipo: {email_class}"
            response += f"\nNivel de confianza: {confidence * 100:.1f}%"

            # Guardar en caché para futuras consultas
            self.cache[cache_key] = response
            return response
        else:
            # Si hay error, usar respuesta de fallback
            return self._generate_fallback_response(email_class, confidence)

    def _generate_fallback_response(self, email_class: str, confidence: float) -> str:
        """
        Genera una respuesta de fallback cuando no se puede usar la API.

        Args:
            email_class: Tipo de correo malicioso
            confidence: Nivel de confianza

        Returns:
            Respuesta básica generada localmente
        """
        # Respuestas básicas para los tipos más comunes
        fallback_responses = {
            "PHISHING_BANCARIO": "Se ha detectado un correo de suplantación bancaria. Nunca haga clic en enlaces recibidos por correo para acceder a su banco. Contacte directamente con su entidad bancaria si tiene dudas.",
            "PHISHING_CREDENCIALES": "Se ha detectado un intento de robo de credenciales. No introduzca sus contraseñas en sitios a los que acceda desde enlaces de correo.",
            "MALWARE_ADJUNTO": "PELIGRO: Se ha detectado un archivo adjunto malicioso. No lo descargue ni abra bajo ninguna circunstancia.",
            "CEO_FRAUD": "Se ha detectado un intento de suplantación de directivo. Verifique directamente con la persona por teléfono cualquier solicitud inusual.",
            "SEXTORSION": "Se ha detectado un intento de extorsión. La mayoría de estas amenazas son falsas. No responda ni pague.",
            # Añadir más tipos según sea necesario
        }

        # Obtener respuesta específica o genérica si no existe
        response = fallback_responses.get(
            email_class,
            f"Se ha detectado un correo potencialmente malicioso de tipo {email_class}. Por favor, tenga precaución."
        )

        # Añadir advertencia de que es una respuesta de emergencia
        response += "\n\nNota: Esta es una respuesta básica generada sin conexión a servicios avanzados de análisis."

        return response

    def set_model(self, model_name: str) -> None:
        """
        Cambia el modelo de OpenAI utilizado.

        Args:
            model_name: Nombre del modelo (ej: "gpt-4", "gpt-3.5-turbo")
        """
        self.model = model_name
        logger.info(f"Modelo cambiado a: {model_name}")

    def clear_cache(self) -> None:
        """Limpia la caché de respuestas."""
        self.cache = {}
        logger.info("Caché de respuestas limpiada")


# Ejemplo de uso del generador
if __name__ == "__main__":
    generator = OpenAIResponseGenerator()

    # Probar si hay una API key configurada
    if generator.api_key:
        # Generar respuesta para un tipo de correo malicioso
        response = generator.generate_security_response("PHISHING_BANCARIO", 0.92)
        print(response)
    else:
        print("Configurar OPENAI_API_KEY en el archivo .env para probar la API")