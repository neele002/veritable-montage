
from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed
from wtforms import validators
from wtforms.fields import StringField, BooleanField,SubmitField,FormField,SelectField,TextField,TextAreaField,FieldList,HiddenField,PasswordField
from wtforms.fields.html5 import DateField
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea    
from zmodels import GameType,TaskUnit


def enabled_units(): 
    return TaskUnit.query.all()

def enabled_categories():
    return GameType.query.all()

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me', default=False)
    sub = SubmitField('Submit')
    
class SignUpForm(FlaskForm):
    openid = StringField('User ID', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    sub = SubmitField('Submit')
    
class ResetForm(FlaskForm):
    openid = StringField('User ID', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    sub = SubmitField('Submit')    
    
class AddGameTypeForm(FlaskForm):
    gametype = StringField('Game Type', validators=[DataRequired()])

    
class AddGameForm(FlaskForm):
    stuff = HiddenField(default='[]')
    puff = HiddenField(default='[]')
    desc = TextField('Name',[validators.Length(min=4, max=80)])
    gametype = QuerySelectField('Game Type',query_factory=enabled_categories, allow_blank=False)
    startdate = StringField('Start Date',id='xt', validators=[DataRequired()])
    enddate = StringField('End Date',id='xt1',validators=[DataRequired()])
    task = StringField('Task')
    unit = QuerySelectField('Unit',query_factory=enabled_units, allow_blank=False)
    button = SubmitField('Add',id="addtask")
    firstname = StringField('First Name')
    lastname = StringField('Last Name')
    email = StringField('Email')
    button1 = SubmitField('Add',id='addplayer')
    upload = FileField('csv', validators=[
        FileAllowed(['csv'], 'CSV File only!')
    ])
    sub = SubmitField('Submit')
    
class EditGameForm(FlaskForm):
    stuff = HiddenField(default='[]')
    puff = HiddenField(default='[]')
    gameid = HiddenField(default=0)
    desc = TextField('Name',[validators.Length(min=4, max=80)])
    gametype = QuerySelectField('Game Type',query_factory=enabled_categories, allow_blank=False)
    startdate = StringField('Start Date',id='xt', validators=[DataRequired()])
    enddate = StringField('End Date',id='xt1',validators=[DataRequired()])
    task = StringField('Task')
    unit = QuerySelectField('Unit',query_factory=enabled_units, allow_blank=False)
    button = SubmitField('Add',id="addtask")
    firstname = StringField('First Name')
    lastname = StringField('Last Name')
    email = StringField('Email')
    button1 = SubmitField('Add',id='addplayer')
    upload = FileField('csv', validators=[
        FileAllowed(['csv'], 'CSV File only!')
    ])
    sub = SubmitField('Submit')    
class GameClickForm(FlaskForm):
    game = HiddenField(default=0)
    edit = HiddenField(default='False')
    alter = HiddenField(default='False')
    
class MyBaseForm(FlaskForm):
    game = HiddenField()
    tasks = HiddenField()
    player = HiddenField()
    gametype = HiddenField()
    