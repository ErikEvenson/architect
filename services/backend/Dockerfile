FROM python:3.12-slim AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
    graphviz \
    curl \
    make \
    fonts-dejavu-core \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    && curl -fsSL https://d2lang.com/install.sh | sh -s -- \
    && apt-get purge -y --auto-remove make \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ /app/src/
COPY knowledge/ /app/knowledge/

RUN useradd -r -u 1000 architect && \
    mkdir -p /app/data/outputs /app/model-cache/onnx && \
    chown -R architect:architect /app

# Download pre-exported ONNX model for all-MiniLM-L6-v2 from HuggingFace
# No PyTorch needed — uses onnxruntime + tokenizers at runtime (~300MB vs ~3GB)
ENV EMBEDDING_MODEL_DIR=/app/model-cache/onnx
RUN HF_BASE="https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main" && \
    curl -sL "$HF_BASE/onnx/model.onnx" -o /app/model-cache/onnx/model.onnx && \
    curl -sL "$HF_BASE/tokenizer.json" -o /app/model-cache/onnx/tokenizer.json && \
    curl -sL "$HF_BASE/config.json" -o /app/model-cache/onnx/config.json

USER architect

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import socket; s=socket.create_connection(('localhost',8000),3); s.close()" || exit 1

ENV PYTHONPATH=/app
CMD ["python", "-m", "src.main"]
