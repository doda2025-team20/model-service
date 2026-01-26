"""
Flask API of the SMS Spam detection model model.
"""
import joblib
from flask import Flask, jsonify, request
from flasgger import Swagger
import pandas as pd
import os
import requests
import zipfile

from text_preprocessing import prepare, _extract_message_len, _text_process

app = Flask(__name__)
swagger = Swagger(app)

def model_version_url(version=None):
    if version is None or version == "latest":
        return "https://github.com/doda2025-team20/model-service/releases/latest/download/model.zip"
    else:
        return f"https://github.com/doda2025-team20/model-service/releases/download/{version}/model.zip"

def get_model(version=None):
    model_path = 'output/model.joblib'
    if os.path.exists(model_path):
        print("[model] Model already exists, skipping download.")
        return
    
    if version is None:
        raise ValueError("[model] Model Version must be provided if model file does not exist, through environment variable MODEL_VERSION. 'latest' can be used to get the latest version.")
    
    print(f"[model] Model not found, downloading {version}...")

    try:
      url = model_version_url(version)
      r = requests.get(url)
      r.raise_for_status()
      with open("model.zip", "wb") as f:
          f.write(r.content)

      with zipfile.ZipFile("model.zip", "r") as zip_ref:
          zip_ref.extractall()
      os.remove("model.zip")
      print("[model] Model downloaded and extracted successfully.")
    except Exception as e:
      raise RuntimeError(f"Failed to download or extract the model: {e}")

@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict whether an SMS is Spam.
    ---
    consumes:
      - application/json
    parameters:
        - name: input_data
          in: body
          description: message to be classified.
          required: True
          schema:
            type: object
            required: sms
            properties:
                sms:
                    type: string
                    example: This is an example of an SMS.
    responses:
      200:
        description: "The result of the classification: 'spam' or 'ham' with confidence."
    """
    input_data = request.get_json()
    sms = input_data.get('sms')
    processed_sms = prepare(sms)
    model = joblib.load('output/model.joblib')
    
    # Get prediction
    prediction = model.predict(processed_sms)[0]
    
    # Get confidence scores (probabilities for each class)
    probabilities = model.predict_proba(processed_sms)[0]
    
    # Get the confidence for the predicted class
    # If prediction is "ham" (class 0), use probabilities[0]
    # If prediction is "spam" (class 1), use probabilities[1]
    if prediction == "ham":
        confidence = float(probabilities[0])
    else:  # spam
        confidence = float(probabilities[1])
    
    res = {
        "result": prediction,
        "confidence": confidence,
        "classifier": "decision tree",
        "sms": sms
    }
    print(res)
    return jsonify(res)

@app.route('/bulk', methods=['POST'])
def predict_bulk():
    """
    Predict the spam status of multiple SMS messages.
    ---
    consumes:
      - application/json
    parameters:
        - name: input_data
          in: body
          description: messages to be classified.
          required: True
          schema:
            type: object
            required: bulk
            properties:
                bulk:
                    type: array
                    items:
                      type: string
                    example: ["This is an example of an SMS.", "Another example SMS."]
    responses:
      200:
        description: "The results of the classification for each SMS."
    """
    input_data = request.get_json()
    bulk = input_data.get('bulk')
    # processed_bulk = prepare(bulk)
    # model = joblib.load('output/model.joblib')
    # prediction = model.predict(processed_sms)[0]
    
    # res = {
    #     "result": prediction,
    #     "classifier": "decision tree",
    #     "sms": sms
    # }
    # print(res)

    res = []
    model = joblib.load('output/model.joblib')

    for sms in bulk:
        processed_sms = prepare(sms)
        prediction = model.predict(processed_sms)[0]
        res.append({
            "result": prediction,
            "classifier": "decision tree",
            "sms": sms
        })

    print(res)

    return jsonify(res)

if __name__ == '__main__':
    #clf = joblib.load('output/model.joblib')
    port = int(os.environ.get("MODEL_PORT", 8081))
    model_url = os.environ.get("MODEL_URL", None)
    model_version = os.environ.get("MODEL_VERSION", "latest")
    if model_url:
        print(f"[model] MODEL_URL is unsupported. Please use MODEL_VERSION instead. {model_version} will be downloaded.")
    is_debug = os.environ.get("DEBUG", "false").lower() == "true"

    get_model(version=model_version)

    app.run(host="0.0.0.0", port=port, debug=is_debug)
