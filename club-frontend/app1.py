from flask import Flask, render_template, redirect, url_for, request
import mysql.connector
from datetime import datetime
import base64
app = Flask(__name__)

# MySQL Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Nid_1801',
    'database': 'sample'
}

print("Database Connection Successfull!!")
# Function to connect to the database
def get_database_connection():
    return mysql.connector.connect(**db_config)

# Index page
@app.route('/')
def index():
    return render_template('index.html')

# Clubs page
@app.route('/clubs.html')
def clubs():
    connection = get_database_connection()
    cursor = connection.cursor()

    # Assuming you have a table named 'clubs' with a column 'name'
    cursor.execute('SELECT C.C_NAME,C.C_DESC,C.C_LOGO,C.C_SDATE,C.C_LINK,C.C_EMAIL,GROUP_CONCAT(CC.C_CATEGORY) AS CLUB_CATEGORIES FROM CLUB AS C JOIN CLUB_CATEGORY AS CC ON C.C_ID=CC.C_ID GROUP BY C.C_ID,C.C_NAME')
    data = cursor.fetchall()
    cursor.execute("select c.c_name,cs.c_sm_link from club as c left join club_sm as cs on c.c_id=cs.c_id and c_sm_name='instagram '")
    link=cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('clubs.html', clubs=data,link=link)


@app.route('/events.html')
def events():
    connection = get_database_connection()
    cursor = connection.cursor()

    # Assuming you have a table named 'events' with columns 'event_name', 'event_date', 'event_description'
    cursor.execute('SELECT E_NAME, E_DATE, E_DESC,E_STIME,E_ETIME,E_LOC,GROUP_CONCAT(CONCAT(G_FNAME," ",G_LNAME)),GROUP_CONCAT(G_INFO) FROM EVENT AS E JOIN GUEST AS G ON E.E_ID=G.E_ID WHERE E_DATE>CURDATE() GROUP BY E_NAME,E.E_ID ORDER BY E_DATE ASC')
    events_data = cursor.fetchall()
    cursor.execute('SELECT E_NAME, E_DATE, E_DESC,E_STIME,E_ETIME,E_LOC,GROUP_CONCAT(CONCAT(G_FNAME," ",G_LNAME)),GROUP_CONCAT(G_INFO) FROM EVENT AS E JOIN GUEST AS G ON E.E_ID=G.E_ID WHERE E_DATE<CURDATE() GROUP BY E_NAME,E.E_ID ORDER BY E_DATE ASC')
    past_events_data = cursor.fetchall()
    cursor.close()
    connection.close()
    
    return render_template('events.html', upcoming_events=events_data,past_events=past_events_data)


@app.route('/login.html')
def login():
    return render_template('login.html')

faculty_name=" "
clubs_data=[]

@app.route('/faculty-login.html', methods=['GET', 'POST'])
def faculty_login():
    if request.method == 'POST':
        global faculty_name,clubs_data,faculty_id
        faculty_id = request.form['facultyId']
        password = request.form['password']
        connection = get_database_connection()
        cursor = connection.cursor()
        query = 'SELECT * FROM faculty_coordinator WHERE f_id = %s AND f_password = %s'
        cursor.execute(query, (faculty_id, password))
        faculty_data = cursor.fetchone()
        faculty_name = faculty_data[1] + " " + faculty_data[2]
        query = 'SELECT GROUP_CONCAT(C.C_NAME) FROM CLUB AS C JOIN FACULTY_COORDINATOR AS FC ON C.F_ID = FC.F_ID WHERE FC.F_ID = %s'
        cursor.execute(query, (faculty_id,))
        clubs_data = cursor.fetchall()
        query3=" SELECT GetNumberOfClubs(%s) AS NumberOfClubs"
        cursor.execute(query3,(faculty_id,))
        no_of_clubs=cursor.fetchone()
        cursor.close()
        connection.close()

        return render_template("success_f.html", faculty_name=faculty_name, clubs=clubs_data,no_of_clubs=no_of_clubs)
    else:
        
        return render_template('faculty-login.html')
    
# Add a new route for viewing members
@app.route('/view_members.html/<club_name>')
def view_members(club_name):
    connection = get_database_connection()
    cursor = connection.cursor()

    # Assuming you have a table named 'members' with columns 'name', 'email', 'club_name'
    cursor.execute('SELECT concat(s_fname," ",s_lname), s_email,s_sem,d_name,s_role FROM member_students as S join club as C on S.C_ID =C.C_ID WHERE c_name = %s ORDER BY S_FNAME', (club_name,))
    members_data = cursor.fetchall()

    cursor.close()
    connection.close()
    
    return render_template('view_members.html', club_name=club_name, members=members_data)


@app.route('/add_events.html', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        event_name = request.form['event_name']
        event_description = request.form['event_description']
        event_date = request.form['event_date']
        event_startime = request.form['event_stime']
        event_endtime = request.form['event_etime']
        event_loc = request.form['event_loc']
        event_budget = request.form['event_budget']
        guest_fname=request.form['firstName']
        guest_lname=request.form['lastName']
        guest_email=request.form['email']
        guest_ph=request.form['phoneNumber']
        guest_info=request.form['guestInfo']
        guest_addr=request.form['guestAddr']

        connection = get_database_connection()
        cursor = connection.cursor()

        # Assuming you have a table named 'events' with columns 'event_name', 'event_date', 'event_description', 'club_name'
        cursor.execute('INSERT INTO EVENT(E_NAME, E_DESC, E_DATE, E_STIME, E_ETIME, E_LOC, E_BUDGET) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                       (event_name, event_description, event_date, event_startime, event_endtime, event_loc, event_budget))

        connection.commit()
        cursor.execute('SELECT E_ID FROM EVENT WHERE E_NAME=%s',(event_name,))
        event_id=cursor.fetchone()[0]
        cursor.execute('INSERT INTO GUEST(E_ID,G_FNAME,G_LNAME,G_ADD,G_INFO,G_EMAIL,G_PHNO) VALUES (%s,%s,%s,%s,%s,%s,%s)',
                       (event_id,guest_fname,guest_lname,guest_addr,guest_info,guest_email,guest_ph))
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('faculty_login'))

    return render_template('add_events.html')

  
@app.route('/success_f.html')
def success_f():
    return render_template("success_f.html", faculty_name=faculty_name, clubs=clubs_data,)

@app.route('/student-login.html', methods=['GET', 'POST'])
def student_login():
    global student_name, student_data
    print("in student_login")
    if request.method == 'POST':
        student_id = request.form['studentId']
        password = request.form['password']
        print("received data")
        connection = get_database_connection()
        cursor = connection.cursor()
        query = 'SELECT * FROM member_students WHERE s_srn = %s AND s_password = %s'
        cursor.execute(query, (student_id, password))
        
        # Debug: Print the executed query and fetched data
        print("Executed Query:", cursor.statement)
        student_data = cursor.fetchone()
        print("Fetched Data:", student_data)

        if student_data:
            student_name = student_data[3] + " " + student_data[4]
            query = 'SELECT CLUB.C_NAME, MEMBER_STUDENTS.S_ROLE,MEMBER_STUDENTS.S_SDATE,MEMBER_STUDENTS.D_NAME FROM MEMBER_STUDENTS JOIN CLUB ON CLUB.C_ID=MEMBER_STUDENTS.C_ID WHERE S_SRN = %s'
            cursor.execute(query, (student_id,))
            clubs_data = cursor.fetchall()
            
            query2 = 'CALL CountClubsForStudent(%s, @count)'
            cursor.execute(query2, (student_id,))
            cursor.execute('SELECT @count')
            club_count = cursor.fetchone()[0]
            
           # Debug: Print the data to be passed to the template
            print("Student Name:", student_name)
            print("Clubs Data:", clubs_data)
            print("Club Count:", club_count)
            
            query3=' select D_NAME,C.C_NAME,S_SDATE,S_EDATE,S_ROLE FROM BACKUP_TABLE JOIN CLUB AS C ON C.C_ID=BACKUP_TABLE.C_ID WHERE S_SRN=%s'
            cursor.execute(query3,(student_id,))
            history=cursor.fetchall()
            cursor.close()
            connection.close()
            return render_template("success_s.html", student_name=student_name, clubs=clubs_data, no_of_clubs=club_count,past_record=history)
        else:
            cursor.close()
            connection.close()
    return render_template('student-login.html')
    
@app.route("/success_s.html")
def success_s():
    return render_template("success_s.html")
@app.route('/index.html')
def index1():
    return render_template('index.html')

@app.route("/head-page.html/<club_name>")
def head_page(club_name):
    return render_template("head-page.html",club_name=club_name)
@app.route("/add.html/<club_name>",methods=['GET', 'POST'])
def add(club_name):
    if request.method == 'POST':
        srn=request.form['studentId']
        d_name=request.form['domainName']
        fname=request.form['firstName']
        lname=request.form['lastName']
        phno=request.form['phoneNumber']
        email=request.form['email']
        dept=request.form['dept']
        sem=request.form['semester']
        role=request.form['role']
        password=request.form['password']
        connection = get_database_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT C_ID FROM CLUB WHERE C_NAME = %s', (club_name,))
        club_id = cursor.fetchone()[0]
        s_date=datetime.now().date()
        query='INSERT INTO MEMBER_STUDENTS VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        cursor.execute(query,(srn,d_name,club_id,fname,lname,email,s_date,dept,phno,sem,role,password,))
        connection.commit()
        cursor.close()
        connection.close()   
        return render_template("/head-page.html",club_name=club_name)

    return render_template("add.html",club_name=club_name)
@app.route("/delete.html/<club_name>",methods=['GET','POST'])
def delete(club_name):
    if request.method=='POST':
        srn=request.form['studentId']
        domain_name=request.form['domainName']
        connection = get_database_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT C_ID FROM CLUB WHERE C_NAME = %s', (club_name,))
        club_id = cursor.fetchone()[0]
        query='DELETE FROM MEMBER_STUDENTS WHERE S_SRN=%s AND D_NAME=%s AND C_ID=%s'
        cursor.execute(query,(srn,domain_name,club_id,))
        connection.commit()
        cursor.close()
        connection.close()
        return render_template("/head-page.html",club_name=club_name)
    return render_template("delete.html",club_name=club_name)

@app.route("/update.html/<club_name>",methods=['GET','POST'])
def update(club_name):
    if request.method=='POST':
        srn=request.form['studentId']
        domain_name=request.form['domainName']
        old_role=request.form['oldRole']
        new_role=request.form['newRole']
        connection = get_database_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT C_ID FROM CLUB WHERE C_NAME = %s', (club_name,))
        club_id = cursor.fetchone()[0]
        query='UPDATE MEMBER_STUDENTS  SET S_ROLE=%s WHERE S_SRN=%s AND D_NAME=%s AND C_ID=%s'
        cursor.execute(query,(new_role,srn,domain_name,club_id,))
        connection.commit()
        cursor.close()
        connection.close()
        return render_template("/head-page.html",club_name=club_name)
    return render_template("update.html",club_name=club_name)


if __name__ == '__main__':
    app.run(debug=True)
