# TTB Label Compliance Review Assistant Dockerfile
FROM python:3.11-slim

# Prevent Python from writing bytecode and buffer outputs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies including Tesseract OCR and OpenCV graphics libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libtesseract-dev \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency definition and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source files
COPY . .

# Generate sample label artwork and CSV datasets inside container
RUN python3 generate_samples.py

# Expose FastAPI server port
EXPOSE 8000

# Run FastAPI server with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
