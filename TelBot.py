import os

import requests
from dotenv import load_dotenv
from loguru import logger


class TelBot:
    production = True

    def __init__(self, monitor_logger: logger):
        load_dotenv()
        if TelBot.production:
            self.token = os.getenv("TELEGRAM_BOT_TOKEN")
            self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        else:
            self.token = os.getenv("TESTING_TELEGRAM_BOT_TOKEN")
            self.chat_id = os.getenv("TESTING_TELEGRAM_CHAT_ID")

        self.get_update_url = "https://api.telegram.org/bot{}/getUpdates"
        self.send_message_url = "https://api.telegram.org/bot{}/sendMessage"
        self.logger: logger = monitor_logger

    def get_chat_id(self):
        response = requests.get(self.get_update_url.format(self.token))
        print(response.json())

    def send_message(self, message, product_page=None, page_description=None):
        payload = {
            'chat_id': self.chat_id,
            'text': message,
            "parse_mode": "html",
            "disable_web_page_preview": "1",
        }

        if product_page:
            payload['reply_markup'] = {
                'inline_keyboard': [
                    [
                        {
                            'text': page_description,
                            'url': product_page
                        }
                    ]
                ]
            }

        headers = {
            "Content-Type": "application/json"
        }

        try:
            result = requests.post(url=self.send_message_url.format(self.token), json=payload, headers=headers)
            if result.status_code != 200:
                self.logger.error("Fail to send tg message...")
            else:
                self.logger.success("Telegram notification send...")
        except Exception as e:
            self.logger.error("Error in sending tg message...", e)


if __name__ == "__main__":
    telegram = TelBot(logger)
    # telegram.get_chat_id()
    telegram.send_message("TG message testing...")
