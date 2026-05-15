FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Fix Windows line endings (CRLF) in all scripts
RUN apt-get update && apt-get install -y sed && \
    find scripts/ -type f -exec sed -i 's/\r$//' {} + && \
    chmod +x scripts/entrypoint.sh

EXPOSE 8000

# Use 'sh' to run the script to avoid shebang line ending issues
ENTRYPOINT ["sh", "scripts/entrypoint.sh"]