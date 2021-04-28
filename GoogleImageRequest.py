from bs4 import BeautifulSoup
import requests
from io import BytesIO
import cv2
from PIL import Image
import numpy as np
from time import perf_counter
from concurrent.futures import ThreadPoolExecutor


TEMPLATE = "https://www.google.com/search?q={}&safe=strict&tbm=isch"

buffer_size = 1024          # in bytes

def get_url_from_tag(tag):
    components = str(tag).split(" ")
    src = ""
    for comp in components:
        if comp.startswith("src"):
            src = comp
            break
    return src.split("\"")[1]

def request_img(url):
    r = requests.get(url)
    if r.status_code != 200:
        return

    img = Image.open(BytesIO(r.content)).convert('RGB')
    cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)



"""
Each image takes 0.12-0.15s to request and convert
"""
def get_images(token, n_threads):
    response = requests.get(TEMPLATE.format(token))
    if response.status_code != 200:
        print(f"Bad return code! {response.status_code}")
        exit()

    data = response.text

    soup = BeautifulSoup(data, "html.parser")
    image_tags = soup.findAll('img')

    imgs_to_request = []
    for tag in image_tags:
        url = get_url_from_tag(tag)
        if not url.startswith('http'):
            continue
        imgs_to_request.append(url)

    t = perf_counter()
    with ThreadPoolExecutor(max_workers=n_threads) as pool:
        pool.map(request_img, imgs_to_request)

    return int((perf_counter() - t) * 1000)

# 25 threads got to 178ms for 20 images 
def min_threads(token):
    for i in range(1, 30):
        time = get_images(token, i)
        print(f"{i} Threads took {time} ms")



        


min_threads("cars")


