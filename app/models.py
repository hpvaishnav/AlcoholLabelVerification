from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class FieldResult(BaseModel):
    field: str
    expected: str
    extracted: str
    status: str  # PASS, NEEDS REVIEW, REJECT
    match_score: float
    confidence: float
    explanation: str

class EvaluationResult(BaseModel):
    application_id: str
    overall_status: str  # PASS, NEEDS REVIEW, REJECT
    summary_reason: str
    field_results: Dict[str, FieldResult]
    ocr_engine_used: str
    processing_time_seconds: float
    image_url: Optional[str] = None
    item_processing_time: Optional[float] = None

class BatchJobStatus(BaseModel):
    job_id: str
    status: str  # QUEUED, PROCESSING, COMPLETED, FAILED
    total_items: int
    processed_items: int
    passed_count: int
    rejected_count: int
    review_count: int
    failed_count: int
    start_time: float
    end_time: Optional[float] = None
    average_time_per_label: float
    results: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []

class OverrideRequest(BaseModel):
    application_id: str
    field_name: str
    previous_status: str
    new_status: str
    reason: str
    reviewer_id: str = "Agent Sarah Chen"

class AuditRecord(BaseModel):
    timestamp: float
    application_id: str
    field_name: str
    previous_status: str
    new_status: str
    reason: str
    reviewer_id: str

class OCRExtractedField(BaseModel):
    value: str
    confidence: float

class OCRExtractionResult(BaseModel):
    raw_text: str
    fields: Dict[str, OCRExtractedField]
    overall_confidence: float
    engine_used: str
    processing_time_seconds: float

class BOMItem(BaseModel):
    library: str
    version: str
    license: str

class SystemConfigResponse(BaseModel):
    app_name: str
    ocr_mode: str
    target_processing_time: str
    fuzzy_pass_threshold: float
    fuzzy_review_threshold: float
    bom_summary: List[BOMItem]
