import base64
import json                    

import requests

api = 'http://localhost:8080/media'
image_file = 'test_images/class.jpg'

with open(image_file, "rb") as f:
    im_bytes = f.read()        
im_b64 = base64.b64encode(im_bytes).decode("utf8")

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
  
payload = json.dumps({"mediaId": -1, "imgBytes": im_b64, "title": "Classroom Of The Elite", "bookmark":139, "rating":8, "notes":"test notee", "medium":"ANIME", "imgExtension":".jpg"})

response = requests.post(api, data=payload, headers=headers)
# response = requests.put(api, data = payload, headers=headers)
# response = requests.delete(api)
# response = requests.get(api)
# print(response.json()["totalPages"])