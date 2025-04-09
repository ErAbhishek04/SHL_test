# backend/Dockerfile

# Use Python base image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy only backend files
COPY ./backend /app/backend
COPY ./requirements.txt /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose FastAPI port
EXPOSE 8080

# Run FastAPI app
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
