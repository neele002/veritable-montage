import os
import csv
import json
import urllib
from datetime import date
from flask import Flask,request,render_template,flash, redirect,url_for
from flask_login import LoginManager, current_user, login_user,logout_user,login_required
from wtforms import validators
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
from wtforms.fields import TextField,TextAreaField,DecimalField,SubmitField
from wtforms.fields.html5 import DateField
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import exc,func
from sqlalchemy.sql import label
from database import db_session
from zmodels import User,Game,GameType,TaskUnit,GameTask,GamePlayers,PlayerGameTask
#from forms import unit_choices

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])

from forms import LoginForm,SignUpForm,AddGameTypeForm,AddGameForm,GameClickForm,MyBaseForm,ResetForm,EditGameForm

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view =  "login"

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
        
@login_manager.user_loader
def load_user(userid):
    return User.query.filter(User.id==userid).first()


    
@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:     
        user =  {'nickname': current_user.username } 
    else:
        user =  {'nickname': 'Howdy' } 
    
    return render_template("index.html",
                           title='Home',
                           user=user)

@app.route("/display")
@login_required
def display():
    user =  {'nickname': current_user.username } 
    lists =  {
	"game": {
		"name": "CrossFit Total Challenge",
        "division": {"label": "Division:", "value":"Beginner"},
        "bodyweight": {"label": "Body Weight:", "value":200,"value1":200},
		"tasks": [{
			"item": "Squat ",
			"value": 200,
			"value1": 240,
			"value2": 40
		}, {
			"item": "Press ",
			"value": 50,
			"value1": 60,
			"value2": 10
		}, {
			"item": "Deadlift ",
			"value": 220,
			"value1": 250,
			"value2": 30
		}],
		"total": {
			"item": "Total ",
			"value": 470,
			"value1": 550,
			"value2": 80
		}
	}
}
    total =  {"item": "Total ","value":470,"value1": 550,"value2": 80}
             
    flash('Loaded')
    return render_template("display.html",
                           title='Home',
                           lists=lists,
                           total=total,
                           user=user)

@app.route("/logout")
def logout():
    logout_user()
    flash('Logged out')
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        username = form.openid.data
        password =  form.password.data
        user = User.query.filter_by(username=username).first()
        if user:
            flash ('User exists')
            return redirect('register')
        user = User(username=username)
        user.hash_password(password)
        db_session.add(user)
        db_session.commit()
        flash('Registered')
        return redirect(url_for('register'))

    return render_template('register.html', form=form,title='Sign Up')
@app.route('/reset', methods=['GET', 'POST'])
def reset():
    form = ResetForm()
    if form.validate_on_submit():
        username = form.openid.data
        password =  form.password.data
        user = User.query.filter_by(username=username).first()
        if user:
            flash(password)
            user = User(username=username) 
            user.hash_password(password)
            db_session.query(User).filter(User.username==username).update({'password_hash': user.password_hash})
            db_session.commit()
            
            return redirect(url_for('login'))
        else:
            flash ('Not Found')
            return redirect('reset')

    return render_template('reset.html', form=form,title='Reset')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.email.data
        password = form.password.data
        rm =       form.remember_me.data
        user = User.query.filter_by(username=username).first()
        if user and user.is_active:
            if user.verify_password(password):
                login_user(user,remember=False)
                return redirect('/index')
            
        flash('Invalid login. Please try again.')
        return redirect('/login')
    return render_template('login.html', 
                           title='Sign In',
                           form=form)

@app.route('/gametype', methods=['GET', 'POST'])
@login_required
def gametype():
    
    form = AddGameTypeForm()
    if form.validate_on_submit():
        ftype = form.gametype.data
        
        gtype = GameType.query.filter_by(type=ftype).first()
        if gtype:
            flash ('Game Type Exists')
            return redirect('gametype')
       
        #mid = db_session.execute("select max(id)+1 from gametype")
        
        gtype = GameType(type=ftype)
        db_session.add(gtype)
        db_session.commit()
        flash('Added')
        return redirect(url_for('gametype'))

    return render_template('gametype.html', form=form)
@app.route('/game', methods=['GET', 'POST'])
@login_required
def game():
    
    form = AddGameForm()  

    x = json.loads(form.stuff.data)
    y = json.loads(form.puff.data)
    
    if form.button.data and form.task.data:
        x.append({"item" : form.task.data, "unit" : str(form.unit.data)})
        form.task.data = ''   
        
    if form.button1.data and form.firstname.data and form.lastname.data and form.email.data:
        y.append({"firstname" : form.firstname.data, "lastname" : form.lastname.data,"email" : form.email.data})
        form.firstname.data =''
        form.lastname.data =''
        form.email.data=''
        
    elif form.button1.data and form.upload.has_file:
        f = secure_filename(form.upload.data.filename)
        with open(f, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            next(reader)
            for row in reader:
                fname, lname = row[0].split()
                y.append({"firstname" : fname, "lastname" : lname,"email" : row[1]})
         
        
    form.stuff.data = json.dumps(x)
    form.puff.data = json.dumps(y)    
    if form.validate_on_submit() and form.sub.data:
        desc = form.desc.data
        gtype = form.gametype.data
        startdate = form.startdate.data
        enddate = form.enddate.data
        gtypeid = GameType.getid(gtype)
        game = Game.query.filter_by(desc=desc).first()
        if game:
            flash ('Game Exists')
        else:
            game = Game(gametype=gtypeid,desc=desc,startdate=startdate,enddate=enddate,createdby=current_user.id)
            
            try:
                db_session.add(game) 
                db_session.flush()
                o = 0
                for tasks in x:
                    o += 1
                    u = TaskUnit.query.filter_by(unit=tasks['unit']).first()
                    gametask = GameTask(gameid=game.id,order=o,task=tasks['item'],unit=u.id)
                    db_session.add(gametask)
                
                # Add user to own game
                gameplayers=GamePlayers(userid=current_user.id,gameid=game.id)    
                db_session.add(gameplayers)
                
                # Add players from forms
                for players in y:
                    user = User.query.filter_by(username=players['email']).first()
                    if user:
                        userid= user.id
                    else:
                        newuser =  User(username=players['email'])
                        newuser.lastname = players['lastname']
                        newuser.email =players['email']
                        newuser.firstname = players['firstname']
                        db_session.add(newuser)
                        db_session.flush()
                        userid = newuser.id
                        
                    gameplayers=GamePlayers(userid=userid,gameid=game.id)
                    db_session.add(gameplayers)
                db_session.commit()
                                            
                flash(game.id)
            except exc:
                flash(exc)
                  
            return redirect(url_for('game'))
    
    return render_template('game.html', x=x,y=y,form=form,title='Create a Game')
@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    if request.method=='GET':
        gameid = request.args.get('id')
    else:
        gameid = request.form['gameid']
    
    game =  Game.query.filter_by(id=gameid).first()
    tasks = GameTask.query.filter_by(gameid=gameid).all()
    players = db_session.query(User.id,User.firstname,User.lastname,User.email).filter\
        (GamePlayers.gameid==gameid,GamePlayers.userid == User.id).order_by(User.id)
    gametype = GameType.query.filter_by(id=game.gametype).first()
    
    
    
    form = EditGameForm()  
    
    form.gameid.data = gameid
    form.desc.data = game.desc
    form.gametype.data = gametype.type
    form.startdate.data = game.startdate
    form.enddate.data = game.enddate
    
    #   Stored in form
    x = json.loads(form.stuff.data)
    if len(x) == 0:
        for ot in tasks:
            x.append({"item" : ot.task, "unit" : ot.unit, "new" : "N"})
            
    y = json.loads(form.puff.data)
    if len(y) == 0:
         for op in players:
            y.append({"firstname" : op.firstname, "lastname" : op.lastname,"email" : op.email,"new" : "N"})
    
    if form.button.data and form.task.data:
        x.append({"item" : form.task.data, "unit" : str(form.unit.data),"new" : "Y"})
        form.task.data = ''   
        
    if form.button1.data and form.firstname.data and form.lastname.data and form.email.data:
        y.append({"firstname" : form.firstname.data, "lastname" : form.lastname.data,"email" : form.email.data,"new" : "Y"})
        form.firstname.data =''
        form.lastname.data =''
        form.email.data=''
        
    elif form.button1.data and form.upload.has_file:
        f = secure_filename(form.upload.data.filename)
        with open(f, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            next(reader)
            for row in reader:
                fname, lname = row[0].split()
                y.append({"firstname" : fname, "lastname" : lname,"email" : row[1], "new" : "Y"})
         
        
    form.stuff.data = json.dumps(x)
    form.puff.data = json.dumps(y)    
    
    if form.validate_on_submit() and form.sub.data:
        desc = form.desc.data
        gtype = form.gametype.data
        startdate = form.startdate.data
        enddate = form.enddate.data
        gtypeid = GameType.getid(gtype)
        game = Game.query.filter_by(desc=desc).first()
        if game:
            flash ('Game Exists')
        else:
            game = Game(gametype=gtypeid,desc=desc,startdate=startdate,enddate=enddate,createdby=current_user.id)
            
            try:
                db_session.add(game) 
                db_session.flush()
                o = 0
                for tasks in x:
                    o += 1
                    u = TaskUnit.query.filter_by(unit=tasks['unit']).first()
                    gametask = GameTask(gameid=game.id,order=o,task=tasks['item'],unit=u.id)
                    db_session.add(gametask)
                
                # Add user to own game
                gameplayers=GamePlayers(userid=current_user.id,gameid=game.id)    
                db_session.add(gameplayers)
                
                # Add players from forms
                for players in y:
                    user = User.query.filter_by(username=players['email']).first()
                    if user:
                        userid= user.id
                    else:
                        newuser =  User(username=players['email'])
                        newuser.lastname = players['lastname']
                        newuser.email =players['email']
                        newuser.firstname = players['firstname']
                        db_session.add(newuser)
                        db_session.flush()
                        userid = newuser.id
                        
                    gameplayers=GamePlayers(userid=userid,gameid=game.id)
                    db_session.add(gameplayers)
                db_session.commit()
                                            
                flash(game.id)
            except exc:
                flash(exc)
                  
            return redirect(url_for('edit'))
    
    return render_template('edit.html', x=x,y=y,form=form,title='Edit Game')
@app.route('/mygame', methods=['GET', 'POST'])
@login_required
def mygame():
    form = GameClickForm()
    # Enter scores
    if form.edit.data == 'True' and form.game.data > 0 and form.alter.data == 'False':
        return redirect(url_for('record',id=form.game.data,pid=current_user.id))
    #Enter Game
    if form.edit.data == 'False' and form.game.data > 0 and form.alter.data == 'True':
        return redirect(url_for('edit',id=form.game.data))
    # Show Players
    if form.game.data > 0:      
        players=db_session.query(User.id,User.firstname,User.lastname,GamePlayers.gender).filter\
        (GamePlayers.gameid==form.game.data,GamePlayers.userid == User.id).order_by(User.id)
        
        gt = db_session.query(Game.gametype,GameType.type).filter(Game.id == form.game.data,GameType.id == Game.gametype).first()
        
        tasks =   GameTask.query.filter_by(gameid = form.game.data).order_by(GameTask.order).all()
        
        huh = []
        
        # Query for Daily Task
        if gt.gametype ==2:
            thestuff = db_session.query(PlayerGameTask.gameplayersuserid,PlayerGameTask.gametaskid,label('reported', func.count(PlayerGameTask.gameplayersuserid)),label('reportedcnt', func.sum(PlayerGameTask.value1))).filter(PlayerGameTask.gameid==form.game.data).group_by(PlayerGameTask.gameplayersuserid,PlayerGameTask.gametaskid).all()
        
        
            for i,p in enumerate(players):
                huh.append({"userid" : p.id, "firstname" : p.firstname, "lastname" : p.lastname, "gender" : p.gender, 'reported' : 0, 'reportedcnt' : 0})
                for t in thestuff:
                    if p.id == t.gameplayersuserid:
                        huh[i]['reportedcnt'] = t.reportedcnt
                        huh[i]['reported'] = t.reported
        else:    
            
            thestuff = db_session.query(PlayerGameTask.gameplayersuserid,PlayerGameTask.gametaskid,GameTask.task,PlayerGameTask.value1,PlayerGameTask.value2,PlayerGameTask.diff).filter(PlayerGameTask.gameid==form.game.data,PlayerGameTask.gametaskid== GameTask.id).order_by(PlayerGameTask.gameplayersuserid,PlayerGameTask.gametaskid).all()
            for i,p in enumerate(players):
                huh.append({"userid" : p.id, "firstname" : p.firstname, "lastname" : p.lastname, "gender" : p.gender})
                for t in thestuff:
                    if p.id == t.gameplayersuserid:
                        huh[i][t.task] = t.value1
                        huh[i][t.task+'a'] = t.value2
                        huh[i][t.task+'d'] = t.diff
            #db_session.query(User.firstname,User.lastname,User.gender,User.division,GameTask.order,GameTask.t#ask,PlayerGameTask.value1,PlayerGameTask.value2,PlayerGameTask.diff).filter(GamePlayers.id==PlayerGameTask.gameplayersid,GameP#layers.gameid==form.game.data,PlayerGameTask.gameid==GameTask.gameid,PlayerGameTask.gametaskid==GameTask.id,GamePlayers.userid#==User.id).order_by(GamePlayers.gender,GamePlayers.division,GamePlayers.lastname,GamePlayers.firstname)
        
        
    else:
        gt = []
        players =[]
        tasks=[]
        thestuff=[]
        huh = []
    games = db_session.query(Game.id,Game.desc,Game.startdate,Game.enddate,GameType.type,Game.createdby).filter(GamePlayers.userid  == current_user.id,Game.id == GamePlayers.gameid, Game.gametype == GameType.id)

    return render_template('mygame.html',form=form,title='My Games',games=games,players=players,tasks=tasks,huh=huh,gt=gt)

@app.route('/record',methods=['GET','POST'])
@login_required
def record():
# For get retrieve game and playerid from url parameters.
# For post get it from the request

    if request.method=='GET':
        gameid = request.args.get('id')
        playerid = request.args.get('pid')
    else:
        gameid = request.form['game']
        playerid = request.form['player']
        
#Fetch game, gametype, player and results data
    
    game = Game.query.filter_by(id=gameid).first()
    gtype = GameType.query.filter_by(id=game.gametype).first()
    
    player = db_session.query(GamePlayers.id ,GamePlayers.userid,GamePlayers.gameid,User.firstname,User.lastname).filter(GamePlayers.userid==playerid,User.id==GamePlayers.userid).first()
    
    results = db_session.query(PlayerGameTask.value1date,PlayerGameTask.value1).filter(PlayerGameTask.gameplayersuserid==playerid,gameid==gameid).all()
    
    days =[]
    
    for day in results:
        days.append(day.value1date.strftime('%d %m %Y'))
        
    today = date.today()
    showcalendar = False
    
#Dynamically create the form and add tasks
    class F(MyBaseForm):
        pass
    
    tasks = GameTask.query.filter_by(gameid = gameid).order_by(GameTask.order).all()

    # Entry date for daily challenges

    if game.gametype ==2:
       setattr(F, 'EntryDate', TextField('EntryDate',id='etshow',default=today))
       showcalendar = True
    
    # Add each task to the form    
    for i,name in enumerate(tasks):
        #a = ''
        #b = ''
        after = 'After :'
        #try:
         #   a += results[i].value1
        #  b += str(results[i].value2 or "")
        #except IndexError:
         #   pass
        # Generate a timefield or decimal fields based on unit type
        if name.unit == 3:
            setattr(F, name.task, DateTime(name.task,description='Task-1',id=name.id))
            if game.gametype == 1:
                 after += name.task
                 setattr(F, after, DateTime(after,description='Task-2',id=name.id))
        else:
            setattr(F, name.task, DecimalField(name.task,description='Task-1',id=name.id))
            if game.gametype == 1:
                after += name.task
                setattr(F, after, DecimalField(after,description='Task-2',id=name.id))  
                
    # Comment and Submit Button
    setattr(F, 'Comments', TextAreaField(validators=[DataRequired()]))
    setattr(F, 'Submit', SubmitField())
    
    form = F()
    # save stuff in the form
    form.game.data = game.id
    form.tasks.data = len(tasks)
    form.player.data = player.userid
    form.gametype.data = gtype.id
    
    if form.validate_on_submit():
        # Type 1 - Daily tasks entered for a period of time x tasks per day.
        # Type 2 - Before and after between two dates - value 1 and Value 2 for each task.  Entry might be split
        # result is an array of task values.
        
        subresults =[]
        taskdate = today
        
        for t in form:
            if t.description == 'Task-1':
                subresults.append({"value1" : t.data,"id": t.id})
                #taskid = t.id
            if t.description == 'Task-2':
                l = len(subresults)
                subresults[l-1]["value2"] = t.data
                #taskid = t.id    
            if t.id == 'etshow':
                taskdate =  t.data
                
        # This is the array of tasks
        for r in subresults:
            # value2 only exists in before after games
            if 'value2' in r:
                value2 = r['value2']
                diff = r['value2'] - r['value1']
            else:
                value2 =0
                diff = 0
            # Add player game task record
            try:
                flash(str(r['value1']))
                playergametask=PlayerGameTask(gameplayersid=player.id,
                                               gameplayersuserid=player.userid,
                                               gameid=game.id,
                                               gametaskid=r['id'],
                                               value1=r['value1'],
                                               value2=value2,
                                               diff=diff,
                                               value1date=taskdate)
                                               #,value2=row[17],diff=row[18])
                db_session.add(playergametask)
            except exc:
                flash(exc)
                
        db_session.commit()
            
        
        return redirect(url_for('mygame'))    
        
    return render_template('record.html',form=form,game=game,player=player,gametype=gtype,showcalendar=showcalendar,days=days)


if __name__ == '__main__':
    app.run()