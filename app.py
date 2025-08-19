import json
from crypt import methods

from flask import Flask, request, jsonify
import os

from utils.get_summary import get_summarised_response
from utils.med_model import get_response
from utils import Image_Processor, med_model

UPLOAD_FOLDER = 'temp_uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
image_processor = Image_Processor()


@app.route('/response', methods=['POST']) #
def chatbot():
    data = request.form
    message = str(data['message'])
    chat_history = json.loads(data['chat_history'])

    med_responses = []

    if 'image' in request.files:
        file = request.files['image']
        filename = "original.png"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        classification = image_processor.classify_image(filepath)
        if classification == "pathology":
            image_processor.generate_patches(filepath, UPLOAD_FOLDER)

        images_path = os.path.join(UPLOAD_FOLDER)
        answer = med_model.get_response(message, images_path)   #not implemented yet
        med_responses.append(answer)

    else:
        answer = med_model.get_response(message)
        med_responses.append(answer)

    history_str = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in chat_history])

    answer = get_summarised_response(med_responses, history_str)

    return jsonify( { 'response' : answer } )

@app.route("/", methods=["GET"])
def index():
    return "Server is running"
