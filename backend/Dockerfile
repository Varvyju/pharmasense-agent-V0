FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements (repo-root-relative)
COPY backend/requirements.txt ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r ./requirements.txt

# Copy app code and data (repo-root-relative)
COPY backend/app/ ./app/
# Place data at /data so the app's DATA_DIR (which resolves to /data) can find it
COPY data/ /data/

# Expose port
EXPOSE 8000

# Run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
