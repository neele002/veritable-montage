import csv
from database import db_session
from zmodels import User,Game,GameType,TaskUnit,GameTask,GamePlayers,PlayerGameTask,Users
#from forms import unit_choicesfrom database import db_session

username = 'user1'
password  ='hereisapassword'

user = User(username=username)
        user.hash_password(password)
        db_session.add(user)
        db_session.commit()
with open('cft.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    next(reader)
    for row in reader:
        fname, lname = row[0].split()
        gameplayers=GamePlayers(gameid=1,lastname=lname,firstname=fname,gender=row[1],division=row[2],weight1=row[7],weight2=row[8])
        db_session.add(gameplayers)
        db_session.flush()
        playergametask = PlayerGameTask(gameplayersid=gameplayers.id,gameid=1,gametaskid=8,value1=row[16],value2=row[17],diff=row[18])
        db_session.add(playergametask)
        playergametask = PlayerGameTask(gameplayersid=gameplayers.id,gameid=1,gametaskid=9,value1=row[19],value2=row[20],diff=row[21])
        db_session.add(playergametask)
        playergametask = PlayerGameTask(gameplayersid=gameplayers.id,gameid=1,gametaskid=10,value1=row[22],value2=row[23],diff=row[24])
        db_session.add(playergametask)
        playergametask = PlayerGameTask(gameplayersid=gameplayers.id,gameid=1,gametaskid=12,value1=row[10],value2=row[11],diff=row[12])
        db_session.add(playergametask)
db_session.commit()
