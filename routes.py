# Module werden importiert 
from flask import Flask, request, redirect, render_template, session
from database import db, users, projects, rooms, tasks
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

    if role is '1':
      return redirect('/admin')

    if role is '2': 
      return redirect('/useredit')
    
    if role is '3':
      return redirect('/superuser')

   

@app.route('/admin')
def admin_session():
  all_projects = projects.query.all()
  all_users = users.query.all()
  return render_template('admin.html',  datas=all_projects, users_data=all_users)

@app.route('/superuser')
def superuser_session():
  all_rooms = rooms.query.all()
  return render_template('superuser.html', datas=all_rooms )


@app.route('/useredit')
def user_session():
  if 'userid' not in session:
    return redirect('/')
  
  #user stored in the session or abort
  userid = str(session['userid'])

  datas = rooms.query.filter(rooms.userid == userid).all()
  datas1 = tasks.query.filter(tasks.userid == userid).all()
  return render_template('useredit.html', datas=datas, datas1=datas1 )
  

@app.route("/update/<int:room_id>", methods=['POST'])
def update(room_id):
  room = rooms.query.filter_by(room_id = rooms.room_id).first()       
  room.status =request.form['status']
  db.session.commit()
  return redirect('/useredit')

@app.route("/grafik")
def grafik():
  if 'userid' not in session:
    return redirect('/useredit')
  
  #user stored in the session or abort
  userid = str(session['userid'])

  datas = rooms.query.filter(rooms.userid == userid).all()
  return render_template('grafik.html', datas=datas)


#CSV Daten importieren
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
    	f = request.files['the_file']
    	f.save(secure_filename(f.filename))
    	newProject=projects(projectname=request.form['name'], filename=f.filename)
    	db.session.add(newProject)
    	db.session.commit()
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
                #extracting the floors & rooms from the csv and instert to table
                with open('Duplex_A_20110907_rooms_modified.csv', 'r') as f:
                    reader = csv.reader(f, delimiter=';')
                    for row in reader:
                      #print(row[1],row[2])
                      cur.execute(
                            " INSERT INTO rooms (userid, floor, room, roomguid) VALUES (%s, %s, %s, %s)",
                            (userid ,row[1],row[2],row[4])
                      )
                conn.commit()

                return redirect('/admin')
            else:
                return redirect('/admin')




#debug mode for occuring problems and mistake informations when debugging the code 
if __name__ == "__main__":
  app.run(debug=True)