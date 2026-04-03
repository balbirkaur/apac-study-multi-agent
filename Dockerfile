# Use Python
FROM python:3.11

# Set working dir
WORKDIR /app

# Copy files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Start app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]