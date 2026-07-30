<<<<<<< HEAD
# AlcoholLabelVerification
=======
# TTB Label Compliance Review Assistant

> **AI-Assisted Verification System for Alcohol Label Compliance Division (TTB Prototype)**

The TTB Label Compliance Review Assistant automates field-by-field verification of alcohol label artwork against application metadata, verifying compliance with federal regulations (including **Title 27 CFR Part 16 Government Warning** requirements) while keeping compliance agents in full control.

---

## Key Features

* **Offline Local OCR Execution**: Runs 100% locally by default with zero cloud AI or external service dependencies.
* **Optional Cloud API Mode**: Configurable via environment variables (`USE_CLOUD_OCR=true`) for evaluating cloud Vision models.
* **Strict Government Warning Rules**: Verifies exact wording, mandatory presence, and required uppercase `"GOVERNMENT WARNING:"` headers.
* **Fuzzy Field Normalization**: Uses RapidFuzz token matching to handle minor OCR transcription variations without false rejections.
* **Explainable Decisions**: Every field gets a `Pass`, `Reject`, or `Needs Review` status with a confidence score and human-readable explanation log.
* **Human Override Audit Trail**: Allows compliance reviewers to override automated decisions with complete audit log capture.
* **High-Throughput Batch Processing**: Processes batches of up to 300+ applications with real-time status monitoring, partial failure isolation, and execution times under **5 seconds per label**.
* **Result Export**: Export review findings to CSV and JSON formats.
* **Full Software Bill of Materials (BOM)**: Includes pinned versions and audited open-source licenses (MIT, Apache 2.0, BSD).

---

## Software Bill of Materials (BOM) & Licenses

| Dependency | Version | License | Description |
| :--- | :--- | :--- | :--- |
| `fastapi` | `0.111.0` | MIT | Web API framework |
| `uvicorn` | `0.30.1` | BSD-3-Clause | ASGI application server |
| `pydantic` | `2.7.4` | MIT | Data validation & schemas |
| `pytesseract` | `0.3.10` | Apache-2.0 | OCR engine interface |
| `easyocr` | `1.7.1` | Apache-2.0 | Deep-learning local OCR engine |
| `rapidfuzz` | `3.9.3` | MIT | C++ accelerated fuzzy string matching |
| `opencv-python-headless` | `4.9.0.80` | Apache-2.0 | Image preprocessing & thresholding |
| `pillow` | `10.3.0` | HPND | Image handling & thumbnailing |
| `pandas` | `2.2.2` | BSD-3-Clause | Data analytics & CSV processing |

---

## Quickstart & Setup Guide

### 1. Prerequisites
* Python 3.9+ installed on your system.
* (Optional) Tesseract OCR installed locally (`brew install tesseract` on macOS or `apt-get install tesseract-ocr` on Linux) for local fallback engine.

### 2. Installation
Clone or navigate to the project root directory and install dependencies:

```bash
cd /Users/yeshabaxi/Documents/AlcoholLabelVerification
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy the `.env.example` file:

```bash
cp .env.example .env
```

By default, `.env` contains:
```env
USE_CLOUD_OCR=false
OCR_CONFIDENCE_THRESHOLD=0.80
FUZZY_PASS_THRESHOLD=0.90
FUZZY_REVIEW_THRESHOLD=0.70
```

*(Optional)* To enable Cloud API OCR mode:
```env
USE_CLOUD_OCR=true
OPENAI_API_KEY=your_openai_key_here
```

---

## Running the Application

### 1. Generate Sample Test Data
Generate realistic demo alcohol label artwork (Whiskey, Wine, Tequila, Beer) and corresponding CSV metadata:

```bash
python3 generate_samples.py
```

This creates sample labels in `sample_data/labels/` and `sample_data/applications_metadata.csv`.

### 2. Start the Server
Run the FastAPI web application server:

```bash
python3 -m app.main
```
Or using Uvicorn directly:
```bash
uvicorn app.main:app --reload --port 8000
```

### 3. Open Web Interface
Open your web browser and navigate to:
`http://localhost:8000`

---

## System Usage Guide

### Single Label Review
1. Select the **Single Label Review** tab.
2. Load one of the pre-rendered demo cases (e.g. *Pass Case*, *Reject Case*, *Government Warning Case*) or upload your own label image and application metadata CSV.
3. Review the side-by-side comparison:
   - Left: Label artwork viewer with zoom/pan capabilities.
   - Right: Field comparison cards with expected metadata vs extracted OCR text, confidence scores, and explanations.
4. Test **Human Override**: Click **Override Decision** on any field to manually set status to `Pass`, `Reject`, or `Needs Review` and capture reviewer rationale.

### Batch Upload & Processing
1. Select the **Batch Processing** tab.
2. Upload `sample_data/applications_metadata.csv` and a ZIP archive or folder of label artwork files.
3. Click **Start Batch Review**.
4. Monitor real-time batch progress (Queued, Processing, Progress Bar, Speed Metric).
5. Filter batch results by status (`Pass`, `Reject`, `Needs Review`).
6. Click **Export CSV** or **Export JSON** to download audit compliance reports.

---

## Verification & Automated Testing

Run the automated test suite to verify string comparison, Government Warning validation, and decision engine logic:

```bash
python3 -m unittest discover -s tests
```

---

## Project Structure

```
AlcoholLabelVerification/
├── REQUIREMENTS.md          # Business specification document
├── ARCHITECTURE.md          # Solution architecture & BOM
├── README.md                # Quickstart & user guide
├── requirements.txt         # Pinned Python dependencies
├── .env.example             # Environment configuration template
├── generate_samples.py      # Demo test data generator
├── app/
│   ├── main.py              # FastAPI application server
│   ├── ocr_engine.py        # Local & Cloud hybrid OCR engine
│   ├── comparator.py        # Field comparison & CFR Part 16 rules
│   └── batch_processor.py   # Asynchronous batch worker queue
├── static/
│   ├── index.html           # HTML5 compliance dashboard
│   ├── styles.css           # Modern CSS stylesheet
│   └── app.js               # Web UI application logic
├── sample_data/             # Generated test artwork & CSVs
└── tests/                  # Automated unit test suite
```
>>>>>>> d58f68f (Initial commit: TTB Label Compliance Review Assistant with 50-Scenario Benchmark and Interactive Batch UI)
