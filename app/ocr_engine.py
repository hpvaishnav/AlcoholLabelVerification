# Backward compatibility wrapper for ocr_engine module
from app.services.ocr_service import (
    HybridOCREngine,
    ocr_service as ocr_engine
)

__all__ = [
    "HybridOCREngine",
    "ocr_engine"
]
