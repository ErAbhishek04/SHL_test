# Use Python base image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy all files to container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8080

# Run FastAPI app inside backend folder
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
