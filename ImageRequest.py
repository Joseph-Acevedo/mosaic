import requests
import shutil

class ImageRequest:

    IMAGE_API_URL = "https://pixabay.com/api/"

    def __init__(self):
        self.num_images = -1
        self.req_data = None

    def set_search_params(self, token, num_images):
        self.num_images = num_images
        # Encodes the query in a url-safe way
        token = '+'.join(token.split(" "))
        self.req_data = {
            'key': "21347790-8576d8bf87e1821d2214055a7",
            'q': token
        }

    def run_request(self):
        response = requests.get(self.IMAGE_API_URL, params=self.req_data)
        if response.status_code != 200:
            print("[ERROR] Unexpected status code: {}. Aborting.".format(response.status_code))
            exit()
        data = response.json()
        hits = data['hits']

        for hit in hits:
            url = hit['previewURL']
            filename = self.get_name_from_preview_url(hit['previewURL'])
            r = requests.get(url, stream=True)
            if response.status_code != 200:
                continue
            with open(filename, 'wb') as f:
                # Saves the iamge to a file, change to a different way in order to send back
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)

    def get_name_from_preview_url(self, preview_url):
        tokens = preview_url.split("/")
        return tokens[-1]

"""
im = ImageRequest()
im.set_search_params("cars", 2)
im.run_request()
"""



    