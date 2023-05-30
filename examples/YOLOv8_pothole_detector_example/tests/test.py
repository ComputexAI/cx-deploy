import requests
from PIL import Image
import io

FILENAME = 'image_0.jpg'

def infer_with_params():
    url = 'http://localhost:8000/infer'
    files = {'input_file': open(FILENAME, 'rb')}
    response = requests.post(url, files=files)
    image_data = response.content
    image = Image.open(io.BytesIO(image_data))
    image.show()

infer_with_params()
