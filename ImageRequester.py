"""
Author: Joseph Acevedo
Project: You, a Mosaic of Concepts
File: ImageRequester.py
Purpose: a call to get_images will populate the given 2-D array with images from the
    internet based on the search token given. Multiple threads are used in order to 
    utilize external I/O wait time
"""

from bs4 import BeautifulSoup
import requests
from io import BytesIO
import cv2
from PIL import Image
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed


GOOGLE_TEMPLATE = "https://www.google.com/search?q={}&safe=strict&tbm=isch&sclient=img"
BING_TEMPLATE = "https://www.bing.com/images/search?q={}&form=HDRSC3&first=1&tsc=ImageBasicHover"


"""
Simple string parsing to grab a url form an HTML img tag
"""
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
def request_img(data):
    url = data[0]
    r = requests.get(url)
    if r.status_code != 200:
        return

    img = Image.open(BytesIO(r.content)).convert('RGB')
    cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    cv_img = cv2.resize(cv_img, (100, 100))
    return (cv_img, data[1])

"""
Each image takes 120-150ms to request and convert
token: the string query
img_dest: the 2-D array to hold the imgs
img_locs: a list of coords for each image, so as to not overwrite images or create
    race conditions
template: the url template to use for requesting images, must be formattable (q={})
"""
def get_images(token, img_dest, img_locs, template=BING_TEMPLATE):
    response = requests.get(template.format(token))
    if response.status_code != 200:
        print(f"Couldn't connect to web server! Code {response.status_code}")
        exit()

    data = response.text

    soup = BeautifulSoup(data, "html.parser")
    image_tags = soup.findAll('img')

    img_loc_idx = 0
    imgs_to_request = []    # contains (url, coord) pairs
    num_imgs = len(img_locs)
    for tag in image_tags:
        if img_loc_idx >= num_imgs:
            break
        url = get_url_from_tag(tag)
        if not url.startswith('http'):
            continue
        coord = img_locs[img_loc_idx]
        img_loc_idx += 1

        imgs_to_request.append( (url, coord) )

    with ThreadPoolExecutor(max_workers=num_imgs) as pool:
        futures = []
        for data in imgs_to_request:
            futures.append(pool.submit(request_img, data=data))
        for future in as_completed(futures):
            result = future.result()
            coord = result[1]
            img_dest[coord[0], coord[1]] = result[0]

    return img_dest

