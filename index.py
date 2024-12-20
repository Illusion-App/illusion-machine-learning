from flask import Flask, request, jsonify
from waitress import serve
import os
import numpy as np
import tensorflow as tf
from keras.utils import load_img, img_to_array
import json

# Threshold Classification
THRESHOLD = 0.5

# Load the ML model
model = tf.keras.models.load_model('./model/final_model.h5')

# Image labels
labels = {0: 'Fake',
          1: "Real"}

# Used to preprocess images into array before predicting them
def preprocess_image(image_path):
    image = load_img(image_path, target_size=(256, 256))
    image = img_to_array(image)
    image = image / 255.0
    image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))
    return image

# Used to predict the images' class
def predict_image(image):
    prediction = model.predict(image, verbose=0)
    confidence = float(prediction[0, 0])
    predicted_label = 1 if confidence > THRESHOLD else 0

    if predicted_label == 0:  # Fake
        confidence = 1 - confidence

    return labels.get(predicted_label), confidence

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1000 * 1000

@app.route("/predict", methods=['POST'])
def index():
    if request.method == 'POST':
        # Try (jika request valid)
        try:
            image_file = request.files['image']
            image_file.save('uploaded_image.jpg')

            image = preprocess_image('uploaded_image.jpg')
            predicted_label, confidence = predict_image(image)

            result = {
            "status": "success",
            "message": "Prediction completed",
            "data": {
                "predicted_label": predicted_label,
                "confidence": confidence
                }
            }
            return jsonify(result)
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

# Memulai Server
if __name__ == "__main__":
    print("Server: http://0.0.0.0:8080")
    serve(app, host="0.0.0.0", port=8080)