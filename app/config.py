import os

class Config:
    HOST = os.getenv("HOST", "localhost")
    FLASK_PORT = int(os.getenv("FLASK_PORT", 4000))
    DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
    MODEL_DIR = os.getenv("MODEL_DIR", "model/fold_1")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    MAX_SEQUENCE_LENGTH = int(os.getenv("MAX_SEQUENCE_LENGTH", 200))
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
