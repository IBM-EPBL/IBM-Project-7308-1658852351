import string
from flask import Flask, render_template,request,redirect,url_for,session,flash
from flask_mail import Mail,Message
from markupsafe import escape
import secrets
import random
import ibm_db
import hashlib
import os

#IBM-DB2 Connection Parameters
db_name="bludb"
db_host_name="ea286ace-86c7-4d5b-8580-3fbfa46b1c66.bs2io90l08kqb1od8lcg.databases.appdomain.cloud"
db_port=31505
db_security="SSL"
db_uname="kjj31886"
db_password="sNOtOHuegSjbIpgg"

dsn=f"DATABASE={db_name};HOSTNAME={db_host_name};PORT={db_port};SECURITY={db_security};SSLServerCertificate=DigiCertGlobalRootCA.crt;UID={db_uname};PWD={db_password}"

#Testing DB Connection
try:
    conn=ibm_db.connect(dsn,"","")
    print(f"Connection Established Successfully to {db_name}!")
except:
    print("Unable To Establish Connection:",ibm_db.conn_errormsg())

#Creating App Instance and Secret Key
app=Flask(__name__)
Flask.secret_key = os.urandom(64)
app = Flask(__name__)
app.config['SECRET_KEY'] = 'top-secret!'
app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'apikey'
app.config['MAIL_PASSWORD'] = '' #here api key is required
app.config['MAIL_DEFAULT_SENDER'] = 'ibm.pet2022@gmail.com'
mail = Mail(app)


#Webpage Rendering
@app.route('/',methods=['GET','POST'])
def home():
    return render_template('index.html')

@app.route('/login',methods=['GET','POST'])
def user_login():
    if request.method=="GET":
        return render_template('login.html')
    if request.method=="POST":
        email_mob=request.form['email/phone']
        password=request.form['password']

        #Condition for empty form
        if(len(email_mob) and len(password) == 0):
            flash(" Enter login credentials ")
            return redirect(url_for('user_login'))

        #Hashing Password
        h = hashlib.sha256(password.encode())
        pass_w=h.hexdigest()

        #Credential Authentication
        query = "SELECT * FROM UAD WHERE PASSWORD=?;"
        stmt = ibm_db.prepare(conn, query)
        ibm_db.bind_param(stmt,1,pass_w)
        ibm_db.execute(stmt)
        eac_cred = ibm_db.fetch_assoc(stmt)
        
        if eac_cred: 
            if email_mob == eac_cred['EMAIL'] or email_mob == eac_cred['MOBILE']:
                return redirect(url_for('user_login'))
        
        else:
            flash(" Invalid Credentials. Try Again. ")
            return redirect(url_for('user_login'))

@app.route('/signup',methods=['GET','POST'])
def user_signup():
    if request.method=="GET":
        return render_template('signup.html')
    if request.method=="POST":
        fname=request.form['fname']
        lname=request.form['lname']
        email=request.form['email']
        mob_no=request.form['mob']
        pass_w=request.form['password']
        c_pass_w=request.form['cpassword']

        #Flagging for alert event
        acc_flag=0

        #Condition for empty form

        if (len(fname) and len(lname) and len(email) and len(mob_no) and len(pass_w)) == 0 :
            flash( "Enter Details to Submit Form ")
            return redirect(url_for('user_signup'))
        
        #Checking for password mismatch

        if pass_w!=c_pass_w:
            flash(" Password Mismatched ")
            return redirect(url_for('user_signup'))
        

        #Hashing Password
        h = hashlib.sha256(pass_w.encode())
        pass_w=h.hexdigest()

        #Checking for already existing credential

        query = "SELECT * FROM UAD WHERE EMAIL =?;"
        stmt = ibm_db.prepare(conn, query)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        if account:
            acc_flag=1
            return render_template('signup.html',msg="User with this e-mail already exists.",flag=acc_flag)
        else:
            insert_query = "INSERT INTO UAD(FNAME,LNAME,EMAIL,MOBILE,PASSWORD) VALUES (?,?,?,?,?);"
            prep_stmt = ibm_db.prepare(conn, insert_query)
            ibm_db.bind_param(prep_stmt, 1, fname)
            ibm_db.bind_param(prep_stmt, 2, lname)
            ibm_db.bind_param(prep_stmt, 3, email)
            ibm_db.bind_param(prep_stmt, 4, mob_no)
            ibm_db.bind_param(prep_stmt, 5, pass_w)
            ibm_db.execute(prep_stmt)

            #Mail API
            msg = Message('Account Confirmation E-Mail',recipients=[email])
            msg.body = (f"Hi {fname},\nGreetings from PET Team!\nYou have successfully registered to our application.\nClick the below link to continue.\nhttp://127.0.0.1:5000/login")
            mail.send(msg)
            print("Msg Sent to recipient")

            #Flash for successful account creation
            flash(" Account Created Successfully. Check e-mail for confirmation ")
            return redirect(url_for('user_signup'))

@app.route('/password_reset',methods=['GET','POST'])
def user_reset():
    # Min Password Length
    N = 14
 
    # using secrets.choice()
    # generating random strings
    res = str(''.join(secrets.choice(string.ascii_uppercase + string.digits)
              for i in range(N)))
    if request.method=="GET":
        return render_template('reset.html')
    if request.method=="POST":
        email=request.form['email']

        #Hashing Password
        h = hashlib.sha256(res.encode())
        rand_pass=h.hexdigest()

        #Query to Update Value
        query="SELECT * FROM UAD WHERE EMAIL=?;"
        stmt=ibm_db.prepare(conn,query)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        chek_record=ibm_db.fetch_assoc(stmt)
        
        pid = chek_record['UID']
        update_query = "UPDATE UAD SET PASSWORD = ? WHERE UID = ?"
        up_stmt=ibm_db.prepare(conn,update_query)
        ibm_db.bind_param(up_stmt,1,rand_pass)
        ibm_db.bind_param(up_stmt,2,pid)
        ibm_db.execute(up_stmt)
        msg = Message('Password Reset',recipients=[email])
        msg.body = (f"Greetings from PET Team!\nHere is your reset password:\t{res}.\nUse the the above password and login using the below link.\nhttp://127.0.0.1:5000/login")
        mail.send(msg)
        print("Msg Sent")

        #flash mail
        flash(" Check your mail for reset password. ")
        return redirect(url_for('user_reset'))
    else:
        flash(" E-Mail not found in record! ")
        return redirect(url_for('user_reset'))
