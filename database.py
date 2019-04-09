from flask_sqlalchemy import SQLAlchemy
import psycopg2, csv 

db = SQLAlchemy()


class projects(db.Model):
  __tablename__ = 'projects'
  project_id = db.Column(db.Integer, primary_key = True)
  projectname = db.Column(db.String(100))
  filename = db.Column(db.String(100))


class users(db.Model):
  __tablename__ = 'users'
  user_id = db.Column(db.Integer, primary_key = True)
  username = db.Column(db.String(100), unique=True)
  password = db.Column(db.String(100), unique=True)
  role = db.Column(db.String(100))
  projectname = db.Column(db.String(100))

	
  def __init__(self,  username, password, role, projectname):
     #Attribute der Klasse -> self.xxxx
    self.username = username
    self.password = password 
    self.role = role 
    self.projectname = projectname


class rooms(db.Model):
  __tablename__ = 'rooms'
  room_id = db.Column(db.Integer, primary_key = True)
  userid = db.Column(db.String(100))
  floor = db.Column(db.String(100))
  room = db.Column(db.String(100))
  roomguid = db.Column(db.String(100))
  status = db.Column(db.String(100))

  def __init__(self,  userid, floor, room, roomguid, status):
     #Attribute der Klasse -> self.xxxx
    self.userid = userid
    self.floor = floor 
    self.room = room 
    self.roomguid = roomguid
    self.status = status

class tasks(db.Model):
  __tablename__ = 'tasks'
  taskid = db.Column(db.Integer, primary_key = True)
  task_id = db.Column(db.String(100))
  task = db.Column(db.String(100))
  userid = db.Column(db.String(100))
  predecessor = db.Column(db.String(100))
  successor = db.Column(db.String(100))
  status = db.Column(db.String(100))

class checklist(db.Model):
  __tablename__ = 'checklist'
  userid = db.Column(db.String(100))
  room = db.Column(db.Integer)
  task_id = db.Column(db.Integer)
  task = db.Column(db.String(100))
  successor = db.Column(db.String(100))
  status = db.Column(db.String(100))
  checklist_id = db.Column(db.Integer, primary_key = True)

 

#conn.close()