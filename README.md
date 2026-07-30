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

## Sample Benchmark Data & "Needs Review" Examples

The repository includes **50 realistic AI-generated alcohol label artwork images** in `sample_data/labels/` and metadata in `sample_data/applications_metadata.csv`, fully committed and pushed to git.

### Benchmark Dataset Scenarios:
- **`PASS` Cases (Scenarios 01 – 20)**: Fully compliant label artwork for Bourbon, Scotch, Rye, Wine, Tequila, Rum, Vodka, Gin, IPA, Cider, Brandy, and Mezcal.
- **`FIELD MISMATCH` Rejections (Scenarios 21 – 30)**: Intentional metadata mismatches (e.g. `45% ABV` on artwork vs `40% ABV` in metadata, wrong Net Contents, missing country of origin).
- **`NEEDS REVIEW` Cases (Scenarios 31 – 40)**: Subtle nuances requiring human compliance agent judgment:
  - `caps_diff_31_tequila_accent.png`: `EL JIMADOR` vs `EL JIMADÓR` (Diacritic / Accent accentuation)
  - `caps_diff_32_stones_throw_punctuation.png`: `STONE'S THROW` vs `STONES THROW` (Apostrophe punctuation difference)
  - `caps_diff_33_mixed_case_brand.png`: `OLD FORESTER` vs `Old Forester` (Casing variation)
  - `caps_diff_34_accent_french_wine.png`: `CHÂTEAU MARGAUX` vs `CHATEAU MARGAUX` (French circumflex accent)
  - `caps_diff_35_spacing_brand.png`: `DON JULIO` vs `DONJULIO` (Word boundary spacing)
  - `caps_diff_36_lowercase_class.png`: `STRAIGHT BOURBON WHISKEY` vs `Straight Bourbon Whiskey`
  - `caps_diff_37_short_abbrev.png`: `ALC. 45% BY VOL.` vs `ALC 45% BY VOL`
  - `caps_diff_38_title_case_bottler.png`: `KENTUCKY DISTILLERS CO.` vs `Kentucky Distillers Co.`
  - `caps_diff_39_german_umlaut.png`: `JÄGERMEISTER` vs `JAGERMEISTER` (German Umlaut character)
  - `caps_diff_40_trailing_dot.png`: `PRODUCED BY HEINEKEN BREWING.` vs `PRODUCED BY HEINEKEN BREWING`
- **`WARNING FAIL` Rejections (Scenarios 41 – 50)**: Strict 27 CFR Part 16 Government Warning violations (lowercase header, missing Surgeon General clause, altered wording).

---

## Application Metadata CSV Format

When uploading a metadata CSV file (or running batch verification), the system expects a CSV file containing the following column headers:

### Required & Optional Column Specifications

| CSV Column Header | Mandatory / Optional | Description & Example |
| :--- | :--- | :--- |
| `application_id` | **Mandatory** | Unique COLA application identifier (e.g., `COLA-2026-001`) |
| `brand_name` | **Mandatory** | Brand name as stated on application (e.g., `WOODFORD RESERVE`) |
| `class_type` | **Mandatory** | Class & Type designation (e.g., `KENTUCKY STRAIGHT BOURBON WHISKEY`) |
| `alcohol_content` | **Mandatory** | ABV percentage declaration (e.g., `45.2% ALC/VOL`) |
| `proof` | *Optional* | Proof declaration (e.g., `90.4 PROOF`). Marked `[NOT REQUIRED]` if missing on artwork when ABV % is present per TTB regulations. |
| `net_contents` | **Mandatory** | Net volume declaration (e.g., `750 ML` or `1 LITER`) |
| `bottler_producer` | **Mandatory** | Bottler / Producer name & address (e.g., `BROWN-FORMAN DISTILLERS, LOUISVILLE, KY`) |
| `country_of_origin` | **Mandatory** | Country of origin (e.g., `USA`, `MEXICO`, `FRANCE`) |
| `government_warning` | **Mandatory** | Expected Title 27 CFR 16 warning statement |
| `image_filename` | *Optional* | Name of corresponding label artwork file in batch ZIP (e.g., `pass_01_bourbon.png`) |

### Sample Metadata CSV File (`sample_data/applications_metadata.csv`)

```csv
application_id,brand_name,class_type,alcohol_content,proof,net_contents,bottler_producer,country_of_origin,government_warning,image_filename
COLA-PASS-2026-01,WOODFORD RESERVE,KENTUCKY STRAIGHT BOURBON WHISKEY,45.2% ALC/VOL,90.4 PROOF,750 ML,"BROWN-FORMAN DISTILLERS, LOUISVILLE, KY",USA,"GOVERNMENT WARNING: (1) According to the Surgeon General, women should not drink alcoholic beverages during pregnancy because of the risk of birth defects. (2) Consumption of alcoholic beverages impairs your ability to drive a car or operate machinery, and may cause health problems.",pass_01_bourbon.png
COLA-FAIL-2026-21,BUFFALO TRACE,KENTUCKY STRAIGHT BOURBON WHISKEY,40.0% ALC/VOL,80.0 PROOF,750 ML,"BUFFALO TRACE DISTILLERY, FRANKFORT, KY",USA,"GOVERNMENT WARNING: (1) According to the Surgeon General, women should not drink alcoholic beverages during pregnancy because of the risk of birth defects. (2) Consumption of alcoholic beverages impairs your ability to drive a car or operate machinery, and may cause health problems.",fail_mismatch_21_abv.png
COLA-REVIEW-2026-31,EL JIMADOR,TEQUILA BLANCO 100% DE AGAVE,40% ALC/VOL,80 PROOF,750 ML,"CASA HERRADURA, AMATITAN, JALISCO",MEXICO,"GOVERNMENT WARNING: (1) According to the Surgeon General, women should not drink alcoholic beverages during pregnancy because of the risk of birth defects. (2) Consumption of alcoholic beverages impairs your ability to drive a car or operate machinery, and may cause health problems.",caps_diff_31_tequila_accent.png
COLA-WARNFAIL-2026-41,SIERRA NEVADA,PALE ALE CRAFT BEER,5.6% ALC/VOL,11.2 PROOF,12 FL. OZ.,"SIERRA NEVADA BREWING CO., CHICO, CA",USA,"government warning: (1) According to the Surgeon General, women should not drink alcoholic beverages during pregnancy because of the risk of birth defects. (2) Consumption of alcoholic beverages impairs your ability to drive a car or operate machinery, and may cause health problems.",warning_fail_41_lowercase_header.png
```

---

## Docker Container Deployment

The application includes a production-ready **[Dockerfile](file:///Users/yeshabaxi/Documents/AlcoholLabelVerification/Dockerfile)** that bundles Python 3.11, Tesseract OCR, system dependencies, fonts, and the 50-scenario benchmark suite into a single self-contained container image.

> [!IMPORTANT]
> **Internet Access Requirement for Building**: An **internet-connected machine** is required during the `docker build` phase to download the base Linux image (`python:3.11-slim`), system packages (`tesseract-ocr`, `libgl1`, etc.), and Python packages via `pip`.
> 
> **Offline Execution**: Once the image is built, the running container operates **completely offline and air-gapped** inside your firewall with zero external network connectivity needed.

### 1. Build the Docker Image
From the project root directory, run:

```bash
docker build -t ttb-label-compliance:latest .
```

*Note: During build, `generate_samples.py` runs automatically inside the image to generate all 50 high-resolution benchmark label images and metadata.*

### 2. Run the Container
Launch the container mapping port `8000`:

```bash
docker run -d --name ttb-compliance -p 8000:8000 ttb-label-compliance:latest
```

### 3. Access the Compliance Dashboard
Open your browser and navigate to:
**`http://localhost:8000`**

### 4. Stop and Clean Up
To stop and remove the container:

```bash
docker stop ttb-compliance && docker rm ttb-compliance
```

---

## Local Python Quickstart & Setup Guide

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

## Running the Application Locally

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
1. Select the **Check Single Label** tab.
2. Load one of the pre-rendered demo cases (e.g. *Pass Case*, *Reject Case*, *Government Warning Case*) or upload your own label image and application metadata CSV.
3. Review the side-by-side comparison:
   - Left: Label artwork viewer with zoom/pan capabilities.
   - Right: Field comparison cards with expected metadata vs extracted OCR text, confidence scores, and explanations.
4. Test **Human Override**: Click **Override** on any field card to manually set status to `PASS`, `REJECT`, or `NEEDS REVIEW` and capture reviewer rationale into audit logs.

### Batch Upload & Processing
1. Select the **Check Multiple Labels (Batch)** tab.
2. Upload multiple label images, a `.ZIP` archive, or attach a metadata CSV file.
3. Click **Start Batch Processing** or trigger **Run 50-Item Batch Demo** from the top-right Admin menu.
4. Monitor real-time batch progress (Queued, Processing, Progress Bar, Speed Metric).
5. Filter batch results by clicking the top stat tiles (**Passing**, **Needs Human Review**, **Rejected**).
6. Click **Inspect** on any row to open the modal overlay inspect view with automatic focus on rejected fields.
7. Click **Download CSV Report** or **Download JSON Audit** to export audit compliance reports.

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
├── Dockerfile               # Production Docker container build file
├── .dockerignore            # Docker build ignore patterns
├── requirements.txt         # Pinned Python dependencies
├── .env.example             # Environment configuration template
├── generate_samples.py      # Benchmark test dataset generator
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
