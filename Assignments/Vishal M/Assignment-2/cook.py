from flask import Flask,redirect,render_template,request,flash,session
import sqlite3
import os
app = Flask(__name__)
app.secret_key = os.urandom(24)
con = sqlite3.connect('database.db')
con.execute('CREATE TABLE IF NOT EXISTS person (pid INTEGER PRIMARY KEY , firstname TEXT , lastname TEXT , email TEXT UNIQUE, mobile INTEGER , username TEXT , password1 PASSWORD , password2 PASSWORD)')
con.close()
@app.route('/')
def home():
    return render_template( 'index.html')
@app.route('/err')
def error():
    return render_template('error.html')
@app.route('/register', methods = ['POST','GET'])
def register():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        mobile = request.form['num']
        uname = request.form['uname']
        pass1 = request.form['password1']
        pass2 = request.form['password2']
        if pass1 != pass2:
            flash('please enter same password!')
            return redirect('/register')
        else:
            try:
                con = sqlite3.connect('database.db')
                cur = con.cursor()
                cur.execute('INSERT INTO person(firstname,lastname,email,mobile,username,password1,password2)values(?,?,?,?,?,?,?)',
                (fname,lname,email,mobile,uname,pass1,pass2))
                con.commit()
                con.close()
                return redirect('/login')
            except:
                flash('email must be unique')
                return redirect('/register')
    return render_template('register.html')
@app.route('/login',methods = ['POST','GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password1']
        con = sqlite3.connect('database.db')
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute('SELECT * FROM person where email = ? and password1 = ?',(email,password))
        data = cur.fetchone()
        if data :
            session['email'] = data['email']
            con.close()
            return redirect('/upro')
        else:
            flash('please enter the credentials correctly!')
            return redirect('/login')
    return render_template('login.html')
@app.route('/upro')
def upro():
    return render_template('upro.html')
@app.route('/forgot',methods = ['POST','GET'])
def forgotform():
    if request.method == 'POST':
        email = request.form['email']
        uname = request.form['username']
        pass1 = request.form['password1']
        pass2 = request.form['password2']
        con = sqlite3.connect('database.db')
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute('SELECT * FROM person where email = ? and username = ? ',(email,uname))
        data = cur.fetchone()
        did = data['pid']
        con.close()
        if data and pass1 == pass2 :
            con = sqlite3.connect('database.db')
            cur = con.cursor()
            cur.execute('UPDATE person SET password1 = ?,password2 = ? where pid = ?',(pass1,pass2,did))
            con.commit()
            con.close()
            flash('successfully password reset done!')
            return redirect('/login')
        elif pass1 != pass2:
            flash('password and confirmpassword must be same!')
            return redirect('/forgot')
        else:
            flash('something gone wrong, please try again correctly!')
            return redirect('/forgot')
    return render_template('forgotform.html')
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
if __name__ == '__main__':
    app.run(debug=True)