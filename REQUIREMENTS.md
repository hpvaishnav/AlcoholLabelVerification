# TTB Label Compliance Review Assistant

## Requirements & Specification Document (Prototype Phase)

---

## 1. Executive Summary

The Alcohol and Tobacco Tax and Trade Bureau (TTB) Label Compliance Division processes approximately **150,000 alcohol label applications annually** using a largely manual review process. Compliance agents visually compare submitted label artwork against application information to verify regulatory compliance.

The objective of this prototype is to demonstrate an AI-assisted verification system that automates repetitive comparison tasks while preserving human judgment for ambiguous or regulatory-sensitive decisions. The prototype is intentionally standalone and does not integrate with the existing COLA system.

The solution improves review efficiency, reduces repetitive manual work, and provides clear, explainable verification results while maintaining a target processing time of **five seconds or less per label**.

---

## 2. Business Objectives

The prototype shall:

* Reduce repetitive manual verification performed by compliance agents.
* Improve processing throughput without replacing human reviewers.
* Demonstrate AI-assisted verification suitable for future integration.
* Provide transparent and explainable verification results.
* Support both single-label and batch review workflows.

---

## 3. Stakeholder Summary

| Stakeholder     | Role                                    | Primary Goals                                                              |
| --------------- | --------------------------------------- | -------------------------------------------------------------------------- |
| **Sarah Chen**   | Lead Compliance Agent                   | Faster processing, batch uploads, simple interface, <5 second response     |
| **Marcus Williams**| IT / Security Director                | Standalone solution, no COLA integration, no external AI dependencies by default |
| **Dave Morrison**| Senior Compliance Auditor               | Preserve human judgment, avoid false mismatches, maintain explainability   |
| **Jenny Park**   | Regulatory Policy Analyst               | Accurate regulatory validation, especially Government Warning verification |

---

## 4. Functional Requirements

### FR-1 Upload Application Package
The system shall accept:
* Application metadata (CSV format)
* Label artwork (JPEG, PNG formats)

Unsupported or corrupted files shall generate a clear validation error message without crashing.

### FR-2 OCR Extraction
The system shall extract, where present on the label artwork:
* Brand Name
* Class / Type
* Alcohol Content (ABV %)
* Proof (if present)
* Net Contents
* Bottler / Producer Name & Address
* Country of Origin
* Government Warning Statement

### FR-3 Field Comparison
The extracted information shall be compared against application metadata on a field-by-field basis.

### FR-4 Brand Matching & Text Normalization
Brand names and other free-text fields shall use normalized comparison including:
* Case-insensitive matching
* Whitespace normalization
* Punctuation normalization
* Fuzzy string matching via RapidFuzz token set ratio algorithms

Near matches (similarity score between 70% and 89%) shall be flagged as **Needs Review** instead of being automatically rejected.

### FR-5 Government Warning Validation
The Government Warning shall be validated against the official required wording under Title 27 CFR Part 16.

The system shall strictly verify:
1. Exact presence of mandatory warning text.
2. Required uppercase header: **"GOVERNMENT WARNING:"**
3. Mandatory health warning statements (Surgeon General statement regarding pregnancy/birth defects and driving/machinery operation).

If OCR confidence is insufficient to verify capitalization or exact wording, the field shall be classified as **Needs Review**.

### FR-6 Decision Classification
Each validated field and overall application shall receive one of:
* **Pass**: Field matches metadata within configured high-confidence threshold (≥ 90%).
* **Reject**: Mandatory field is missing, severely mismatched (< 70%), or violates strict regulatory rules.
* **Needs Review**: Field requires human judgment due to borderline confidence (70% - 89%), low OCR resolution, or OCR uncertainty.

### FR-7 Explainable Results
Every validation result shall include:
* Expected value (from metadata)
* Extracted value (from OCR)
* Validation outcome (Pass / Reject / Needs Review)
* Confidence score (0.0 to 1.0)
* Human-readable explanation detailing why the decision was made.

### FR-8 OCR Confidence & Automated Routing
Confidence scores shall be calculated and displayed for every extracted field. Fields below the configured confidence threshold (default 80%) shall automatically be routed to **Needs Review**.

### FR-9 Human Override & Audit Recording
Compliance agents shall be able to override any automated decision (e.g. changing `Needs Review` or `Reject` to `Pass`). All overrides shall be permanently recorded in the structured audit log output.

### FR-10 Batch Processing
The system shall support batch uploads of at least **300 applications** in a single job.

### FR-11 Real-Time Batch Status Monitoring
Users shall be able to monitor real-time execution status during batch operations:
* Queued
* Processing (with live progress bar and throughput timer)
* Completed
* Failed

### FR-12 Partial Failure Isolation
Failure to process an individual application (e.g. corrupted image file) shall not terminate or interrupt processing of remaining items in the batch.

### FR-13 Exception Handling
Unreadable images, OCR extraction failures, or missing metadata fields shall never produce silent failures. Such items shall be explicitly classified as **Needs Review** with a diagnostic explanation log.

### FR-14 User Interface
The interface shall support:
* Single label side-by-side review
* Batch file drag-and-drop upload
* High-contrast status indicators (Green / Red / Amber)
* Large, accessible controls suitable for reviewers of varying technical backgrounds.

### FR-15 Result Export
Users shall be able to export single and batch review results in structured **CSV** and **JSON** formats.

---

## 5. Non-Functional Requirements

| Category        | Requirement                                                                                                            |
| --------------- | ---------------------------------------------------------------------------------------------------------------------- |
| **Performance** | Average processing time shall not exceed **5 seconds per individual label** under standard execution conditions.       |
| **Scalability**  | System shall process batches of at least **300 labels** asynchronously without memory leakage.                         |
| **Reliability** | Processing failures shall be isolated to individual labels without interrupting remaining batch items.                |
| **Availability**| Web UI shall remain fluid and responsive while background batch workers process jobs.                                |
| **Security**    | System operates locally without external data transmission or production credential dependencies.                      |
| **Deployment**  | Operates 100% offline within local network by default. Optional Cloud API mode configurable via environment variables.|
| **Accessibility**| High-contrast UI with WCAG AA compliance standards for status colors and clear typography.                             |
| **Auditability**| Every decision produces a structured JSON audit record describing expected vs actual text and explanation rationale.   |
| **Compliance**  | Includes software Bill of Materials (BOM) listing exact pinned library versions and open-source licenses.              |

---

## 6. Assumptions

1. Metadata is provided in CSV format.
2. Label artwork images are provided in JPEG or PNG format.
3. Default execution uses locally hosted OCR engines (Tesseract / EasyOCR).
4. Compliance agents remain the ultimate decision-makers; system functions as an AI assistant.
5. Verification results are exportable to standard CSV and JSON files for audit compliance.
