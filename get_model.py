import zipfile
import urllib.request
urllib.request.urlretrieve("https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip", "vosk-model-small-ru-0.22.zip")
with zipfile.ZipFile('vosk-model-small-ru-0.22.zip', 'r') as zip_ref:
    zip_ref.extractall('./')
