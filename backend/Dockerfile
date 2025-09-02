FROM python:3.11-slim

# Set working directory
WORKDIR /code

# Install useful tools for debugging
RUN apt-get update && apt-get install -y \
    curl \
    netcat-openbsd \
    iputils-ping \
    libgl1 \
    libglib2.0-0 \
    poppler-utils \
    tesseract-ocr \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python -m pip install --upgrade pip

# Copy dependencies
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
COPY . .

# Set PYTHONPATH so apps is discoverable
ENV PYTHONPATH=/code

# Expose app port
EXPOSE 8000

# Run FastAPI app
CMD ["uvicorn", "apps.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
