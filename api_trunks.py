import mysql.connector
from mysql.connector import Error

from flask import (Flask, jsonify, render_template, redirect, 
                  request, make_response, url_for, flash, abort)

from requests.auth import HTTPBasicAuth
from flask_basicauth import BasicAuth

import uuid
import logging

from lib.api import Api
from lib.config import (
  BOT_TOKEN, CHAT_ID, IP_SERVER, BASIC_AUTH_USERNAME, BASIC_AUTH_PASSWORD,
  DATABASE, DB_USER, DB_PASSWORD
)

api = Api(BOT_TOKEN, CHAT_ID, IP_SERVER)

app = Flask("TruncksModule", static_url_path = "")

app.config['SECRET_KEY']= 'a2db28d7-13eb-4b67-bcc3-8hbc2ze3a83d'

app.config['BASIC_AUTH_USERNAME'] = BASIC_AUTH_USERNAME
app.config['BASIC_AUTH_PASSWORD'] = BASIC_AUTH_PASSWORD

basic_auth = BasicAuth(app)

logging.basicConfig(
    format='[TruncksModule] %(levelname)s: %(message)s',
    level=logging.INFO
)

@app.route('/trunks_gateway', methods=["GET"])
def index():
  return jsonify({"code": "403"})

@app.route('/get_phones', methods=["GET"])
@basic_auth.required
def getTrunks():
  try:
    
    connection = mysql.connector.connect(host='localhost',
                                         database=DATABASE,
                                         user=DB_USER,
                                         password=DB_PASSWORD)


    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
        cursor = connection.cursor()
        
        phones = []
        
        cursor.execute("SELECT * from asmrl_megafon_pool")
        result=cursor.fetchall()
        
        for r in result:
          phones.append({"id_trunk": r[0], "phone": r[2], "password": r[3]})
          
  except Error as e:
      print("Error while connecting to MySQL", e)
  finally:
      if connection.is_connected():
          cursor.close()
          connection.close()
          print("MySQL connection is closed")
        
        
  return jsonify({'response': phones})

        

if __name__ == '__main__':
    app.run(debug=True, port=3000)