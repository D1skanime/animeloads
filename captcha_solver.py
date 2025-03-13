import time
import json
import hashlib
import cv2
import numpy
import shutil
				  

def doCaptcha(cID, driver, session, b64):
    captcha_baseURL = "https://www.anime-loads.org/files/captcha"
    img_baseURL = captcha_baseURL + "?cid=0&hash="

    print("Getting captcha images")

    js = "var xhr2 = new XMLHttpRequest(); \
    xhr2.open('POST', 'https://www.anime-loads.org/files/captcha', false); \
    xhr2.setRequestHeader('Content-type', 'application/x-www-form-urlencoded'); \
    xhr2.send('cID=0&rT=1'); \
    return xhr2.response;"

    ajaxresponse = driver.execute_script(js)
    captchaIDs = ajaxresponse.replace("\"", "").replace("[", "").replace("]", "").split(",")

    request_cookies_browser = driver.get_cookies()
    c = [session.cookies.set(c['name'], c['value']) for c in request_cookies_browser]

    images = []
    images_url = []
    correct_index = -1

    session.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
    }

    for c in captchaIDs:
        url = img_baseURL + c
        images_url.append(c)
        response = session.get(url, stream=True, headers=headers)
        images.append(response.content)

    print("Got captcha images")

    print("Calculating correct captcha")

    cv_images = []
    for image in images:
        nparr = numpy.frombuffer(image, numpy.uint8)
        img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        cv_images.append(img_np)

    perc = []
    for img in cv_images:
        iPerc = 0
        for i in cv_images:
            if hashlib.md5(i).digest() == hashlib.md5(img).digest():
                pass
            else:
                iPerc += getDifference(img, i)
        perc.append(iPerc)

    biggest = 0
    bigI = -1
    for idx, iPerc in enumerate(perc):
        print("Percentage img " + str(idx) + ": " + str(iPerc))
        if iPerc > biggest:
            biggest = iPerc
            bigI = idx

    print("Correct captcha: Image Nr. " + str(bigI + 1) + " with a confidence of " + str(biggest))

    print("Checking if captcha is correct")

    capURL = captcha_baseURL + "?cID=0&pC=" + images_url[bigI] + "&rT=2"
    js = "var xhr2 = new XMLHttpRequest(); \
    xhr2.open('POST', '" + captcha_baseURL + "', false); \
    xhr2.setRequestHeader('Content-type', 'application/x-www-form-urlencoded'); \
    xhr2.send('cID=0&pC=" + images_url[bigI] + "&rT=2'); \
    return xhr2.response;"

    ajaxresponse = driver.execute_script(js)		   

    response_json = json.loads(ajaxresponse)

    return response_json

def getDifference(img1, img2):
    res = cv2.absdiff(img1, img2)
    res = res.astype(numpy.uint8)
    percentage = (numpy.count_nonzero(res) * 100) / res.size
    return percentage

if __name__ == "__main__":
    print("Teste Captcha Solver... (kein vollständiger Test möglich ohne Webbrowser)")