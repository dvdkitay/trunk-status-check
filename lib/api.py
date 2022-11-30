import requests

class Api():
    
    def __init__(self, bot_token, chat_id, IP_SERVER):
        self._bot_token = bot_token
        self._chat_id = chat_id
        
        # self.message_telegram(
        #     f"Сервер {IP_SERVER}\nМодуль мониторинга транков запущен"
        # )
    
    
    def message_telegram(self, text) -> bool:
        # Отправляет сообщения в телеграм
        try:
            method = "https://api.telegram.org/bot" + \
                self._bot_token + "/sendMessage"
            r = requests.post(method, data={"chat_id": self._chat_id, "text": text})
        except Exception as e:
            print(e)
            return False
        return True
        