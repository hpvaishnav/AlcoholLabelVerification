# Backward compatibility wrapper for batch_processor module
from app.services.batch_service import (
    BatchProcessorService as BatchProcessor,
    batch_service as batch_processor
)

__all__ = [
    "BatchProcessor",
    "batch_processor"
]
