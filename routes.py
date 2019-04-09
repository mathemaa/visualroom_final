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

#Verifizierung des Nutzers beim Login in der App
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

   
#Alle Tabellendaten fuer den Administartor laden
@app.route('/admin')
def admin_session():
  all_projects = projects.query.all()
  all_users = users.query.all()
  all_tasks = tasks.query.all()
  return render_template('admin.html',  datas=all_projects, users_data=all_users, tasks_data=all_tasks)

#Alle Daten fuer allgemeinen Nutzer laden, Projektuebersicht
@app.route('/superuser')
def superuser_session():
  all_rooms = rooms.query.all()
  return render_template('superuser.html', datas=all_rooms )

#Daten laden zum ausfuellen der Tabelle de Nutzer
@app.route('/useredit')
def user_session():
  if 'userid' not in session:
    return redirect('/')

  userid = str(session['userid'])

  datas = rooms.query.filter(rooms.userid == userid).all()
  datas1 = checklist.query.filter(checklist.userid == userid).all()

  return render_template('useredit.html', datas=datas, datas1=datas1)
  

#Status in der Datenbank speichern
@app.route("/update/<int:room_id>", methods=['POST'])
def update(room_id):
  current_id = room_id
  status = request.form['status']

  conn = psycopg2.connect(
                database="vr",
                user="postgres",
                host="localhost",
                port="5432"
                )
  cur = conn.cursor()
  cur.execute(
  			"UPDATE rooms SET status = %s WHERE room_id = %s ",
      		(status, current_id) )
  conn.commit()

  return redirect('/useredit')


#Checkliste aktualisieren
@app.route("/checked/<int:checklist_id>", methods=['POST'])
def checked(checklist_id):
  status = request.form['status']
  cur_id = str(checklist_id)

  conn = psycopg2.connect(
                database="vr",
                user="postgres",
                host="localhost",
                port="5432"
                )
  cur = conn.cursor()

  cur.execute(
      		"UPDATE checklist SET status = %s WHERE checklist_id = %s",
      		(status, cur_id))

  cur.execute(" SELECT checklist.room, checklist.successor FROM checklist WHERE checklist_id = %s ",
      		 (cur_id,))

  datas = (cur.fetchall())
  for row in datas:
  	room = row [0]
  	suc = row [1]

  cur.execute(
  			"UPDATE checklist SET status = '0' WHERE room = %s AND task_id = %s",
     		(room, suc))
  
  conn.commit()
  return redirect('/useredit')
  #return (suc)

#Status der Raeume fuer visualisierung abrufen
@app.route("/grafik")
def grafik():
  if 'userid' not in session:
    return redirect('/useredit')
  
  #user stored in the session 
  userid = str(session['userid'])

  datas = rooms.query.filter(rooms.userid == userid).all()
  return render_template('grafik.html', datas=datas)


#CSV Raumliste importieren
@app.route('/upload_rooms', methods=['POST'])
def upload_file():
    if request.method == 'POST':
    	f = request.files['the_file']
    	f.save(secure_filename(f.filename))
    	newProject=projects(projectname=request.form['name'], filename=f.filename)
    	db.session.add(newProject)
    	db.session.commit()
        return 'file uploaded successfully'

#Terminplan importieren
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

    #Alle Vorgaenge ohne Vorgaenger (=0) werden mit 0 als Status belegt
    cur.execute(
  			"UPDATE tasks SET status = '0' WHERE predecessor = '0' "
    )
    conn.commit()
    return 'file uploaded successfully'


#neuen Nutzer mit Raeumen hinzufuegen
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