import os
import sys
import time
import requests
from dotenv import load_dotenv

def resource_path(relative_path):
    """Get absolute path to resource, works for PyInstaller and development."""
    try:
        # If running as a PyInstaller bundle
        base_path = sys._MEIPASS
    except AttributeError:
        # If running locally (not bundled)
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Load the .env file
env_path = resource_path(".env")
load_dotenv(env_path)

load_dotenv()

# Obtener el dominio de la API desde las variables de entorno
API_BASE_URL = os.getenv("API_BASE_URL")

def watch_folder(folder_path, stop_event, comm, start_time):
    """Vigila la carpeta especificada en busca de nuevos archivos de audio."""
    processed_files = set()  # Seguimiento de archivos procesados

    while not stop_event.is_set():  # Verifica si se debe detener el proceso
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)

                # Verificar si el archivo es de audio
                if file.lower().endswith(('.mp3', '.wav', '.m4a')):
                    mod_time = os.path.getmtime(file_path)

                    # Saltar si el archivo ya fue procesado o es antiguo
                    if mod_time < start_time or file_path in processed_files:
                        continue

                    processed_files.add(file_path)
                    comm.log_message_signal.emit(f"Nuevo audio detectado: {file_path}")

                    try:
                        # Solicitar la URL prefirmada desde el backend
                        presigned_url = get_presigned_url(file)
                        comm.log_message_signal.emit(f"Subiendo audio a: {presigned_url}")

                        # Subir el archivo a la URL prefirmada
                        upload_file(file_path, presigned_url)
                        comm.log_message_signal.emit(f"Audio subido: {file_path}")
                    except Exception as e:
                        comm.log_message_signal.emit(f"Error: {str(e)}")

        time.sleep(5)  # Esperar antes de volver a verificar


def get_presigned_url(file_name):
    try:
        response = requests.get(
            f"{API_BASE_URL}/get_presigned",
            params={"file_name": file_name, "file_type": "audio/mpeg"}
        )
        response.raise_for_status()
        return response.json().get("url")
    except requests.RequestException as e:
        raise Exception(f"Error al obtener la URL prefirmada: {str(e)}")


def upload_file(file_path, presigned_url):
    """Sube un archivo a la URL prefirmada."""
    try:
        with open(file_path, 'rb') as f:
            response = requests.put(presigned_url, data=f, headers={'Content-Type': 'audio/mpeg'})
            print(f"Response: {response.status_code}, {response.text}")
            response.raise_for_status()
    except requests.RequestException as e:
        raise Exception(f"Error al subir el archivo: {str(e)}")
