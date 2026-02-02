#!/usr/bin/env python3
"""
Setup script to download the Vosk model for Larynx ASR tool.
"""

import urllib.request
import zipfile
import os

def download_vosk_model():
    url = "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip"
    zip_path = os.path.join("models", "vosk-model-en-us-0.22.zip")
    model_dir = "models"

    # Create models directory if it doesn't exist
    os.makedirs(model_dir, exist_ok=True)

    print("Downloading Vosk model (vosk-model-en-us-0.22)... This may take a while (1.8GB).")

    try:
        urllib.request.urlretrieve(url, zip_path)
        print("Download complete. Extracting...")

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(model_dir)

        # Remove the zip file
        os.remove(zip_path)
        print("Model downloaded and extracted successfully to models/vosk-model-en-us-0.22/")

    except Exception as e:
        print(f"Error downloading or extracting model: {e}")
        if os.path.exists(zip_path):
            os.remove(zip_path)

if __name__ == "__main__":
    download_vosk_model()