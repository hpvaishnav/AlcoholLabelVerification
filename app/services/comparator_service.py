import re
import difflib
import unicodedata
from typing import Dict, Any, List

from app.config import settings
from app.models import FieldResult, EvaluationResult, OCRExtractionResult

try:
    from rapidfuzz import fuzz
    HAS_RAPIDFUZZ = True
except ImportError:
    HAS_RAPIDFUZZ = False

def calculate_token_similarity(s1: str, s2: str) -> float:
    """Calculates token-set string similarity using RapidFuzz or difflib fallback."""
    if not s1 or not s2:
        return 0.0
    if HAS_RAPIDFUZZ:
        return fuzz.token_set_ratio(s1, s2) / 100.0
    else:
        words1 = set(s1.split())
        words2 = set(s2.split())
        if not words1 or not words2:
            return 0.0
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        jaccard = len(intersection) / len(union)
        seq_ratio = difflib.SequenceMatcher(None, s1, s2).ratio()
        return round(0.7 * jaccard + 0.3 * seq_ratio, 3)

def normalize_text(text: str) -> str:
    """Normalizes text by stripping accents (NFKD), lowercasing, and collapsing whitespace."""
    if not text:
        return ""
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    text = text.lower()
    text = re.sub(r'[^a-z0-9%\.]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def remove_all_whitespace(text: str) -> str:
    return re.sub(r'\s+', '', normalize_text(text))

class LabelComparatorService:
    def __init__(self, pass_threshold: float = settings.fuzzy_pass_threshold, review_threshold: float = settings.fuzzy_review_threshold):
        self.pass_threshold = pass_threshold
        self.review_threshold = review_threshold

    def compare_field(self, field_name: str, expected: str, extracted: str, ocr_confidence: float) -> FieldResult:
        """Compares a single metadata field against extracted OCR text."""
        exp_clean = normalize_text(expected)
        ext_clean = normalize_text(extracted)

        if not expected or expected.upper() in ["N/A", "NONE", "UNKNOWN", ""]:
            return FieldResult(
                field=field_name,
                expected=expected or "N/A",
                extracted=extracted or "N/A",
                status="PASS",
                match_score=1.0,
                confidence=ocr_confidence,
                explanation="Field marked N/A in application metadata."
            )

        if not extracted or extracted.strip() == "":
            if field_name.lower() in ["proof"]:
                return FieldResult(
                    field=field_name,
                    expected=expected,
                    extracted="[NOT REQUIRED]",
                    status="PASS",
                    match_score=1.0,
                    confidence=1.0,
                    explanation="Proof is an optional field when Alcohol Content (ABV %) is present."
                )
            return FieldResult(
                field=field_name,
                expected=expected,
                extracted="[NOT DETECTED]",
                status="REJECT",
                match_score=0.0,
                confidence=0.0,
                explanation=f"Mandatory field '{field_name}' could not be detected on label artwork."
            )

        similarity = calculate_token_similarity(exp_clean, ext_clean)
        
        if remove_all_whitespace(expected) == remove_all_whitespace(extracted):
            similarity = 1.0

        if similarity >= self.pass_threshold and ocr_confidence >= 0.70:
            status = "PASS"
            explanation = f"Exact or high-confidence match ({int(similarity * 100)}% text similarity)."
        elif similarity >= self.review_threshold or ocr_confidence < 0.70:
            status = "NEEDS REVIEW"
            explanation = f"Near match ({int(similarity * 100)}% similarity) or lower OCR confidence. Requires human agent review."
        else:
            status = "REJECT"
            explanation = f"Mismatch detected between metadata ('{expected}') and label text ('{extracted}'). Similarity: {int(similarity * 100)}%."

        return FieldResult(
            field=field_name,
            expected=expected,
            extracted=extracted,
            status=status,
            match_score=round(similarity, 3),
            confidence=round(ocr_confidence, 3),
            explanation=explanation
        )

    def validate_government_warning(self, expected: str, extracted_text: str) -> FieldResult:
        """Strict regulatory validation for Title 27 CFR Part 16 Government Warning."""
        if not extracted_text or extracted_text.strip() == "":
            return FieldResult(
                field="government_warning",
                expected=expected,
                extracted="[NOT DETECTED]",
                status="REJECT",
                match_score=0.0,
                confidence=0.0,
                explanation="CRITICAL REGULATORY VIOLATION: Mandatory Government Warning statement is completely missing from label artwork."
            )

        reasons = []
        status = "PASS"

        has_uppercase_header = bool(re.search(r'GOVERNMENT\s+WARNING[\:\.\s\,-]', extracted_text))
        if not has_uppercase_header:
            if re.search(r'Government\s+Warning|government\s+warning', extracted_text):
                status = "REJECT"
                reasons.append("Header 'GOVERNMENT WARNING:' must be in ALL CAPS per 27 CFR 16.21.")
            else:
                status = "REJECT"
                reasons.append("Mandatory header 'GOVERNMENT WARNING:' was not found.")

        has_surgeon = bool(re.search(r'SURG?EON\s+GEN', extracted_text, re.IGNORECASE))
        has_pregnancy = bool(re.search(r'PREGNAN', extracted_text, re.IGNORECASE))
        if not (has_surgeon and has_pregnancy):
            status = "REJECT"
            reasons.append("Missing required Surgeon General pregnancy health risk warning.")

        has_driving = bool(re.search(r'DRIVE\s+A?\s*CAR|OPERATE\s+MACHINERY|HEALTH\s+PROBLEMS', extracted_text, re.IGNORECASE))
        if not has_driving:
            status = "REJECT"
            reasons.append("Missing required driving/machinery impairment warning statement.")

        if not reasons:
            explanation = "Fully compliant with 27 CFR Part 16: Required uppercase header and health warning statements verified."
            sim_score = 1.0
        else:
            explanation = " ".join(reasons)
            sim_score = 0.0

        return FieldResult(
            field="government_warning",
            expected=expected,
            extracted=extracted_text[:180] + "..." if len(extracted_text) > 180 else extracted_text,
            status=status,
            match_score=round(sim_score, 3),
            confidence=0.98 if status == "PASS" else 0.70,
            explanation=explanation
        )

    def evaluate_application(self, metadata: Dict[str, str], ocr_results: OCRExtractionResult) -> EvaluationResult:
        """Evaluates all fields and computes final overall application compliance decision."""
        field_results: Dict[str, FieldResult] = {}
        raw_text = ocr_results.raw_text
        extracted_fields = ocr_results.fields

        target_fields = [
            ("brand_name", "Brand Name"),
            ("class_type", "Class / Type"),
            ("alcohol_content", "Alcohol Content"),
            ("proof", "Proof"),
            ("net_contents", "Net Contents"),
            ("bottler_producer", "Bottler / Producer"),
            ("country_of_origin", "Country of Origin"),
        ]

        statuses = []
        raw_no_space = remove_all_whitespace(raw_text)

        for field_key, display_name in target_fields:
            exp_val = metadata.get(field_key, "")
            field_data = extracted_fields.get(field_key)
            ext_val = field_data.value if field_data else ""
            conf = field_data.confidence if field_data else 0.85

            exp_no_space = remove_all_whitespace(exp_val)
            if exp_val and exp_no_space in raw_no_space:
                ext_val = exp_val
                conf = 0.98

            res = self.compare_field(display_name, exp_val, ext_val, conf)
            field_results[field_key] = res
            statuses.append(res.status)

        exp_gov = metadata.get("government_warning", "")
        gov_res = self.validate_government_warning(exp_gov, raw_text)
        field_results["government_warning"] = gov_res
        statuses.append(gov_res.status)

        if "REJECT" in statuses:
            overall_status = "REJECT"
            summary_reason = "Application REJECTED due to critical regulatory or metadata field mismatches."
        elif "NEEDS REVIEW" in statuses:
            overall_status = "NEEDS REVIEW"
            summary_reason = "Application requires HUMAN REVIEW due to near matches or lower confidence scores."
        else:
            overall_status = "PASS"
            summary_reason = "All required fields and regulatory warning statements match metadata with high confidence."

        return EvaluationResult(
            application_id=metadata.get("application_id", "UNKNOWN"),
            overall_status=overall_status,
            summary_reason=summary_reason,
            field_results=field_results,
            ocr_engine_used=ocr_results.engine_used,
            processing_time_seconds=ocr_results.processing_time_seconds
        )

comparator_service = LabelComparatorService()
