FROM python:3.10-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set PYTHONPATH to include the backend directory
ENV PYTHONPATH=/app

CMD ["python", "-m", "backend.entrypoint.app"]