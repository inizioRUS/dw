from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileRequired, FileAllowed, DataRequired
from wtforms import TextAreaField, PasswordField, SubmitField, BooleanField, RadioField, FileField, \
    SelectField, TextAreaField, EmailField, StringField, FieldList, FormField

list_of_type = ['jpg', 'png', 'jpeg']


class RegisterForm(FlaskForm):
    Email = EmailField('Email', validators=[DataRequired()])
    Password = PasswordField('Password', validators=[DataRequired()])
    Password_again = PasswordField('Repeat password', validators=[DataRequired()])
    Surname = StringField('Surname', validators=[DataRequired()])
    Login = StringField('Login', validators=[DataRequired()])
    Name = StringField('Name', validators=[DataRequired()])
    photo = FileField(validators=[FileAllowed(list_of_type), DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField('Sumbit')


class Edit_form(FlaskForm):
    Surname = StringField('Surname')
    Login = StringField('Login')
    Name = StringField('Name',)
    photo = FileField(validators=[FileAllowed(list_of_type)])
    submit = SubmitField('Sumbit')


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign in')


class one_studiesFrom(FlaskForm):
    photo = FileField(validators=[FileAllowed(list_of_type)])
    text = TextAreaField("Text")


class Make_new_stadiesForm(FlaskForm):
    Number = TextAreaField('Number', validators=[DataRequired()], default=1)
    submit = SubmitField('Submit')


class Add_Commentform(FlaskForm):
    text = TextAreaField("Text")
    recaptcha = RecaptchaField()
    submit = SubmitField('Sumbit')
