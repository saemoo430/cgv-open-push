import requests
import queue
import time
import atexit
import multiprocessing
from cgv_open_push_function import *
from cgv_open_push_global_variable import *
from cgv_open_push_movie import movie_main
from cgv_open_push_screen import screen_main
from logging.handlers import RotatingFileHandler

message_queue = multiprocessing.Queue()
def send_telegram_message(text):

    url = (
        f"http://api.telegram.org/bot"
        f"{telegram_bot_token}/sendMessage"
    )
    payload = {
        "chat_id": telegram_chat_id,
        "text": text
    }
    try:
        requests.post(url, json=payload, timeout=10)
        print(f"Telegram sent: {text}")
    except Exception as e:
        print(f"Telegram Error: {e}")
 


def message_sender_loop():
    while True:
        if not message_queue.empty():
            message = message_queue.get()
            target_name = message[0]
            text = message[1]
            send_telegram_message(
                f"[{target_name}]\n{text}"
            )
        time.sleep(1)

# 프로세스 배열
processes = []

# 로그 저장 (최대 5MB씩 3개 백업본 저장)
handlers = [RotatingFileHandler('cgv-open-push.log', maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')]
logging.basicConfig(handlers=handlers, level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

# cgv_open_push_status.py 실행
p = multiprocessing.Process(target=run_cgv_open_push_status)
processes.append(p)
p.start()
time.sleep(1)

# 서버 시작 알림 보내기
message_queue.put(["LOG", "cgv-open-push server started..."])

# 영화관 프로세스 실행
for data in enumerate(movie_json_data):
    p = multiprocessing.Process(target=movie_main, args=(movie_url, movie_cookies, movie_headers, data[1], movie_target_name[data[0]], message_queue))
    processes.append(p)
    p.start()
    time.sleep(1)

# 특별관 프로세스 실행
for data in enumerate(screen_json_data):
    p = multiprocessing.Process(target=screen_main, args=(screen_url, screen_cookies, screen_headers, data[1], screen_target_name[data[0]], message_queue))
    processes.append(p)
    p.start()
    time.sleep(1)

# 종료 시 서버 종료 알림 보내기
def send_stopped_message():
    message_queue.put(["LOG", "cgv-open-push server stopped..."])
atexit.register(send_stopped_message)

message_sender_loop()
