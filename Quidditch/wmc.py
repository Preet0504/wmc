from flask import Flask, render_template, request, redirect, url_for, session
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import bcrypt

uri = "mongodb+srv://kingpreetpatel:mongodb@cluster0.pirltzr.mongodb.net/?retryWrites=true&w=majority"
app = Flask(__name__,template_folder="templates",static_folder="static")
app.secret_key = 'key'
app.static_folder = 'static'


# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client['quidditch']
@app.route("/")
def first():
    return render_template('first.html')

@app.route("/login",methods=['GET','POST'])
def login():
    if request.method == 'POST':
        users = db['user']
        admins = db['admin']
        check_admin = admins.find_one({'admin_id':request.form['username']})
        check_user = users.find_one({'username':request.form['username']})
        if check_user:
            if bcrypt.hashpw(request.form['password'].encode('utf-8'),check_user['password']) == check_user['password']:
                print('User logged in successfully')
                session['username']=request.form['username']
                return redirect(url_for('home'))
            else:
                print('fysoab')
        elif check_admin:
            if check_admin['password'] == request.form['password']:
                print('Admin logged in successfully')
                session['admin_id']=request.form['username']
                return redirect(url_for('admin'))
        
        else:
            print('fysoab')
    print('nothing happened')
    return render_template('login.html')

@app.route("/register",methods = ['POST','GET'])
def register():
    if request.method == 'POST':
        users = db['user']
        existing_user = users.find_one({'username':request.form['username']})
        existing_email = users.find_one({'email':request.form['email']})
        if existing_user is None and existing_email is None:
            hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'),bcrypt.gensalt())
            users.insert_one({'name':request.form['name'],'username':request.form['username'],'email':request.form['email'],'password':hashpass})
            print('User registered successfully')
            session['username'] = request.form['username']
            return redirect(url_for('home'))
        else:
            print('fysoab')
    print('nothing happened')
    return render_template('register.html')

@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/login")
def logout():
    session.pop()
    return redirect(url_for('login'))

@app.route("/admin")
def admin():
    return render_template('admin.html')

@app.route("/home/gryffindor")
def gryffindor():
    players = []
    player_data = db['players']
    player_range = player_data.find({"House":{"$in":["Gryffindor"]}},{"_id":0})
    for i in player_range:
        players.append([i])
    print(players)
    return render_template('gryffindor.html',players=players,length=len(players))

@app.route("/home/slytherin")
def slytherin():
    players = []
    player_data = db['players']
    player_range = player_data.find({"House":{"$in":["Slytherin"]}},{"_id":0})
    for i in player_range:
        players.append([i])
    return render_template('slytherin.html',players=players,length=len(players))

app.debug = True
app.run()