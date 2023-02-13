import subprocess
import os
import io
import json
import time
import threading
import requests
import base64

from PIL import ImageGrab
import pyautogui

from dotenv import load_dotenv
load_dotenv()

#HTTP_SERVER_URL = 'https://pyrd.dsi.su'
HTTP_SERVER_URL: str = os.getenv('HTTP_SERVER_URL') or None

#proxies = {
    #'https' : 'https://s.dolganuk:user2026@srvtmg.ctt.com.mps:8080',
#    'http' : 'https://s.dolganuk:user2026@srvtmg.ctt.com.mps:8080'
#}
#, proxies=proxies

def now() -> int:
    return int(time.time() * 1000)

def screenshot_thread_function():
    delay_value = 0.3
    altprintscreen_mode: bool = False
    while True:
        time.sleep(delay_value)
        try:
            if altprintscreen_mode:
                pyautogui.press("printscreen")
                time.sleep(0.1)
                image = ImageGrab.grabclipboard()
            else:
                image = pyautogui.screenshot()
            image_bytes_array = io.BytesIO()
            if image:
                image.save(image_bytes_array, 'PNG')
                screenshot_data = image_bytes_array.getvalue()
                base64_data = base64.b64encode(screenshot_data).decode('utf-8')
                request_body = {
                    'type': 'screenshot',
                    'payload': base64_data
                }
                result = requests.post(HTTP_SERVER_URL + '/screenshot', json = request_body)
            response = requests.get(HTTP_SERVER_URL + '/control')
            control = json.loads(response.text)
            for item in control:
                if item['type'] == 'mouse-move':
                    pyautogui.moveTo(item['x'], item['y'])
                if item['type'] == 'mouse-click':
                    pyautogui.click(x=item['x'], y=item['y'])
                if item['type'] == 'mouse-click-right':
                    pyautogui.click(x=item['x'], y=item['y'], button='right')
                if item['type'] == 'mouse-double-click':
                    pyautogui.click(x=item['x'], y=item['y'], clicks=2, interval=0.25)
                if item['type'] == 'swapmode':
                    altprintscreen_mode = not altprintscreen_mode
                if item['type'] == 'press':
                    pyautogui.press(item['command'])
                if item['type'] == 'run':
                    subprocess.run(item['command'])
                    #'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe https://us05web.zoom.us/j/3763055085?pwd=S1Z4Qk1mdW9yd3h2RzdDM2xiNTEzQT09'
            delay_value = 1
        except Exception as e:
            print('screenshot_thread_function exception: ', e.args[0])
            delay_value = 5

screenshot_thread = threading.Thread(target=screenshot_thread_function, args=())
screenshot_thread.start()


