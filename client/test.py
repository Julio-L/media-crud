import base64
import json                    

import requests

api = 'http://localhost:8080/media'
image_file = 'img2.jpeg'

with open(image_file, "rb") as f:
    im_bytes = f.read()        
im_b64 = base64.b64encode(im_bytes).decode("utf8")

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
  
payload = json.dumps({"mediaId": 2, "imgBytes": im_b64, "title": "Attack On Titan", "bookmark":139, "rating":10, "notes":"test notee", "medium":"ANIME", "imgExtension":".jpeg"})
# response = requests.post(api, data=payload, headers=headers)

response = requests.put(api, data = payload, headers=headers)