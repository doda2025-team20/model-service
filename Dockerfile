# Dependency Stage
FROM python:3.12.9-slim

WORKDIR /sms

COPY pyproject.toml /sms/pyproject.toml
COPY src /sms/src

RUN pip install --no-cache-dir --prefer-binary /sms/

ENV MODEL_URL="https://github.com/doda2025-team20/model-service/releases/latest/download/model.zip"
ENV MODEL_PORT=8081
ENV DEBUG=false

EXPOSE ${MODEL_PORT}

ENTRYPOINT ["python", "src/serve_model.py"]
