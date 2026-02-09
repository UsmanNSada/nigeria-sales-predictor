# Use python 3.9 slim (smaller & faster)
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# 1. Install System Dependencies
# libgomp1 -> Required for XGBoost
# libpq-dev & gcc -> Required for PostgreSQL driver
RUN apt-get update && apt-get install -y \
    libgomp1 \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 2. Copy Requirements and Install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy the rest of the app code
COPY . .

# 4. Run the App
# --host 0.0.0.0 is MANDATORY for Docker to be accessible from your browser
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]