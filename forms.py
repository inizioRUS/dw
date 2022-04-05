from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileRequired, FileAllowed, DataRequired
from wtforms import TextAreaField, PasswordField, SubmitField, BooleanField, RadioField, FileField, \
    SelectField, TextAreaField, EmailField, StringField, FieldList, FormField

list_of_type = ['jpg', 'png', 'jpeg', 'gif']


class RegisterForm(FlaskForm):
    Email = EmailField('Email', validators=[DataRequired()])
    Password = PasswordField('Password', validators=[DataRequired()])
    Password_again = PasswordField('Repeat password', validators=[DataRequired()])
    Surname = StringField('Surname', validators=[DataRequired()])
    Login = StringField('Login', validators=[DataRequired()])
    Name = StringField('Name', validators=[DataRequired()])
    photo = FileField(validators=[FileAllowed(list_of_type)])
    recaptcha = RecaptchaField()
    submit = SubmitField('Sumbit')


class Edit_form(FlaskForm):
    Surname = StringField('Surname')
    Login = StringField('Login')
    Name = StringField('Name', )
    photo = FileField(validators=[FileAllowed(list_of_type)])
    submit = SubmitField('Sumbit')


class LoginForm(FlaskForm):
    login = StringField('Email', validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign in')


class Add_Commentform(FlaskForm):
    text = TextAreaField("Text", validators=[DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField('Sumbit')
