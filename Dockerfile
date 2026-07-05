FROM python:3.11-slim

WORKDIR /usr/src/app

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p 06_memory

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request, sys; sys.exit(0 if urllib.request.urlopen('http://localhost:' + __import__('os').environ.get('PORT', '8000') + '/health').getcode() == 200 else 1)"

CMD ["sh", "-c", "uvicorn bridge:app --host 0.0.0.0 --port ${PORT:-8000}"]