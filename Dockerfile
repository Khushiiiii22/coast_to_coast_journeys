# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirement file first to leverage Docker cache
COPY backend/requirements.txt requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Run the application with Gunicorn
# app.py has both create_app() factory and app instance at module level
# Use app:app to reference the pre-created instance for faster startup
CMD ["gunicorn", "--bind", ":8080", "--workers", "2", "--threads", "4", "--timeout", "300", "--preload", "--chdir", "backend", "app:app"]
