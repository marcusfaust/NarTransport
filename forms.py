__author__ = 'marcusfaust'

from wtforms import Form, TextField, PasswordField
from wtforms.validators import Required, Email, EqualTo
from models import db, User


class Unique(object):
    """ validator that checks field uniqueness """
    def __init__(self, model, field, message=None):
        self.model = model
        self.field = field
        if not message:
            message = u'this element already exists'
        self.message = message

    def __call__(self, form, field):
        check = self.model.query.filter(self.field == field.data).first()
        if check:
            raise ValidationError(self.message)


class NewUserForm(Form):
    boxuseremail = TextField('Box Account Email', [Required(), Email(message='Invalid Email Address'), Unique(User, 'boxuser', message='Box Email already registered!')])
    mitrend_user = TextField('MiTrend User Email', [Required(), Email(message='Invalid Email Address')])
    password = PasswordField('MiTrend Password', [Required(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password', [Required()])
