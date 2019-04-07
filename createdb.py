import psycopg2

 
 
def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE IF NOT EXISTS projects (
            project_id  SERIAL PRIMARY KEY, 
            projectname VARCHAR (50) NOT NULL,
            filename VARCHAR (50) NOT NULL

        )
        """,
        """ CREATE TABLE IF NOT EXISTS users (
                user_id  SERIAL PRIMARY KEY, 
                username VARCHAR (100) NOT NULL unique,
                password VARCHAR (100) NOT NULL unique,
                role VARCHAR (100) NOT NULL,
                projectname VARCHAR (100) NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS rooms (
                room_id  SERIAL PRIMARY KEY, 
                userid VARCHAR (100) NOT NULL,
                floor VARCHAR (100) NOT NULL,
                room VARCHAR (100) NOT NULL,
                roomguid VARCHAR (100) NOT NULL,
                status VARCHAR (100) NULL

        )
        """,
        """
        CREATE TABLE IF NOT EXISTS tasks (
        		taskid  SERIAL PRIMARY KEY, 
                task_id VARCHAR (100) NOT NULL,
                task VARCHAR (100) NOT NULL,
                userid VARCHAR (100) NOT NULL,
                predecessor VARCHAR (100) NULL,
                successor VARCHAR (100) NULL,
                status VARCHAR (100) NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS checklist AS (
                SELECT rooms.userid, rooms.room, tasks.task_id, tasks.task, tasks.successor, tasks.status
                FROM rooms 
                INNER JOIN tasks 
                ON (rooms.userid = tasks.userid)
        )
        """
        )
        
    conn = None
    try:
        
        # connect to the PostgreSQL server
        conn = psycopg2.connect(
              database="vr",
              user="postgres",
              host="localhost",
              port="5432"
              )
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
 
 
if __name__ == '__main__':
    create_tables()
