import requests

FILENAME='short_clip.mp3'

def infer_with_params():
    url = 'http://localhost:8000/infer'
    files = {'input_file': open(FILENAME, 'rb')}
    data = {
        'params': '[{"name":"model_name", "value":"tiny"}, {"name":"input_type", "value":"text_input"}]'
    }
    response = requests.post(url, files=files, data=data)
    print(response.content)

infer_with_params()
