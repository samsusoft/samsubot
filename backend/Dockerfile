FROM python:3.11

# Set working directory
WORKDIR /apps

# Copy code
COPY . .

# Add this line to help Python discover local modules
ENV PYTHONPATH=/apps

# Upgrade pip
RUN python -m pip install --upgrade pip

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set PYTHONPATH so that `apps` becomes discoverable
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Run FastAPI app
CMD ["uvicorn", "apps.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
