#!/usr/bin/python
# -*- coding: UTF-8 -*-

from __future__ import print_function
import requests
import sys 
import xml.etree.ElementTree as ET
from datetime import datetime
import MySQLdb
import gc  
import random  
from flask import Flask, flash, redirect, render_template, request 
from flaskext.mysql import MySQL 
#from werkzeug.exceptions import BadRequestKeyError 
import json

# open the config.json file 
with open('config.json') as f:
    mydata = json.load(f);

# get database user and password
user = mydata.get('info').get('user') 
password = mydata.get('info').get('password') 
 
if len(sys.argv) == 2 and len(sys.argv[1]) == 35:
    date_ranges = sys.argv[1] 
    date_from = date_ranges[20:24] + date_ranges[16:20] + date_ranges[14:16]
    date_to = date_ranges[+31:] + date_ranges[27:31] + date_ranges[25:27]

    try:
        date_from_obj = datetime.date(datetime.strptime(date_from,'%Y-%m-%d'))
        date_to_obj = datetime.date(datetime.strptime(date_to, "%Y-%m-%d"))
    except ValueError:
        print("\ndate_ranges argv is incorrect\n=============================") 
        print("USAGE: script_name.py --date_ranges=dd-mm-yyyy_dd-mm-yyyy")
        exit(1)  

else: 
    print("\ndate_ranges argv are missing or incorrect\n=========================================") 
    print("USAGE: script_name.py --date_ranges=dd-mm-yyyy_dd-mm-yyyy")
    exit(1)

# url variables
key = '4e923a83-8b31-4c28-ac3d-f6cb994a60af'
type_name = "dsp"
format = "xml"

url = "http://publishers.imonomy.com/api/reports?key=%s&type_name=%s&format=%s&date_from=%s&date_to=%s" % (key, type_name, format, date_from, date_to) 

response = requests.get(url) 

api_data_to = [()] 

if response.status_code == 200:
    client_list = [
        "David Bruno",
        "Martin Brigs",
        "Karl First",
        "Micle Winter",
        "Mike White",
        "Rebeka Harms",
        "Justin Big",
        "Tom Brady",
        "Peter Bug",
        "Jana Green",
        "Jamila Won",
        "Ronaldo Man"
    ]

    tree = ET.fromstring(response.content)
    #for doc in tree.findall(".//report"):
    for elem in tree.findall("row"):
        if elem.find('date').text: 
            date_str = elem.find('date').text
        else: date_str = ""

        date = datetime.date(datetime.strptime(date_str, "%Y-%m-%d"))
 
        if elem.find('provider_name').text:
            provider_name = elem.find('provider_name').text
        else: provider_name = ""
  
        if elem.find('revenue').text:
            revenue = float(elem.find('revenue').text)
        else: revenue = ""

        if elem.find('wons').text:
            wons = float(elem.find('wons').text)
        else: wons = 0.0
         
        client_name = random.choice(client_list)
        date_updated = datetime.date(datetime.now()) 
        date_created = datetime.date(datetime.now()) 

        api_data_to += [(date, client_name, provider_name, revenue, wons, date_updated, date_created)] 
         
else:
    print("Request.Get Error")
    exit(1) 

api_data_to.remove(api_data_to[0])  

# Connection to MySQL server by means MySQLdb.connect 
db = MySQLdb.connect(
                    host="localhost",
                    user=user,
                    passwd=password, 
                    db="apicom_db"
                    )
 
# create object db by means method cursor() of module MySQLdb
cursor = db.cursor() 

#data = cursor.fetchone()
#print ("MySQL ver.: %s " % data)
 
# delete the table if it already exists 
cursor.execute("DROP table IF EXISTS api_data")
 
# create table
cursor.execute("""CREATE TABLE api_data(date DATE, client_name VARCHAR(80), provider_name VARCHAR(80), revenue FLOAT, wons INT, date_updated DATE, date_created DATE)""")  

# insert into table with error handling 
try:   
    for item in api_data_to: 
        cursor.execute("""INSERT INTO api_data (date, client_name, provider_name, revenue, wons, date_updated, date_created) VALUES (%s, %s, %s, %s, %s, %s, %s)""", (item)) 
 
    db.commit() # save data in table 
 
except MySQLdb.Error as e: 
    print("MySQL Error [%d]: %s" % (e.args[0], e.args[1])) 

else: 
    # disconnect from the server   
    db.close() 
    gc.collect()

app = Flask(__name__)

mysql = MySQL()
 
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = user
app.config['MYSQL_DATABASE_PASSWORD'] = password
app.config['MYSQL_DATABASE_DB'] = 'apicom_db'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()  

@app.route('/') 

def sort_data(): 
 
    sql = "SELECT * FROM api_data ORDER BY date"
    cursor.execute(sql)
    results = cursor.fetchall()
 
    results = data_list()
 
    if len(results) > 0:
        num_rec = len(results) 
        date_in = results[0][0] 
        date_out = results[num_rec-1][0]
        cl_name_list = ""

    return render_template("index.html", 
        results_all = results,
        results = results,
        date_in = date_in,
        date_out = date_out, 
        title = 'Office UI' 
        )

@app.route('/date_select', methods=['GET', 'POST'])

def date_select():
    if request.method == 'POST':
        req_data = request.form
        date_list = req_data.getlist('calendar')
        date_in_s = date_list[0]
        date_out_s = date_list[1]
        date_in_s = datetime.date(datetime.strptime(date_in_s, "%Y-%m-%d"))
        date_out_s = datetime.date(datetime.strptime(date_out_s, "%Y-%m-%d"))

    sql = "SELECT * FROM api_data WHERE api_data.date>=%s AND api_data.date<=%s ORDER BY date"
    cursor.execute(sql, (date_in_s, date_out_s))
    results = cursor.fetchall()
    
    results_all = data_list()
    date_in = date_range()[0]
    date_out = date_range()[1]

    return render_template("index.html", 
        results_all = results_all,
        results = results,
        date_in = date_in,
        date_out = date_out, 
        title = 'Office UI'        
        ) 

@app.route('/client_select', methods=['GET', 'POST'])

def client_select():
    if request.method == 'POST': 
        client_name = request.form.get('client_name')[1:-1] 
 
    sql = "SELECT * FROM api_data WHERE client_name=%s ORDER BY date"
    cursor.execute(sql, (client_name))

    results = cursor.fetchall()   

    results_all = data_list()
    date_in = date_range()[0]
    date_out = date_range()[1]

    return render_template("index.html",
        results_all = results_all, 
        results = results,
        title = 'Office UI', 
        date_in = date_in,
        date_out = date_out 
        )

def data_list():
    sql = "SELECT * FROM api_data ORDER BY date"
    cursor.execute(sql)
    results = cursor.fetchall() 

    return results
 
def date_range():
    results_all = data_list()

    if len(results_all) > 0:
        num_rec = len(results_all)
        date_in = results_all[0][0] 
        date_out = results_all[num_rec-1][0] 
    else:
        date_in = ""
        date_out = ""

    return (date_in, date_out)

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host= 'localhost', port=8000, debug=True)
    conn.close() 
    gc.collect()




 