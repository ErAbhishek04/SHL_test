# streamlit/Dockerfile

# Use Python base image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy streamlit files
COPY ./app.py /app
COPY ./requirements.txt /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose default Streamlit port
EXPOSE 8501

# Run Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
