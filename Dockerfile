# Dependency Stage
FROM python:3.12.9-slim AS deps

WORKDIR /sms
COPY requirements.txt /sms/requirements.txt
RUN pip install --no-cache-dir --prefer-binary -r /sms/requirements.txt

# Training Stage
FROM deps AS training

WORKDIR /sms
COPY . /sms

RUN mkdir -p /sms/output

RUN python src/text_preprocessing.py

RUN python src/text_classification.py

# Runtime Stage
FROM deps AS runtime

WORKDIR /sms

COPY . /sms/
COPY --from=training /sms/output /sms/output

ENTRYPOINT ["python", "src/serve_model.py"]

EXPOSE 8081
