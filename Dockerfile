FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    default-libmysqlclient-dev \
    build-essential \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Fix Windows line endings (CRLF) in all scripts and python files
RUN find . -type f -name "*.sh" -exec dos2unix {} + && \
    find . -type f -name "*.py" -exec dos2unix {} + && \
    chmod +x scripts/entrypoint.sh

EXPOSE 8000

# Use 'sh' to run the script to avoid shebang line ending issues
ENTRYPOINT ["sh", "scripts/entrypoint.sh"]