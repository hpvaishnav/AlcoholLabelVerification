# Backward compatibility wrapper for comparator module
from app.services.comparator_service import (
    calculate_token_similarity,
    normalize_text,
    remove_all_whitespace,
    LabelComparatorService as LabelComparator,
    comparator_service as comparator
)

__all__ = [
    "calculate_token_similarity",
    "normalize_text",
    "remove_all_whitespace",
    "LabelComparator",
    "comparator"
]
