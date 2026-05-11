FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake curl git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir fastapi uvicorn[standard] pydantic huggingface_hub llama-cpp-python

COPY ai_service.py /app/ai_service.py

CMD ["uvicorn", "ai_service:app", "--host", "0.0.0.0", "--port", "8099"]
