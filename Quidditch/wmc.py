from flask import Flask, render_template, request, redirect, url_for, session,Response
import pymongo
from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId
from gridfs import GridFS
from werkzeug.utils import secure_filename
from pymongo.errors import InvalidDocument
from pymongo.server_api import ServerApi
import bcrypt
import random
import copy
from flask_mail import Mail, Message
import datetime
import stripe

uri = "mongodb+srv://kingpreetpatel:mongodb@cluster0.pirltzr.mongodb.net/?retryWrites=true&w=majority"
app = Flask(__name__,template_folder="templates",static_folder="static")
app.secret_key = 'key'
app.static_folder = 'static'


# Create a new client and connect to the server
client = MongoClient(uri,server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client['quidditch']
fs = GridFS(db)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'kingpreetpatel@gmail.com'  # Replace with your Gmail email
app.config['MAIL_PASSWORD'] = 'xdzkjdlqueckriau'        # Replace with your Gmail password
app.config['MAIL_DEFAULT_SENDER'] = 'kingpreetpatel@gmail.com'

# Initialize the Mail extension
mail = Mail(app)

def send_email(to_address, subject, body):
    msg = Message(subject, recipients=[to_address], body=body)
    mail.send(msg)

def send_event_notification(event_description):
    e=[]
    event_name = 'New Match Scheduled'
    user_emails = db['user']
    email = user_emails.find({})
    for i in email:
        e.append(i['email'])
    subject = f'New Event: {event_name}'
    body = f'Event: {event_name}\nDescription: {event_description}\n\nThis is an email notification for the newly created event.'
    recipients=e
    print(recipients)
    msg = Message(subject=subject, recipients=recipients, body=body)
    mail.send(msg)

@app.route("/")
def first():
    session['admin_id']=0
    session['username']=0
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
    if session['username'] or session['admin_id']:
        events=[]
        event = db['schedule']
        event_range = event.find({},{"_id":0}).sort("Date",1)
        count=0
        for i in event_range:
            events.append(i)
            if count==2:
                break
            count+=1
        print(events)
        return render_template('home.html',events=events,user=session['username'])

@app.route("/login")
def logout():
    session['username']=0
    session['admin_id']=0
    return redirect(url_for('login'))

@app.route("/home/gryffindor")
def gryffindor():
    if session['username']:
        players = []
        player_data = db['team']
        player_range = player_data.find({"House":"Gryffindor"},{"Id":1,"_id":0})
        for i in player_range:
            players.append(i)
        print(players)
        return render_template('gryffindor.html',players=players)

@app.route("/home/gryffindor/gteam",methods=['GET','POST'])
def gteam():
    if session['username']:
        players=[]
        player = db['images']
        if request.method == 'POST':
            Id = int(request.form['Id'])
            player_range = player.find({"House":"Gryffindor","Id":Id})
            for i in player_range:
                players.append(i)
            print(players)
            return render_template('filter.html',players=players,length=len(players))
        return render_template('gryffindor.html')

@app.route("/home/ravenclaw")
def ravenclaw():
    if session['username']:
        players = []
        player_data = db['team']
        player_range = player_data.find({"House":"Ravenclaw"},{"Id":1,"_id":0})
        for i in player_range:
            players.append(i)
        print(players)
        return render_template('ravenclaw.html',players=players)

@app.route("/home/ravenclaw/rteam",methods=['GET','POST'])
def rteam():
    if session['username']:
        players=[]
        player = db['images']
        if request.method == 'POST':
            Id = int(request.form['Id'])
            player_range = player.find({"House":"Ravenclaw","Id":Id})
            for i in player_range:
                players.append(i)
            print(players)
            return render_template('filter.html',players=players,length=len(players))
        return render_template('ravenclaw.html')

@app.route("/home/slytherin")
def slytherin():
    if session['username']:
        players = []
        player_data = db['team']
        player_range = player_data.find({"House":"Slytherin"},{"Id":1,"_id":0})
        for i in player_range:
            players.append(i)
        print(players)
        return render_template('slytherin.html',players=players)

@app.route("/home/slytherin/steam",methods=['GET','POST'])
def steam():
    if session['username']:
        players=[]
        player = db['images']
        if request.method == 'POST':
            Id = int(request.form['Id'])
            player_range = player.find({"House":"Slytherin","Id":Id})
            for i in player_range:
                players.append(i)
            print(players)
            return render_template('filter.html',players=players,length=len(players))
        return render_template('slytherin.html')

@app.route("/home/hufflepuff")
def hufflepuff():
    if session['username']:
        players = []
        player_data = db['team']
        player_range = player_data.find({"House":"Hufflepuff"},{"Id":1,"_id":0})
        for i in player_range:
            players.append(i)
        print(players)
        return render_template('hufflepuff.html',players=players)

@app.route("/home/hufflepuff/hteam",methods=['GET','POST'])
def hteam():
    if session['username']:
        players=[]
        player = db['images']
        if request.method == 'POST':
            Id = int(request.form['Id'])
            player_range = player.find({"House":"Hufflepuff","Id":Id})
            for i in player_range:
                players.append(i)
            print(players)
            return render_template('filter.html',players=players,length=len(players))
        return render_template('hufflepuff.html')

@app.route("/admin",methods=['POST','GET'])
def admin():
    if session['admin_id']:
        print(session['admin_id'])
        msg=''
        if request.method == 'POST':
            teamA = request.form['teamA']
            teamB = request.form['teamB']
            Aid = request.form['Aid']
            Bid = request.form['Bid']
            Aid = int(Aid)
            Bid = int(Bid)
            date = request.form['date']
            admin = db['schedule']
            team = db['images']
            check_A = team.find_one({"House":teamA,"Id":Aid})
            check_B = team.find_one({"House":teamB,"Id":Bid})
            if 'add' in request.form:
                check_event = admin.find_one({'date':date})
                if not check_event and check_A and check_B:
                    admin.insert_one({'teamA':teamA,'teamA_id':Aid,'teamB':teamB,'teamB_id':Bid,'date':date})
                    msg = "Schedule added successfully"
                    event_description = '{} {} vs {} {} happening on {}. Book your tickets now'.format(teamA,Aid,teamB,Bid,date)
                    send_event_notification(event_description=event_description)
                else:
                    msg = "event already exists or no such team exists"
                
            elif 'remove' in request.form:
                check_event = admin.find_one({'teamA':teamA,'teamA_id':Aid,'teamB':teamB,'teamB_id':Bid,'date':date})
                if check_event:
                    admin.delete_one({'teamA':teamA,'teamA_id':Aid,'teamB':teamB,'teamB_id':Bid,'date':date})
                    msg = "Schedule removed successfully"
                else:
                    msg = "No such event exists"
            else:
                msg=''
                print('Nothing Happened')
        else:
            print('fysoab')
        return render_template("admin.html",msg=msg)

@app.route("/admin/players",methods=['GET','POST'])
def players():
    if session['admin_id']:
        player = db['images']
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
    if session['admin_id']:
        events=[]
        event = db['schedule']
        event_range = event.find({},{"_id":0}).sort("Date",pymongo.ASCENDING)
        for i in event_range:
            events.append(i)
        print(events)
        return render_template('calendar.html',events=events)


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed image extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/home/team',methods=['GET','POST'])
def team():
    if session['username']:
        assigned_house=""
        position_counts = {'Seeker':0,'Keeper':0,'Beater':0,'Chaser':0}
        
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

            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                
            image_data = file.read()
            player_id = str(ObjectId())


            broomstick = request.form['broomstick']
            house = ['Gryffindor','Slytherin','Hufflepuff','Ravenclaw']
            print(name,position)
            registered_team = db['images']
            team_details = db['team']
            if 'add' in request.form:
                temp = copy.deepcopy(session['team'])
                player_exists = any(player['Name'] == name and player['Position'] == position for player in temp)
                loses = int(totalmatches)-int(wins)
                if not player_exists and loses>=0:
                    print('ok')
                    session['current_player'] = player_id
                    fs.put(image_data,filename=filename,player_id=player_id)
                    temp.append({"ID": player_id,"Name": name, "Age":int(age), "Position": position, "Total Matches":int(totalmatches), "Wins":int(wins), "Loses":loses, "Broomstick":broomstick, "Gender":gender})
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
                id = registered_team.find({"House":assigned_house},{"Id":1})
                if(len(session['team'])== 7):
                    
                    z = []
                    for item in id:
                        z.append(item["Id"])
                    z.append(0)
                    print(z)
                    y = max(z)+1
                    
                    team_details.insert_one({"House":assigned_house,"Id":y})
                    for new in session['team']:
                        new['House']=assigned_house
                        new['Id']=y
                    registered_team.insert_many(session['team'])
                    print('team registered successfully')
                    send_email(to_address=session['username'],subject="Team registration",body='Your team is registered successfully')
                    session['team'] = []
                else:
                    print('nothing happened')

            elif 'reset' in request.form:
                session['team']=[]
                

        return render_template('team-register.html',teams=session['team'],position_counts=position_counts,assigned_house=assigned_house) 


@app.route('/image/<player_id>')
def get_image(player_id):
    try:
        # Retrieve the image data from MongoDB GridFS using player_id
        image = fs.find_one({"player_id": player_id})
        if image:
            # Return the image data as binary
            return Response(image.read(), content_type='image/jpeg')
        else:
            # Return a default image or an error message if the image is not found
            # return send_file('path/to/default_image.jpg', mimetype='image/jpeg')
            print("NO Image Found")
    except Exception as e:
        # Handle any errors that may occur during image retrieval
        return str(e)
    
@app.route("/admin/event_teams")
def event_teams():
    if session['admin_id']:
        teams = db['images']
        team_set = set()  # Use a set to store unique combinations of "House" and "Id"
        team = []

        team_range = teams.find({}, {"House": 1, "Id": 1}).sort("Id",pymongo.ASCENDING)

        for item in team_range:
            # Get the "House" and "Id" values for the current item
            house_id_combination = (item['House'], item['Id'])

            # Check if the combination is already in the set
            if house_id_combination not in team_set:
                # If not, add it to the set and append the item to the team list
                team_set.add(house_id_combination)
                team.append(item)

        return render_template("event_teams.html", team=team)

@app.route('/home/user-events',methods=['GET','POST'])
def user_events():
    if session['username']:
        events=[]
        event = db['schedule']
        
        date = request.args.get('date')
        if date:
            filteredEvents = event.find({
                'date': date
            })
            for item in filteredEvents:
                events.append(item)
        else:
            allEvent = event.find({})
            for item in allEvent:
                events.append(item)
        return render_template('user-events.html',events=events)

@app.route('/home/event-info',methods=['GET','POST'])
def event_info():
    if session['username']:
        team_detail = db['team']
        team_player = db['images']
        if request.method == 'POST':
            if 'event' in request.form:
                playerA=[]
                playerB=[]
                teamA = request.form['teamA']
                teamB = request.form['teamB']
                teamA_id = int(request.form['teamA_id'])
                teamB_id = int(request.form['teamB_id'])
                print(teamA,teamA_id,teamB,teamB_id)
                
                teamA_detail = team_detail.find_one({"House":teamA,"Id":teamA_id})
                teamB_detail = team_detail.find_one({"House":teamB,"Id":teamB_id})
                teamA_player = team_player.find({"House":teamA,"Id":teamA_id}).sort("Position",pymongo.DESCENDING)
                teamB_player = team_player.find({"House":teamB,"Id":teamB_id}).sort("Position",pymongo.DESCENDING)
                for item in teamA_player:
                    playerA.append(item)
                for item in teamB_player:
                    playerB.append(item)
                print(teamA_detail)
                print(playerA)
                print(playerB)

                return render_template('events-info.html',teamA_detail=teamA_detail,teamB_detail=teamB_detail,playerA=playerA,playerB=playerB)
            
            if 'book' in request.form:
                teamA = request.form['teamA']
                teamB = request.form['teamB']
                teamA_id = int(request.form['teamA_id'])
                teamB_id = int(request.form['teamB_id'])
                return render_template('checkout.html')
                # return render_template('price.html',teamA=teamA,teamB=teamB,teamA_id=teamA_id,teamB_id=teamB_id)
        return render_template('events-info.html')

@app.route("/home/event-info/players-info",methods=['GET','POST'])
def players_info():
    if session['username']:
        players=[]
        name = request.form['Name']
        if request.method == 'POST':
            player = db['images']
            print(name)
            player_detail = player.find_one({"Name":name})
            print((player_detail))
            players.append(player_detail)
            return render_template('filter.html',players=players,length=1)
        return render_template('players.html')

@app.route("/admin/stats",methods=['GET','POST'])
def update_stats():
    if session['admin_id']:
        collection = db['schedule1']
        if request.method == 'POST':
            WteamName = request.form['winning_team']
            W_name,W_id = WteamName.split(' ')
            A_name,A_id = request.form['teamA'].split(' ')
            W_id = int(W_id)
            A_id = int(A_id)
            B_name,B_id = request.form['teamB'].split(' ')
            B_id = int(B_id)
            if W_name == A_name and W_id == A_id:
                winningTeam = A_name
                winning_id = A_id
                losingTeam = B_name
                losingId = B_id
            else:
                winningTeam = B_name
                winning_id = B_id
                losingTeam = A_name
                losingId = A_id
            
            collection1 = db['team1']
            collection1.update_one({'House': winningTeam,'Id': winning_id},
                            {'$inc': {'Wins': 1, 'Total Matches': 1}})

            # Update the losing team's Loses and total matches
            collection1.update_one({'House':losingTeam,'Id': losingId },
                                {'$inc': {'Loses': 1, 'Total Matches': 1}})
            
            collection.update_one({'teamA': A_name,'teamA_id': A_id,'teamB': B_name,'teamB_id': B_id},
                            {'$set': {'updated': 'yes'}})

            # return render_template('stats.html',events1=events1,events2=events2) 

        
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        updated_yes_query = {"date": {"$lt": today}, "updated": "yes"}
        updated_no_query = {"date": {"$lt": today}, "updated": "no"}
        events_no = collection.find(updated_no_query)
        events_yes = collection.find(updated_yes_query)
        events1 = []
        events2 = []
        for event in events_no:
            events1.append(event)
        
        
        for event in events_yes:
            events2.append(event)


        return render_template('stats.html',events1=events1,events2=events2)



public_key = "pk_test_51NZl8bSJIq2XxF7LxWUfY06w9BDfJCd2gRqvf7aAeYSxp3irUAk3i8gXDgVJqVOGv9TdacAUEUUSwEIaQA8Dm4Fi00AbxsADFn"
stripe.api_key = 'sk_test_51NZl8bSJIq2XxF7LLOONAsEvptriH1V2Cyu0SQP6Fen3HO2fgRYc004WEtnpnc5SDYo2vCb0q7rbJn5V0Uok7fws00WboSbcon'
YOUR_DOMAIN = 'https://hpquidditch.onrender.com/'
# YOUR_DOMAIN = 'http://localhost:4242'


@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': 'price_1Nb1hwSJIq2XxF7LcfbslfTq',
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + 'success',
            cancel_url=YOUR_DOMAIN + 'cancel',
        )
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)

@app.route('/success')
def success():
    #send_email(to_address=session['username'],subject='Payment',body='Payment done successfully')
    return render_template('success.html')

@app.route('/cancel')
def cancel():
    return render_template('cancel.html')
app.debug = True
app.run(host='0.0.0.0')
