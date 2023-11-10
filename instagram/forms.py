from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from wtforms.widgets import TextArea

from instagram.models import User


class FormLogin(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    btn = SubmitField('Entrar')


class FormCreateNewAccount(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Nome de usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    checkPassword = PasswordField('Confirmação de senha', validators=[DataRequired(), Length(6, 20), EqualTo('password')])
    btn = SubmitField('Cadastrar')

    def validate_email(self, email):
        email_of_user = User.query.filter_by(email=email.data).first()
        if email_of_user:
            return ValidationError('~ email já cadastrado ~')


class FormCreateNewPost(FlaskForm):
    text = StringField('Texto', widget=TextArea(), validators=[DataRequired()])
    photo = FileField('Imagem', validators=[DataRequired()])
    btn = SubmitField('Publicar')


class FormFollow(FlaskForm):
    btn = SubmitField('Seguir')


class FormUnfollow(FlaskForm):
    btn = SubmitField('Deixar de seguir')


class FormBlock(FlaskForm):
    btn = SubmitField('Bloquear')


class FormUnblock(FlaskForm):
    btn = SubmitField('Desbloquear')
