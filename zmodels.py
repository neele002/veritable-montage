from flask_login import UserMixin
from sqlalchemy import Column,Integer,String,ForeignKey,DateTime,Date,Numeric,Boolean
from sqlalchemy.orm import relationship
from passlib.apps import custom_app_context as pwd_context
from database import Base

class User(UserMixin,Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(120), index=True, unique=True)
    password_hash = Column(String(120), nullable=False)
    lastname = Column(String(120))
    firstname = Column(String(120))
    email = Column(String(254))
    active   =  Column(Boolean, nullable=False)
    #posts = relationship('Post', backref='author', lazy='dynamic')

    def __init__(self, username):
        self.username = username
        #self.password_hash = password
        self.active = False
    
    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)
    
    @property
    def is_active(self):
        return self.active
    
    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 
        
    def __repr__(self):
        return '<User %r>' % (self.username)
class TaskUnit(Base):
    __tablename__ = 'taskunit'
    id = Column(Integer, primary_key = True)
    unit = Column(String(140), index=True, unique=True)
    
    def __init__(self,unit):
        self.unit = unit
       
    def getid(self):
        return (self.id)      
    
    def __repr__(self):
        return (self.unit)   
    
class GameType(Base):
    __tablename__ = 'gametype'
    id = Column(Integer, primary_key = True)
    type = Column(String(140), index=True, unique=True)
    
    def __init__(self,type):
        self.type = type
       
    def getid(self):
        return (self.id)
    
    def __repr__(self):
        return (self.type)   
    

class Game(Base):
    __tablename__ = 'game'
    id = Column(Integer, primary_key = True)
    gametype = Column(Integer,ForeignKey('gametype.id'))
    desc = Column(String(140))
    startdate = Column(Date)
    enddate = Column(Date)
    createdby = Column(Integer,ForeignKey('users.id')) 
    
    def __init__(self,gametype,desc,startdate,enddate,createdby):
        self.gametype = gametype
        self.desc = desc
        self.startdate = startdate
        self.enddate = enddate
        self.createdby = createdby
    def getid(self):
        return(self.id)
    
    def __repr__(self):
        return '<Game %r>' % (self.desc)
    
class GameTask(Base):
    __tablename__ = 'gametask'
    id = Column(Integer, primary_key = True)
    gameid = Column(Integer, ForeignKey('game.id'))
    order = Column(Integer)
    task = Column(String(140))
    unit = Column(Integer)
    
    game = relationship("Game", back_populates="gametask")
    
    def __repr__(self):
        return '<Task %r>' % (self.task)
    
Game.gametask = relationship("GameTask",order_by=GameTask.id, back_populates="game")    

class GamePlayers(Base):
    __tablename__ = 'gameplayers'
    id = Column(Integer, primary_key = True)
    userid = Column(Integer, ForeignKey('users.id'))
    gameid = Column(Integer, ForeignKey('game.id'))
    lastname = Column(String(120))
    firstname = Column(String(120))
    email = Column(String(120))
    gender = Column(String(6))
    division = Column(String(6))
    weight1 = Column(String(10))
    weight2 = Column(String(10))
    
    game = relationship("Game", back_populates="gameplayers")
    
    def __repr__(self):
        return ('<First %r>') % (self.firstname) % (' ') % (self.lastname)

Game.gameplayers = relationship("GamePlayers",back_populates="game")

class PlayerGameTask(Base):
    __tablename__ = 'playergametask' 
    id = Column(Integer, primary_key = True)
    gameplayersid = Column(Integer, ForeignKey('gameplayers.id'))
    gameplayersuserid = Column(Integer, ForeignKey('users.id'))
    gameid = Column(Integer, ForeignKey('game.id'))
    gametaskid = Column(Integer, ForeignKey('gametask.id'))
    value1date = Column(Date)
    value1 = Column(Numeric(6,2))
    #tval1 = Column(DateTime)
    value2date = Column(Date)
    value2 = Column(Numeric(6,2))
    #tval2 = Column(DateTime)
    diff =  Column(Numeric(6,2))
    #tdiff = Column(DateTime)
    #game = relationship("Game"(
    #gameplayers = relationship("GamePlayers", back_populates="results")
    
    def __repr__(self):
        return ('<First %r>') % (self.value1) % (' ') % (self.lastname)
    
#GamePlayers.results = relationship("PlayerGameTask",backpopulates("gameplayers") 