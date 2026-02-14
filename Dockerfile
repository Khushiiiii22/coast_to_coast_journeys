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
# Adjust the path to app:app based on your structure. 
# Since app.py is in backend/app.py, user runs "python backend/app.py"
# We need to make sure gunicorn can find the app factory or instance.
CMD ["gunicorn", "--bind", ":8080", "--workers", "1", "--threads", "8", "--timeout", "180", "--chdir", "backend", "app:create_app()"]
