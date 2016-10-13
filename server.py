from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
from sqlalchemy.sql import text
app = Flask(__name__)
mysql = MySQLConnector(app,'mydb')
app.secret_key = 'ThisIsSecret'

@app.route('/')
def index():                       # run query with query_db()
    return render_template('index.html') # pass data to our template

@app.route('/register', methods=['POST'])
def register():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = request.form['password']
    if validate_user(request.form):
        insert_query = "INSERT INTO users (first_name, last_name, email, pwd, created_at, updated_at) VALUES (:first_name, :last_name, :email, :pwd, NOW(), NOW())"
        query_data = { 'first_name': first_name, 'last_name': last_name, 'email': email, 'pwd': password }
        mysql.query_db(insert_query, query_data)
        flash('success! please log in')
        return redirect('/')
    else:
        flash('validation errors found')
        return redirect ('/')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    user_query = "SELECT * FROM users WHERE email = :email LIMIT 1"
    data_query = { 'email': email }
    log_response = mysql.query_db(user_query, data_query)
    print '-----------'
    print log_response
    if log_response:
        session['logged_in'] = True
        session['user'] = log_response[0] ['id']
    else:
        flash("login failed")
        return redirect ('/')
    return redirect ('/the_wall/'+str(session['user']))

def validate_user(form):
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = request.form['password']
    is_valid = True

    if len(first_name) < 1:
        flash("first name cannot be empty")
        is_valid = False
    if any(char.isdigit() for char in first_name):
        flash("name cannot contain numbers")
        is_valid = False
    if len(last_name) < 1:
        flash("last name cannot be empty")
        is_valid = False
    if any(char.isdigit() for char in last_name):
        flash("name cannot contain numbers")
        is_valid = False
    if len(email) < 1:
        flash("Email cannot be blank!")
        is_valid = False
    if len(password) < 1:
        flash("password cannot be empty")
        is_valid = False
    return is_valid

@app.route('/the_wall/<current_id>')
def show(current_id):
    if session['logged_in'] == True:

        query1 = "SELECT * FROM users WHERE id = :current_id"
        data1 = {"current_id": current_id}
        name_query = mysql.query_db(query1, data1) #user id

        query2 = "SELECT * from users LEFT JOIN messages ON users.id = messages.users_id1"
        m_response = mysql.query_db(query2) #all_messages

        query3 = "SELECT * from messages LEFT JOIN comments ON messages.users_comments_id1 = comments.messages_id"
        c_response = mysql.query_db(query3) #

        return render_template('the_wall.html', messages=m_response, comments=c_response, name=name_query)


    else:
        flash('please login')
        return redirect('/')

@app.route('/new_message', methods=['POST'])
def create():
    message = request.form['message']
    # Write query as a string. Notice how we have multiple values
    # we want to insert into our query.
    query = "INSERT INTO messages (users_id1, message, created_at, updated_at) VALUES (:id, :message, NOW(), NOW())"
    # We'll then create a dictionary of data from the POST data received.
    data = {
             'id': session['user'],
             'message': message
           }
    # Run query, with dictionary values injected into the query.
    mysql.query_db(query, data)
    return redirect('/the_wall/'+str(session['user']))

app.run(debug=True)
