import os
import io
import csv
import json
import zipfile
import shutil
import asyncio
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, File, UploadFile, Form, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models import OverrideRequest, AuditRecord, SystemConfigResponse, BOMItem
from app.services.ocr_service import ocr_service
from app.services.comparator_service import comparator_service
from app.services.batch_service import batch_service

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(settings.static_dir, exist_ok=True)
os.makedirs(settings.labels_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")
app.mount("/labels", StaticFiles(directory=settings.labels_dir), name="labels")

audit_overrides: List[AuditRecord] = []

@app.get("/", response_class=HTMLResponse)
async def get_index():
    index_path = os.path.join(settings.static_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h2>TTB Label Compliance Review Assistant Backend Active</h2>")

@app.get("/api/config", response_model=SystemConfigResponse)
async def get_system_config():
    return SystemConfigResponse(
        app_name=settings.app_name,
        ocr_mode="Cloud API Mode" if settings.use_cloud_ocr else "100% Local Offline (EasyOCR/Tesseract)",
        target_processing_time="< 5.0 seconds per label",
        fuzzy_pass_threshold=settings.fuzzy_pass_threshold,
        fuzzy_review_threshold=settings.fuzzy_review_threshold,
        bom_summary=[
            BOMItem(library="FastAPI", version="0.111.0", license="MIT"),
            BOMItem(library="PyTesseract", version="0.3.10", license="Apache-2.0"),
            BOMItem(library="EasyOCR", version="1.7.1", license="Apache-2.0"),
            BOMItem(library="RapidFuzz", version="3.9.3", license="MIT"),
            BOMItem(library="OpenCV Headless", version="4.9.0.80", license="Apache-2.0"),
            BOMItem(library="Pandas", version="2.2.2", license="BSD-3-Clause")
        ]
    )

@app.get("/api/sample-data")
async def get_sample_cases():
    csv_path = os.path.join(settings.sample_data_dir, "applications_metadata.csv")
    if not os.path.exists(csv_path):
        from generate_samples import generate_50_samples
        generate_50_samples()

    cases = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["image_url"] = f"/labels/{row['image_filename']}"
            cases.append(row)
    return {"sample_cases": cases}

@app.post("/api/verify-single")
async def verify_single(
    image: Optional[UploadFile] = File(None),
    metadata_csv: Optional[UploadFile] = File(None),
    metadata_json: Optional[str] = Form(None),
    sample_filename: Optional[str] = Form(None)
):
    """Verifies single label artwork image against metadata."""
    os.makedirs(settings.temp_dir, exist_ok=True)
    
    if sample_filename:
        image_path = os.path.join(settings.labels_dir, sample_filename)
        image_url = f"/labels/{sample_filename}"
    elif image:
        image_path = os.path.join(settings.temp_dir, image.filename)
        with open(image_path, "wb") as f:
            f.write(await image.read())
        image_url = f"/labels/temp/{image.filename}"
        temp_static = os.path.join(settings.labels_dir, "temp")
        os.makedirs(temp_static, exist_ok=True)
        shutil.copy(image_path, os.path.join(temp_static, image.filename))
    else:
        raise HTTPException(status_code=400, detail="Please upload a label artwork image.")

    metadata = {}
    if metadata_json:
        metadata = json.loads(metadata_json)
    elif metadata_csv:
        csv_bytes = await metadata_csv.read()
        buffer = io.StringIO(csv_bytes.decode("utf-8"))
        reader = csv.DictReader(buffer)
        rows = list(reader)
        if rows:
            metadata = rows[0]

    ocr_res = ocr_service.extract_text_from_image(image_path)
    eval_res = comparator_service.evaluate_application(metadata, ocr_res)
    eval_dict = eval_res.model_dump()
    eval_dict["image_url"] = image_url

    return JSONResponse(content=eval_dict)

@app.post("/api/verify-batch")
async def verify_batch(
    background_tasks: BackgroundTasks,
    images: List[UploadFile] = File(default=[]),
    zip_file: Optional[UploadFile] = File(None),
    csv_file: Optional[UploadFile] = File(None)
):
    """Processes batch label applications from images, ZIP archive, or CSV metadata."""
    os.makedirs(settings.temp_batch_dir, exist_ok=True)

    csv_items_map = {}
    if csv_file:
        contents = await csv_file.read()
        buffer = io.StringIO(contents.decode("utf-8"))
        reader = csv.DictReader(buffer)
        for row in reader:
            fname = row.get("image_filename", "").strip()
            if fname:
                csv_items_map[fname] = row

    batch_image_files = []

    # 1. Unpack ZIP if uploaded
    if zip_file and zip_file.filename:
        zip_bytes = await zip_file.read()
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
            for zname in z.namelist():
                if zname.lower().endswith(('.png', '.jpg', '.jpeg')) and not zname.startswith('__MACOSX'):
                    extracted_path = z.extract(zname, settings.temp_batch_dir)
                    fname = os.path.basename(zname)
                    target_path = os.path.join(settings.temp_batch_dir, fname)
                    if extracted_path != target_path:
                        shutil.move(extracted_path, target_path)
                    batch_image_files.append((fname, target_path))

    # 2. Save multiple uploaded image files
    if images:
        for img in images:
            if img.filename and img.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                save_path = os.path.join(settings.temp_batch_dir, img.filename)
                with open(save_path, "wb") as f:
                    f.write(await img.read())
                batch_image_files.append((img.filename, save_path))

    # Assemble items for batch worker
    items = []

    if batch_image_files:
        for fname, fpath in batch_image_files:
            csv_meta = csv_items_map.get(fname, {})
            item = {
                "application_id": csv_meta.get("application_id", fname),
                "image_filename": fname,
                "image_path": fpath,
                **csv_meta
            }
            items.append(item)
    elif csv_items_map:
        for fname, csv_meta in csv_items_map.items():
            item = {
                "application_id": csv_meta.get("application_id", fname),
                "image_filename": fname,
                "image_path": os.path.join(settings.labels_dir, fname),
                **csv_meta
            }
            items.append(item)

    if not items:
        raise HTTPException(status_code=400, detail="Please upload image files, a ZIP archive, or a CSV file to process batch.")

    job_id = batch_service.create_job(len(items))
    background_tasks.add_task(batch_service.process_batch_async, job_id, items, settings.labels_dir)

    return {
        "job_id": job_id,
        "message": f"Batch processing started for {len(items)} label applications.",
        "status": "QUEUED"
    }

@app.get("/api/batch-status/{job_id}")
async def get_batch_status(job_id: str):
    return batch_service.get_job_status(job_id)

@app.post("/api/override")
async def record_human_override(req: OverrideRequest):
    override_entry = AuditRecord(
        timestamp=asyncio.get_event_loop().time(),
        application_id=req.application_id,
        field_name=req.field_name,
        previous_status=req.previous_status,
        new_status=req.new_status,
        reason=req.reason,
        reviewer_id=req.reviewer_id
    )
    audit_overrides.append(override_entry)
    return {"message": "Override recorded successfully.", "audit_record": override_entry.model_dump()}

@app.get("/api/export/{job_id}/{export_format}")
async def export_batch_results(job_id: str, export_format: str):
    job = batch_service.get_job_status(job_id)
    if "error" in job:
        raise HTTPException(status_code=404, detail="Batch job not found.")

    results = job.get("results", [])

    if export_format.lower() == "json":
        json_data = json.dumps(job, indent=2)
        return StreamingResponse(
            io.BytesIO(json_data.encode("utf-8")),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=ttb_batch_results_{job_id}.json"}
        )

    elif export_format.lower() == "csv":
        output = io.StringIO()
        fieldnames = ["application_id", "overall_status", "summary_reason", "processing_time_seconds", "ocr_engine_used"]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for res in results:
            writer.writerow({
                "application_id": res.get("application_id"),
                "overall_status": res.get("overall_status"),
                "summary_reason": res.get("summary_reason"),
                "processing_time_seconds": res.get("processing_time_seconds"),
                "ocr_engine_used": res.get("ocr_engine_used")
            })

        return StreamingResponse(
            io.BytesIO(output.getvalue().encode("utf-8")),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=ttb_batch_results_{job_id}.csv"}
        )

    else:
        raise HTTPException(status_code=400, detail="Invalid export format. Choose 'csv' or 'json'.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
