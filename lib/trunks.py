from subprocess import Popen, PIPE, DEVNULL, STDOUT
import os
import json

import mysql.connector
from mysql.connector import Error

import subprocess
import time

import requests
from requests.auth import HTTPBasicAuth


class Trunks():
    
    
    def __init__(
        self, bot_token, chat_id, ip_server, remote_server, 
        remote_user, remote_password, database, db_user, db_password
    ):
        self._bot_token = bot_token
        self._chat_id = chat_id
        self._remote_server = remote_server
        self._ip_server = ip_server
        self._remote_user = remote_user
        self._remote_password = remote_password
        
        self._database = database
        self._db_user = db_user
        self._db_password = db_password
    
    
    def message_telegram(self, text) -> bool:
        # Отправляет сообщения в телеграм
        try:
            method = "https://api.telegram.org/bot" + \
                self._bot_token + "/sendMessage"
            r = requests.post(method, data={"chat_id": self._chat_id, "text": text})
        except Exception as e:
            return False
        return True
    
    def list_trunks(self) -> list:
    
        list_arguments = ["/usr/sbin/asterisk", "-rx sip show registry"]

        NoRegisteredTrunks = []
        ban_ip = False
        countST = 0

        with Popen(list_arguments, stdout=PIPE, stdin=DEVNULL, stderr=STDOUT, encoding='cp866') as process:
            for line in iter(process.stdout.readline, b''):
                
                lineS = line.split()
                if line == '':
                    break
                
                if lineS[0] == "18":
                    break

                if lineS[4] != "Registered" and lineS[4] != "Request" and lineS[0] != "Host":
                    NoRegisteredTrunks.append(lineS[2])
                
                if lineS[4] == "Request":
                    countST = countST + 1
            
            if countST > 6:
                ban_ip = True 
        
        return NoRegisteredTrunks, ban_ip
    
    
    def get_id_trunks(self, NoRegisteredTrunks) -> list:
    
        list_arguments = ["fwconsole", "trunks"]

        id_trunks = []

        with Popen(list_arguments, stdout=PIPE, stdin=DEVNULL, stderr=STDOUT, encoding='cp866') as process:
            for line in iter(process.stdout.readline, b''):
                
                lineS = line.strip().split()
                if line == '':
                    break
                
                if lineS[0] != "+----+------------+-----------+----------+----------------------+----------------------+-----+-----+":        
                    if lineS[1] != "ID":
                        trunk = lineS[9].split("_")
                        if trunk[1] in NoRegisteredTrunks:
                            id_trunks.append({
                                "id": trunk[0],
                                "trunk": trunk[1]
                            })
            
        return id_trunks
    
    
    def disabled_trunks(self, id_trunks) -> list:
        
        connection = mysql.connector.connect(host='localhost',
                                         database=self._database,
                                         user=self._db_user,
                                         password=self._db_password)
        
        try:
            for id in id_trunks:
                # list_arguments = ["fwconsole", f"trunks --disable {id['id']}"]
                # res = subprocess.call(list_arguments, stdout=PIPE, stdin=DEVNULL, stderr=STDOUT, encoding='cp866')
                
                cursor = connection.cursor()
                
                sql = f"DELETE FROM asmrl_megafon_pool WHERE phone = {id['trunk']}"

                cursor.execute(sql)
                connection.commit()
                
                self.message_telegram(
                    f"Удален транк: {id['trunk']}"
                ) 
            
            # reload_asterisk = subprocess.call(["fwconsole", "-r"], stdout=PIPE, stdin=DEVNULL, stderr=STDOUT, encoding='cp866')
            # if not reload_asterisk:
            #     return False
            
            self.message_telegram(
                    f"Asterisk сервер {self._ip_server} успешно перезагружен"
                ) 
            
        except Exception as err:
            return False
        
        return True
    
    
    def send_data_for_update(self, NoRegisteredTrunks, status_work):
        try:
            
            url = "http://" + self._remote_server + "/data_for_update"

            r = requests.post(url, json={
                "status_work": status_work, "NoRegisteredTrunks": NoRegisteredTrunks},
                auth=HTTPBasicAuth(self._remote_user, self._remote_password)
            )
            
            if int(r.status_code) != 200:
                return False
            
        except Exception as err:
            return False 
        
        return True