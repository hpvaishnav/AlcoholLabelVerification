# TTB Label Compliance Review Assistant

## Solution Architecture Document

---

## 1. System Overview & Architecture

The TTB Label Compliance Review Assistant is a standalone, AI-assisted verification web application designed for compliance agents at the Alcohol and Tobacco Tax and Trade Bureau (TTB). The architecture consists of a high-performance **Python FastAPI** backend serving an **HTML5/Vanilla JavaScript Single Page Application (SPA)**, powered by a modular local/cloud **OCR Extraction Engine**, a normalized **Fuzzy Matcher & Regulatory Validator**, and an **Asynchronous Batch Processor**.

```
 +-------------------------------------------------------------------------+
 |                          WEB USER INTERFACE                             |
 |  Single Label Review | Batch Processing | Audit Log | BOM & Config Tab   |
 +-------------------------------------------------------------------------+
                                    |  HTTP REST / Web API
                                    v
 +-------------------------------------------------------------------------+
 |                            FASTAPI BACKEND                              |
 |  /api/verify-single  |  /api/verify-batch  |  /api/export  | /api/config |
 +-------------------------------------------------------------------------+
            |                                           |
            v                                           v
 +-----------------------+                   +-----------------------------+
 |  OCR PIPELINE ENGINE  |                   |  BATCH ASYNC PROCESSOR      |
 |  Local (EasyOCR/Tess) |                   |  Background Queue & Worker  |
 |  Optional Cloud API   |                   |  Isolation & Progress Timer |
 +-----------------------+                   +-----------------------------+
            |                                           |
            +-------------------+-----------------------+
                                |
                                v
 +-------------------------------------------------------------------------+
 |               COMPARATOR & REGULATORY VALIDATOR (27 CFR 16)             |
 |  Text Normalization | RapidFuzz Token Match | Government Warning Rules  |
 |  Confidence Scoring | Decision Engine (Pass/Reject/Needs Review)        |
 +-------------------------------------------------------------------------+
                                |
                                v
 +-------------------------------------------------------------------------+
 |                     AUDIT TRAIL & RESULT EXPORT                         |
 |  Human Overrides | JSON Audit Trails | CSV Batch Compliance Summary |
 +-------------------------------------------------------------------------+
```

---

## 2. Software Bill of Materials (BOM) & Licenses

To comply with federal open-source software governance and supply-chain auditing, all core dependencies are pinned to exact version numbers and audited for license compatibility.

| Library / Dependency | Version | Open Source License | Primary Purpose in System |
| :--- | :--- | :--- | :--- |
| **FastAPI** | `0.111.0` | MIT | High-performance asynchronous REST API backend web framework |
| **Uvicorn** | `0.30.1` | BSD-3-Clause | ASGI server for serving FastAPI endpoints |
| **Pydantic** | `2.7.4` | MIT | Data validation, request/response schema serialization |
| **Python-Multipart** | `0.0.9` | Apache-2.0 | Form data parsing for file uploads (CSV, PNG, JPEG) |
| **Pillow (PIL)** | `10.3.0` | HPND (BSD-like) | Image processing, resizing, format conversion, thumbnail rendering |
| **PyTesseract** | `0.3.10` | Apache-2.0 | Wrapper for Google Tesseract OCR engine |
| **EasyOCR** | `1.7.1` | Apache-2.0 | Deep learning-based local OCR extraction engine |
| **RapidFuzz** | `3.9.3` | MIT | C++ accelerated fuzzy string matching & token set ratio comparison |
| **OpenCV (Headless)**| `4.9.0.80`| Apache-2.0 | Image preprocessing (grayscale, adaptive thresholding, noise reduction) |
| **Pandas** | `2.2.2` | BSD-3-Clause | CSV metadata parsing, batch analysis, export formatting |
| **Jinja2** | `3.1.4` | BSD-3-Clause | Template rendering for UI web components |
| **Python-Dotenv** | `1.0.1` | BSD-3-Clause | Environment variable configuration loader (`.env`) |
| **HTTPX** | `0.27.0` | BSD-3-Clause | Async HTTP client for optional Cloud Vision API integration |

---

## 3. Core Subsystems

### 3.1 OCR Extraction Engine (`app/ocr_engine.py`)
The system features a **Hybrid OCR Provider Interface**:
* **Local Provider (Default)**: Leverages `EasyOCR` / `PyTesseract` after OpenCV preprocessing (adaptive binarization and contrast stretching). Operates 100% offline within local network infrastructure with zero external network calls.
* **Optional Cloud Provider**: Triggered by setting environment variables `USE_CLOUD_OCR=true` and configuring `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or `GOOGLE_VISION_API_KEY`. Provides cloud vision inference when evaluating higher-resolution artwork or remote cloud environments.

#### Extracted Fields:
1. Brand Name
2. Class / Type
3. Alcohol Content (ABV %)
4. Proof
5. Net Contents
6. Bottler / Producer
7. Country of Origin
8. Government Warning Statement

### 3.2 Field Normalization & Comparison (`app/comparator.py`)
Field comparison uses a multi-tier matching strategy:
* **String Normalization**: Unicode NFKD normalization, case-folding, punctuation strip, multi-space collapse.
* **Fuzzy Matcher**: RapidFuzz `token_set_ratio` algorithm to evaluate word permutations and slight OCR transcription variances (e.g. accent marks, trailing punctuation).

#### Decision Threshold Matrix:
* **PASS (Score ≥ 90%)**: High confidence match.
* **NEEDS REVIEW (70% ≤ Score < 90%)**: Near match requiring agent verification.
* **REJECT (Score < 70% or Missing)**: Mismatched or absent mandatory field.

### 3.3 Strict Government Warning Validation (27 CFR Part 16)
The Government Warning statement is subjected to explicit regulatory rules:
1. **Mandatory Header**: Verifies presence of uppercase string `"GOVERNMENT WARNING:"`. If header is lowercase or missing, decision resolves to `REJECT` or `NEEDS REVIEW`.
2. **Surgeon General Statement**: Verifies exact text regarding pregnancy risks and birth defects.
3. **Impairment Statement**: Verifies exact text regarding operating machinery or driving a car.

### 3.4 Asynchronous Batch Processor (`app/batch_processor.py`)
* Uses Python `asyncio` background task queues.
* **Isolation**: Individual label failures are caught and logged as `Needs Review` or `Failed` without halting batch progression.
* Target execution throughput: **≤ 5 seconds per label**.

---

## 4. Data Flow Architecture

```
[User CSV + Images] --> [API Upload] --> [Preprocessing (OpenCV)]
                                              |
                                              v
[Field Comparison Engine] <--- [Text Extraction] <--- [Local / Cloud OCR Engine]
           |
           v
[Government Warning Rules] --> [Decision Matrix (Pass/Reject/Needs Review)]
                                              |
                                              v
[Human Override Modal] ------> [JSON / CSV Audit Trail Export]
```

---

## 5. Security & Governance

1. **Zero External Data Leakage**: Default local OCR mode operates completely isolated from external networks.
2. **Audit Logging**: Every validation output records timestamp, reviewer ID, extracted raw text, confidence score, decision, and human override logs.
