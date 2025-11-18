# Training Stage
FROM python:3.12.9-slim AS training

WORKDIR /sms
COPY . /sms

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /sms/output

RUN python src/text_preprocessing.py

RUN python src/text_classification.py

# Runtime Stage
FROM python:3.12.9-slim AS runtime

WORKDIR /sms

COPY . /sms/
COPY --from=training /sms/output /sms/output

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "src/serve_model.py"]

EXPOSE 8081
