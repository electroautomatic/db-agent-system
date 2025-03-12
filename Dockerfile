FROM python:3.10-slim

WORKDIR /

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create the app directory structure
RUN mkdir -p /app

# Python will search modules from the working directory
ENV PYTHONPATH=/

CMD ["python", "-m", "app.database.main"] 