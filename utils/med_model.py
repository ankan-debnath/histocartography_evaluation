import requests
import os
from dotenv import load_dotenv

load_dotenv()

MED_SERVICE_URI = os.getenv("MED_SERVICE_URI")

def get_response(message, images_path=None):
    # Prepare the form data
    data = {"message": message, "chat_history" : ""}

    files = []
    if images_path is not None:
        if not os.path.exists(images_path):
            return {"error": f"Image file not found at {images_path}"}

        for image_name in os.listdir(images_path):
            image_path = os.path.join(images_path, image_name)
            files.append(("image", (image_name,  open(image_path, "rb"))))

    try:
        response = requests.post(MED_SERVICE_URI+"/response", data=data, files=files)

        for _, (fname, fobj) in files:
            fobj.close()

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Error from API: {response.status_code} - {response.text}"}

    except Exception as e:
        return {"error": str(e)}