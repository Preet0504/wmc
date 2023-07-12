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
        check_admin = admins.find_one({'username':request.form['username']})
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

@app.route("/admin",methods=['POST','GET'])
def admin():
    msg=''
    if request.method == 'POST':
        teamA = request.form['teamA']
        teamB = request.form['teamB']
        date = request.form['date']
        admin = db['schedule']
        if 'add' in request.form:
            check_event = admin.find_one({'date':date})
            if not check_event:
                admin.insert_one({'teamA':teamA,'teamB':teamB,'date':date})
                msg = "Schedule added successfully"
            else:
                msg = "event already exists mf"
        elif 'remove' in request.form:
            check_event = admin.find_one({'teamA':teamA,'teamB':teamB,'date':date})
            if check_event:
                admin.delete_one({'teamA':teamA,'teamB':teamB,'date':date})
                msg = "Schedule removed successfully"
            else:
                msg = "No such event exists mf"
        else:
            msg=''
            print('Nothing Happened')
    else:
        print('fysoab')
    return render_template("admin.html",msg=msg)

@app.route("/admin/players",methods=['GET','POST'])
def players():
    player = db['players']
    players=[]
    houses=request.form.getlist('house')
    positions=request.form.getlist('position')
    name = request.form.get('search')
    if name is not None and request.method=='POST':
        player_range = player.find({"Name":{"$regex":name,"$options":'i'}},{"_id":0})
        for item in player_range:
            players.append(item)
        return render_template('filter.html',players=players,length=len(players))
    if len(houses) and len(positions):
        player_range = player.find({"$and":[{"House":{"$in":houses}},{"Position":{"$in":positions}}]},{"_id":0})
        for item in player_range:
            players.append(item)
        return render_template('filter.html',players=players,length=len(players))
    elif len(houses) or len(positions):
        player_range = player.find({"$or":[{"House":{"$in":houses}},{"Position":{"$in":positions}}]},{"_id":0})
        for item in player_range:
            players.append(item)
        print(players)
        return render_template('filter.html',players=players,length=len(players))
    else:
        return render_template('players.html')
    

app.debug = True
app.run()