Create MySQL database:
======================

mysql>create database apicom_db;
Query OK, 1 row affected (0.03 sec)

edit config.json:
=================
"user" : "myuser" >>> replace for your database user:
"user" : "yourdatabaseuser"
--------------------------
"password":"userpwd" >>> replace for your database userpassword:
"password":"youdatabaseuserpassword"

install flask:
==============
pip2.7 install flask

install flask_mysqldb
=====================
pip2.7 install flask_mysqldb

install flaskext.mysql
======================
pip2.7 install flaskext.mysql

install jinja2 
==============
pip2.7 install jinja2


Start script_name.py with date_ranges in argument:
=================================================
python script_name.py --date_ranges=22-08-2020_29-08-2020


Open your browser url: http://localhost:8000 
============================================
