from flask import Flask, render_template, request, redirect, url_for, session
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import bcrypt
import random
import copy

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
    
@app.route('/admin/events',methods=['GET','POST'])
def events():
    events=[]
    event = db['schedule']
    event_range = event.find({},{"_id":0})
    for i in event_range:
        events.append(i)
    print(events)
    return render_template('calendar.html',events=events)


@app.route('/home/team',methods=['GET','POST'])
def team():
    assigned_house=""
    position_counts = {'Seeker':0,'Keeper':0,'Beater':0,'Chaser':0}
    if 'g' not in session:
        session['g']=0
    if 's' not in session:
        session['s']=0
    if 'r' not in session:
        session['r']=0
    if 'h' not in session:
        session['h']=0
    if 'team' not in session:
        print('not working')
        session['team']=[]

    if request.method == 'POST':
        print('noice')
        x = random.randint(0,3)
        name = request.form['name']
        position = request.form.get('position')
        age = request.form.get('age')
        gender = request.form.get('gender')
        totalmatches = request.form['totalmatches']
        wins = request.form['wins']
        
        broomstick = request.form['broomstick']
        house = ['Gryffindor','Slytherin','Hufflepuff','Ravenclaw']
        print(name,position)
        registered_team = db['team_registration']
        if 'add' in request.form:
            # check_player = team.find_one({"Name":name},{"Position":position})
            
            # if check_player:
            #     return render_template('team-register.html',msg='Player already Exists')
            # team.insert_one({"Name":name,"Position":position,"House":house[x]})
            temp = copy.deepcopy(session['team'])
            player_exists = any(player['Name'] == name and player['Position'] == position for player in temp)
            loses = int(totalmatches)-int(wins)
            if not player_exists and loses>=0:
                print('ok')
                temp.append({"Name": name, "Age":int(age), "Position": position, "Total Matches":int(totalmatches), "Wins":int(wins), "Loses":loses, "Broomstick":broomstick, "Gender":gender})
                session['team'] = temp
            for player in session['team']:
                position = player['Position']
                if position in position_counts:
                    position_counts[position] += 1
                else:
                    position_counts[position] = 1

        elif 'register' in request.form:
            assigned_house = house[x]
            
            print(len(session['team']))
            if(len(session['team'])==7):
                if assigned_house == 'Gryffindor':
                    session['g']+=1
                    update = {'$set':{'House':assigned_house,'Id':session['g']}}
                elif assigned_house == 'Slytherin':
                    session['s']+=1
                    update = {'$set':{'House':assigned_house,'Id':session['s']}}
                elif assigned_house == 'Ravenclaw':
                    session['r']+=1
                    update = {'$set':{'House':assigned_house,'Id':session['r']}}
                elif assigned_house == 'Hufflepuff':
                    session['h']+=1
                    update = {'$set':{'House':assigned_house,'Id':session['h']}}
                registered_team.insert_many(session['team'])
                filter={}
                
                registered_team.update_many(update=update,filter=filter)
                print('team registered successfully')
                del session['team']
            else:
                print('nothing happened')

        elif 'reset' in request.form:
            session['team']=[]
              

    return render_template('team-register.html',teams=session['team'],position_counts=position_counts,assigned_house=assigned_house) 

app.debug = True
app.run()