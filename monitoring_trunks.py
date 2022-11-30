from subprocess import Popen, PIPE, DEVNULL, STDOUT
import os
import json

import subprocess
import time

from lib.trunks import Trunks
from lib.config import (
    BOT_TOKEN, CHAT_ID, IP_SERVER, REMOTE_SERVER, 
    REMOTE_USER, REMOTE_PASSWORD, DATABASE, DB_USER, DB_PASSWORD
)

trunks = Trunks(
    BOT_TOKEN, CHAT_ID, IP_SERVER, REMOTE_SERVER, 
    REMOTE_USER, REMOTE_PASSWORD, DATABASE, DB_USER, DB_PASSWORD
)

while True:
    
    try:
        NoRegisteredTrunks, ban_ip = trunks.list_trunks()

        if not ban_ip:
            
            if len(NoRegisteredTrunks) > 0:
                trunks.message_telegram(
                    f"Сервер {IP_SERVER}\nНайдены заблокированые транки: {NoRegisteredTrunks}"
                )
                trunks.message_telegram(
                    f"Сервер {IP_SERVER}\nДелаем паузу в 120 секунд для повторной проверки"
                )
                
                time.sleep(120)
                
                NoRegisteredTrunks, ban_ip = trunks.list_trunks()
                
                if not ban_ip:
                
                    if len(NoRegisteredTrunks) > 0:
                        
                        trunks.message_telegram(
                            f"Сервер {IP_SERVER}\nБлокировка транков: {NoRegisteredTrunks} подтвердилась"
                        )   
                    
                        id_trunks = trunks.get_id_trunks(NoRegisteredTrunks)
                        
                        if not trunks.disabled_trunks(id_trunks):
                            trunks.message_telegram(
                                f"Сервер {IP_SERVER}\nПолучена ошибка при удалении транков"
                            )
                        
                        if REMOTE_SERVER:
                            if not trunks.send_data_for_update(NoRegisteredTrunks, status_work=True):
                                trunks.message_telegram(
                                    f"Cервер {IP_SERVER}\nОшибка отправки данных на сервер {REMOTE_SERVER}"
                                )
                            
                    else:
                        trunks.message_telegram(
                        f"Сервер {IP_SERVER}\nТранки востановили свою работу"
                    )
                        
                else:
                    
                    time.sleep(12)
                    
                    if REMOTE_SERVER:
                        if not trunks.send_data_for_update(NoRegisteredTrunks, status_work=False):
                            trunks.message_telegram(
                                f"Cервер {IP_SERVER}\nОшибка отправки данных на сервер {REMOTE_SERVER}"
                            )
            
                    trunks.message_telegram(
                        f"Сервер {IP_SERVER}\nCервер заблокирован у мегафона"
                    )
                    
            
            else:
                # Все хорошо. Ничего не выводим в консоль
                pass
        
        else:
            
            time.sleep(12)
            
            NoRegisteredTrunks, ban_ip = trunks.list_trunks()
            
            if ban_ip:
                
                if REMOTE_SERVER:
                    if not trunks.send_data_for_update(NoRegisteredTrunks, status_work=False):
                        trunks.message_telegram(
                            f"Cервер {IP_SERVER}\nОшибка отправки данных на сервер {REMOTE_SERVER}"
                        )
            
                trunks.message_telegram(
                    f"Сервер {IP_SERVER}\nCервер заблокирован у мегафона"
                )
                    
    except Exception as err:
        trunks.message_telegram(
            f"⛔ Сервер {IP_SERVER} Ошибка работы мониторинга"
        )
    
    time.sleep(1)

