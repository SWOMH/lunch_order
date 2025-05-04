import requests
from constant import CONSTANT

class Telegram:

    def __init__(self):
        self.CHAT_ID = CONSTANT.CHAT_ID
        self.TOKEN = CONSTANT.BOT_TOKEN
        self.url = f"https://api.telegram.org/bot{self.TOKEN}/sendMessage"


    def send_message(self, message: str, id=''):
        if id:
            params = {
                'chat_id': id,
                'text': message
            }
        else:
            params = {
                'chat_id': self.CHAT_ID,
                'text': message
            }
        requests.post(self.url, params=params)

telegram = Telegram()