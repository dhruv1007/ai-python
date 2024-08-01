from flask import Flask, request, jsonify
from flask_cors import CORS
from google.cloud import secretmanager
import google.generativeai as genai
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Replace with your secret name and project ID
SECRET_NAME = "gemini-api-key"
PROJECT_ID = os.getenv('PROJECT_ID')

def get_api_key_from_secret_manager(secret_name, PROJECT_ID):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(name=name)
    secret_string = response.payload.data.decode("UTF-8")
    return secret_string

# Retrieve API key from Secret Manager
API_KEY = get_api_key_from_secret_manager(SECRET_NAME, PROJECT_ID)

# Configure the generative AI library
genai.configure(api_key=API_KEY)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'Application is running'}), 200

@app.route('/generate', methods=['POST'])
def generate_text():
    data = request.get_json()
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400

    try:
        response = genai.generate_text(prompt=prompt)
        result = response.result if response.result else 'No text found in response'
        return jsonify({'response': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
