import os
import time
import uuid
import asyncio
import logging
from typing import Dict, Any, List
from app.ocr_engine import ocr_engine
from app.comparator import comparator

logger = logging.getLogger("batch_processor")

class BatchProcessor:
    def __init__(self):
        # In-memory storage for active and completed batch jobs
        self.jobs: Dict[str, Dict[str, Any]] = {}

    def create_job(self, total_items: int) -> str:
        job_id = str(uuid.uuid4())[:8]
        self.jobs[job_id] = {
            "job_id": job_id,
            "status": "QUEUED", # QUEUED, PROCESSING, COMPLETED, FAILED
            "total_items": total_items,
            "processed_items": 0,
            "passed_count": 0,
            "rejected_count": 0,
            "review_count": 0,
            "failed_count": 0,
            "start_time": time.time(),
            "end_time": None,
            "average_time_per_label": 0.0,
            "results": [],
            "errors": []
        }
        return job_id

    async def process_batch_async(self, job_id: str, items: List[Dict[str, Any]], labels_dir: str):
        job = self.jobs.get(job_id)
        if not job:
            return

        job["status"] = "PROCESSING"
        job["start_time"] = time.time()
        
        for item in items:
            item_start = time.time()
            app_id = item.get("application_id", "UNKNOWN")
            img_file = item.get("image_filename", "")
            img_path = item.get("image_path") or (os.path.join(labels_dir, img_file) if img_file else "")

            try:
                # 1. OCR Extraction
                if os.path.exists(img_path):
                    ocr_res = ocr_engine.extract_text_from_image(img_path)
                else:
                    ocr_res = {
                        "raw_text": "",
                        "fields": {},
                        "overall_confidence": 0.0,
                        "engine_used": "N/A",
                        "processing_time_seconds": 0.0
                    }

                # 2. Field Comparison & CFR 16 Validation
                eval_res = comparator.evaluate_application(item, ocr_res)
                eval_res["item_processing_time"] = round(time.time() - item_start, 3)
                eval_res["image_url"] = f"/labels/{img_file}" if img_file else ""

                # Update job counters
                status = eval_res["overall_status"]
                if status == "PASS":
                    job["passed_count"] += 1
                elif status == "REJECT":
                    job["rejected_count"] += 1
                elif status == "NEEDS REVIEW":
                    job["review_count"] += 1

                job["results"].append(eval_res)

            except Exception as e:
                logger.error(f"Error processing item {app_id}: {e}")
                job["failed_count"] += 1
                job["errors"].append({
                    "application_id": app_id,
                    "error": str(e)
                })

            job["processed_items"] += 1
            await asyncio.sleep(0.01)

        job["end_time"] = time.time()
        total_time = job["end_time"] - job["start_time"]
        job["average_time_per_label"] = round(total_time / max(job["processed_items"], 1), 3)
        job["status"] = "COMPLETED"

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        return self.jobs.get(job_id, {"error": "Job not found"})

batch_processor = BatchProcessor()
