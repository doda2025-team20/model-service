# Dependency Stage
FROM python:3.12.9-slim

WORKDIR /sms

COPY requirements.txt /sms/requirements.txt
COPY src /sms/src

RUN pip install --no-cache-dir --prefer-binary -r /sms/requirements.txt

ENV MODEL_URL="https://github.com/doda2025-team20/model-service/releases/latest/download/model.zip"
ENV MODEL_PORT=8081
ENV DEBUG=false

EXPOSE ${MODEL_PORT}

ENTRYPOINT ["python", "src/serve_model.py"]
