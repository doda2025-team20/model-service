# SMS Checker / Backend

The backend of this project provides a simple REST service that can be used to detect spam messages.
We have extended the base project [rohan8594/SMS-Spam-Detection](https://github.com/rohan8594/SMS-Spam-Detection), which introduces several basic classification models, and wrap one of them in a microservice.

The following sections will explain you how to get started.
The project **requires a Python 3.12 environment** to run (tested with 3.12.9).
Use the `requirements.txt` file to restore the required dependencies in your environment.


### Training the Model

To train the model, you have two options.
Either you create a local environment...

    $ python -m venv venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt

... or you train in a Docker container (recommended):

    $ docker run -it --rm -v ./:/root/sms/ python:3.12.9-slim bash
    ... (container startup)
    $ cd /root/sms/
    $ pip install -r requirements.txt

Once all dependencies have been installed, the data can be preprocessed and the model trained by creating the output folder and invoking three commands:

    $ mkdir output
    $ python src/read_data.py
    Total number of messages:5574
    ...
    $ python src/text_preprocessing.py
    [nltk_data] Downloading package stopwords to /root/nltk_data...
    [nltk_data]   Unzipping corpora/stopwords.zip.
    ...
    $ python src/text_classification.py

The resulting model files will be placed as `.joblib` files in the `output/` folder.


### Serving Recommendations

To make the models accessible, you need to start the microservice by running the `src/serve_model.py` script from within the virtual environment that you created before, or in a fresh Docker container (recommended):

    $ docker run -it --rm -p 8081:8081 -v ./:/root/sms/ python:3.12.9-slim bash
    ... (container startup)
    $ cd /root/sms/
    $ pip install -r requirements.txt
    $ python src/serve_model.py

The server will start on port 8081.
Once its startup has finished, you can either access [localhost:8081/apidocs](http://localhost:8081/apidocs) in your browser to interact with the service, or you send `POST` requests to request predictions, for example with `curl`:


    $ curl -X POST "http://localhost:8081/predict" -H "Content-Type: application/json" -d '{"sms": "test ..."}'
    {
      "classifier": "decision tree",
      "result": "ham",
      "sms": "test ..."
    }

## Running the Backend via Docker

A built container image is published to GitHub Container Registry (GHCR).

Pull the image
```bash
docker pull ghcr.io/doda2025-team20/model-service:latest
```

If the repository is private, authenticate first:

```bash
echo "<GHCR_PAT>" | docker login ghcr.io -u <github-username> --password-stdin
```

Run the container
```bash
docker run \
  -p 8081:8081 \
  ghcr.io/doda2025-team20/model-service:latest
```

The service becomes available on:
```bash
http://localhost:8081/apidocs
```

## Configurable runtime parameters

The Dockerfile defines:

```bash
ENV MODEL_PORT=8081
ENV DEBUG=false
```

These settings can be overridden at runtime:

```bash
docker run -e DEBUG=true -e MODEL_PORT=9000 -p 9000:9000 ...
```

The container starts using:

```bash
ENTRYPOINT ["python", "src/serve_model.py"]
```

This keeps behavior predictable and avoids the need to manually specify commands when deploying.

## Release Process

### Container Images

Container images are automatically built and published to GHCR when changes are pushed to the `main` branch. The behavior depends on the version specified in `pyproject.toml`:

- **Release Version** (e.g., `0.1.0`): If the version is incremented and does not contain a hyphen, a new Git tag `v0.1.0` is created, and the image is published with the `0.1.0` tag and `latest`.
- **Snapshot Version** (e.g., `0.1.0-dev`): If the version contains a hyphen, a snapshot image is built with the tag `snapshot-<commit-sha>`. This allows for testing without releasing a stable version.

### Model Training

The model training process is decoupled from the application release. You can manually trigger the **Train and Release Model** workflow from the GitHub Actions tab. This workflow will:

1. Train the model using the current code.
2. Package the model artifacts.
3. Create a GitHub Release tagged `model-<version>` containing the trained model.
