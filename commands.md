
1.	Projekt Strukur und Pakete

//project structure
Touch routes.py
Touch database.py
//creating a website
Mkdir templates
layout.html  (base web-template)
session.html
admin.html
user.html
superuser.html
//statische ressourcen wie Bilder oder CSS (stylesheet language)
Mkdir static
Touch css


// create an isolated Python environment to avoid sharing dependencies with other venv’s
virtualenv venv
source venv/bin/activate
desactivate

//install packages for pyhton programming language
pip install flask (Webframework)
pip install flask-sqlalchemy (extension for DB)
pip install psycopg2 (PostgresSQL database adapter)
pip install psycopg2-binary
pip list  (Look up the dependencies installed by pip (python packages/libaries)



2.	Code

//routes.py
from flask import Flask, render_template



3.	Postgres Struktur

psql 
create database VR;
psql project1 (entering db)
select * from users; 
select * from projects; 


CREATE TABLE projects (	
Project_id  SERIAL PRIMARY KEY, 
projectname VARCHAR (50) NOT NULL,
filename VARCHAR (50) NOT NULL
);

CREATE TABLE rooms (
Room_id  SERIAL PRIMARY KEY, 
userid VARCHAR (100) NOT NULL,
floor VARCHAR (100) NOT NULL,
room VARCHAR (100) NOT NULL,
roomguid VARCHAR (100) NOT NULL,
status VARCHAR (100) NULL
);

CREATE TABLE tasks (
task_id  VARCHAR (100) NOT NULL,
task VARCHAR (100) NOT NULL,
userid VARCHAR (100) NOT NULL,
predecessor VARCHAR (100) NOT NULL,
successor VARCHAR (100) NOT NULL,
status VARCHAR (100) NULL
);

CREATE TABLE users (
User_id  SERIAL PRIMARY KEY, 
username VARCHAR (100) NOT NULL unique,
password VARCHAR (100) NOT NULL unique,
role VARCHAR (100) NOT NULL,
projectname VARCHAR (100) NOT NULL
);



INSERT INTO rooms (userid, floor, room) Values ('s.breden', '1.OG', '1.10');
UPDATE site1 SET room = '1.10' where id=3;

DROP DATABASE dbName; (nur wenn man sich nicht drinnen befindet)
DROP TABLE tbname;
DELETE FROM users; (delete rows)
ALTER SEQUENCE users_user_id_seq RESTART WITH 1; (reset id)

UPDATE checklist
SET status = null;

ALTER TABLE checklist
ADD checklist_id SERIAL PRIMARY KEY;

ALTER TABLE table_name
DROP COLUMN column_name;


\list (all DB’s)
\dt (list all tables)
\d Site1 (describes table)
select * from users; 

//Querying from DB – Code for python
import psycopg2 as p
conn = p.connect("dbname=project1 user=postgres host=localhost")
cur = conn.cursor() -to execute queries in sql)
cur.execute(SELECT room) –select table and display
rows = cur.fetchall()
rows


4.	saving to github

git status (to see the unadded files)
git add ...(to add to github)
git commit -m "detailing" (localy savings)
git push -u origin master (remote saving to git)
git remote add origin https://github.com/mathemaa/vr.git

