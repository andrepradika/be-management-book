FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the requirements file first
COPY requirements.txt .

# Install the requirements
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code
COPY . .

# Ensure the Alembic command can find the app module
ENV PYTHONPATH=/app

# Run Alembic migrations and start FastAPI
CMD ["sh", "-c", "alembic revision --autogenerate -m 'Migration' && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]
