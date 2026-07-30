import os
from pydantic import BaseModel

class Settings(BaseModel):
    app_name: str = "TTB Label Compliance Review Assistant"
    app_version: str = "1.0.0"
    app_description: str = "AI-assisted verification prototype for Alcohol Label Compliance Division"
    
    # Matching & Decision Thresholds
    fuzzy_pass_threshold: float = float(os.getenv("FUZZY_PASS_THRESHOLD", "0.80"))
    fuzzy_review_threshold: float = float(os.getenv("FUZZY_REVIEW_THRESHOLD", "0.65"))
    ocr_confidence_threshold: float = float(os.getenv("OCR_CONFIDENCE_THRESHOLD", "0.80"))
    
    # Engine Mode
    use_cloud_ocr: bool = os.getenv("USE_CLOUD_OCR", "false").lower() == "true"
    cloud_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # Directory Paths
    static_dir: str = os.getenv("STATIC_DIR", "static")
    labels_dir: str = os.getenv("LABELS_DIR", "sample_data/labels")
    sample_data_dir: str = os.getenv("SAMPLE_DATA_DIR", "sample_data")
    temp_dir: str = os.path.join(sample_data_dir, "temp")
    temp_batch_dir: str = os.path.join(labels_dir, "batch_temp")

settings = Settings()
