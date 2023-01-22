import os
import io
import json
import pyautogui
import time
import threading
import requests
import base64

HTTP_SERVER_URL = 'http://127.0.0.1:80'

def now() -> int:
    return int(time.time() * 1000)

def screenshot_thread_function():
    delay_value = 0.3
    while True:
        time.sleep(delay_value)
        try:
            image = pyautogui.screenshot()
            image_bytes_array = io.BytesIO()
            image.save(image_bytes_array, 'PNG')
            screenshot_data = image_bytes_array.getvalue()
            base64_data = base64.b64encode(screenshot_data).decode('utf-8')
            request_body = {
                'type': 'screenshot',
                'payload': base64_data
            }
            requests.post(HTTP_SERVER_URL + '/screenshot', json = request_body)
            response = requests.get(HTTP_SERVER_URL + '/control')
            control = json.loads(response.text)
            for item in control:
                if item['type'] == 'mouse-click':
                    pyautogui.click(x=item['x'], y=item['y'])
            delay_value = 0.3
        except Exception as e:
            print('screenshot_thread_function exception: ', e.args[0])
            delay_value = 5

screenshot_thread = threading.Thread(target=screenshot_thread_function, args=())
screenshot_thread.start()


