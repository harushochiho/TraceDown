# Dockerfile - development-friendly for TraceDown
FROM python:3.12-slim

# Avoid warnings and set a consistent locale
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install OS deps (if needed), pip tools and install requirements
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy pip requirements and install
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

# Copy project
COPY . /app

# Copy entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Collect static (optional for dev; run on container start in prod)
# RUN python manage.py collectstatic --noinput

EXPOSE 8800

# Use entrypoint to run migrate then server
ENTRYPOINT ["/app/entrypoint.sh"]
