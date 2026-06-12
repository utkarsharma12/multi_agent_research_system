# ==========================================
# Stage 1: Build the Next.js Frontend
# ==========================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./
RUN npm install

# Copy frontend source and build
COPY frontend/ .
RUN npm run build

# ==========================================
# Stage 2: Build the FastAPI Backend
# ==========================================
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend source code
COPY backend/ ./backend/

# Copy the built frontend static files from Stage 1 into the location main.py expects
COPY --from=frontend-builder /app/frontend/out ./frontend/out

# Expose the port (Render sets the PORT env var dynamically)
EXPOSE 8000

# Start Uvicorn from the backend directory using the PORT variable
WORKDIR /app/backend
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"
