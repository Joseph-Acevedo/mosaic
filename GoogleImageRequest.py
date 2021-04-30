from bs4 import BeautifulSoup
import requests
from io import BytesIO
import cv2
from PIL import Image
import numpy as np
import random
from time import perf_counter
from concurrent.futures import ThreadPoolExecutor


GOOGLE_TEMPLATE = "https://www.google.com/search?q={}&safe=strict&tbm=isch&sclient=img"
BING_TEMPLATE = "https://www.bing.com/images/search?q={}&form=HDRSC3&first=1&tsc=ImageBasicHover"


def get_url_from_tag(tag):
    components = str(tag).split(" ")
    src = ""
    for comp in components:
        if comp.startswith("src"):
            src = comp
            break
    return src.split("\"")[1]

"""
Given a URL, streams the image and converts into 3-D np matrix
"""
def request_img(url):
    r = requests.get(url)
    if r.status_code != 200:
        return

    img = Image.open(BytesIO(r.content)).convert('RGB')
    cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

"""
Each image takes 120-150ms to request and convert
Requests images from the internet using token as the query
"""
def get_images(token, template=BING_TEMPLATE):
    response = requests.get(template.format(token))
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

    n_imgs = len(imgs_to_request)
    with ThreadPoolExecutor(max_workers=n_imgs) as pool:
        pool.map(request_img, imgs_to_request)

    return n_imgs
        
bing_count = get_images("cars bars")
print(bing_count)


