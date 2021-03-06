__author__ = 'marcusfaust'

from wtforms import Form, TextField, PasswordField
from wtforms.validators import Required, Email, EqualTo


class NewUserForm(Form):
    boxuseremail = TextField('Box Account Email', [Required(), Email(message='Invalid Email Address')])
    mitrend_user = TextField('MiTrend User Email', [Required(), Email(message='Invalid Email Address')])
    password = PasswordField('MiTrend Password', [Required(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password', [Required()])

