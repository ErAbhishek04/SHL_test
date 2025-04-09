# backend/Dockerfile

FROM python:3.13-slim

WORKDIR /app

# First copy and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Now copy all source files (from the current directory)
COPY . .

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
