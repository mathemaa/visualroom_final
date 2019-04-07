# Module werden importiert 
from flask import Flask, request, redirect, render_template, session
from database import db, users, projects, rooms, checklist, tasks
from werkzeug.utils import secure_filename
import psycopg2, csv
import os



app = Flask(__name__)
app.secret_key = os.urandom(12)


#connecting to postgres
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost/vr'
db.init_app(app)

#ROUTING
@app.route("/")
def session_start():
  return render_template("session.html")


@app.route("/login", methods=['POST'])
def login():

    conn = psycopg2.connect(
              database="vr",
              user="postgres",
              host="localhost",
              port="5432"
              )
    cur = conn.cursor()

    x = request.form['username']
    y = request.form['password']
    
    cur.execute( "SELECT user_id FROM users WHERE username = %s AND password = %s ",
      (x,y)
      )

    userid = str(cur.fetchone()[0])

    cur.execute("SELECT role FROM users WHERE user_id = %s ",
      (userid)
      )

    role = cur.fetchone()[0]

    session['userid'] = userid

    if role is '2': 
      return redirect('/useredit')
    
    if role is '3':
      return redirect('/superuser')

   

@app.route('/admin')
def admin_session():
  all_projects = projects.query.all()
  all_users = users.query.all()
  all_tasks = tasks.query.all()
  return render_template('admin.html',  datas=all_projects, users_data=all_users, tasks_data=all_tasks)

@app.route('/superuser')
def superuser_session():
  all_rooms = rooms.query.all()
  return render_template('superuser.html', datas=all_rooms )


@app.route('/useredit')
def user_session():
  if 'userid' not in session:
    return redirect('/')
  
  userid = str(session['userid'])

  datas = rooms.query.filter(rooms.userid == userid).all()
  datas1 = checklist.query.filter(checklist.userid == userid).all()
  
  #datas1 = tasks.query.filter(tasks.userid == userid).all()

  return render_template('useredit.html', datas=datas, datas1=datas1)
  

@app.route("/update/<int:room_id>", methods=['POST'])
def update(room_id):
  room = rooms.query.filter_by(room_id = rooms.room_id).first()       
  room.status =request.form['status']
  db.session.commit()
  return redirect('/useredit')


@app.route("/checked/<int:checklist_id>", methods=['POST'])
def checked(checklist_id):
  current = checklist.query.filter_by(checklist_id = checklist.checklist_id).first()    
  current.status = request.form['status']
  cur_room = current.room
  cur_suc = current.successor
  db.session.commit()

  conn = psycopg2.connect(
                database="vr",
                user="postgres",
                host="localhost",
                port="5432"
                )
  cur = conn.cursor()
  cur.execute(
  			"UPDATE checklist SET status = '0' WHERE room = %s AND task_id = %s",
      		(cur_room,cur_suc) )
  conn.commit()

  return redirect('/useredit')
   #x = str (checklist_id)
   #return(x)
  


@app.route("/grafik")
def grafik():
  if 'userid' not in session:
    return redirect('/useredit')
  
  #user stored in the session 
  userid = str(session['userid'])

  datas = rooms.query.filter(rooms.userid == userid).all()
  return render_template('grafik.html', datas=datas)


#Test funktion 
@app.route("/checklist1")
def checklist1():
  userid = str(session['userid'])

  conn = psycopg2.connect(
                database="vr",
                user="postgres",
                host="localhost",
                port="5432"
                )
  cur = conn.cursor()
  #cur.execute(" SELECT * FROM rooms INNER JOIN tasks ON (rooms.userid = tasks.userid) WHERE rooms.userid = '5' ")
  cur.execute(" SELECT rooms.room_id,tasks.task_id,tasks.predecessor,tasks.successor,tasks.status FROM rooms INNER JOIN tasks ON (rooms.userid = tasks.userid) WHERE rooms.userid = %s ",
      (userid)
      )
  datas = str(cur.fetchall())

  return (datas)
  

#CSV Daten importieren
@app.route('/upload_rooms', methods=['POST'])
def upload_file():
    if request.method == 'POST':
    	f = request.files['the_file']
    	f.save(secure_filename(f.filename))
    	newProject=projects(projectname=request.form['name'], filename=f.filename)
    	db.session.add(newProject)
    	db.session.commit()
        return 'file uploaded successfully'


@app.route('/upload_terminplan', methods=['POST'])
def upload_tp():
    f = request.files['the_file']
    f.save(secure_filename(f.filename))

    conn = psycopg2.connect(
                database="vr",
                user="postgres",
                host="localhost",
                port="5432"
                )
    cur = conn.cursor() 

    x = '1'  
    if x == '1' : 
		with open('tp.csv', 'rU') as file:
                    reader = csv.reader(file, delimiter=';')
                    for row in reader:
                      cur.execute(
                            " INSERT INTO tasks (task_id, task, userid, predecessor, successor) VALUES (%s, %s, %s, %s, %s)",
                            (row[0],row[1],row[2],row[3],row[4])
                      )
                      conn.commit()


    cur.execute(
  			"UPDATE tasks SET status = '0' WHERE predecessor = '0' "
    )
    conn.commit()

    return 'file uploaded successfully'



@app.route('/new_user', methods=['POST'])
def add_user():
        #verifying the role, than adding new user
            role = request.form['role']
            newuser=users(request.form['username'], request.form['password'], request.form['role'], request.form['projectname'])
            db.session.add(newuser)
            db.session.flush()
            db.session.commit()
            userid = str(newuser.user_id)

            #adding within this userid all the rooms to the rooms table
            
            conn = psycopg2.connect(
              database="vr",
              user="postgres",
              host="localhost",
              port="5432"
              )
            cur = conn.cursor()
            if role == '2' : 
                
                with open('Duplex_A_20110907_rooms_modified.csv', 'r') as file:
                    reader = csv.reader(file, delimiter=';')
                    for row in reader:
                      cur.execute(
                            " INSERT INTO rooms (userid, floor, room, roomguid) VALUES (%s, %s, %s, %s)",
                            (userid ,row[1],row[2],row[3])
                      )
                      conn.commit()

                return redirect('/admin')
            else:
                return redirect('/admin')



#debug mode for occuring problems and mistake informations when debugging the code 
if __name__ == "__main__":
  app.run(debug=True)