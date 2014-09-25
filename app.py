import os
from flask import Flask, render_template, redirect, url_for, request
from flask.ext.sqlalchemy import SQLAlchemy
from forms import NewUserForm
from flask_sslify import SSLify


app = Flask(__name__)
app.config.from_object('config')
if 'DYNO' in os.environ: # only trigger SSLify if the app is running on Heroku
    sslify = SSLify(app)

db = SQLAlchemy(app)
import models

@app.route('/')
def index():
    return redirect(url_for('runlog'))


@app.route('/runlog')
def runlog():
    entries = db.session.query(models.RunLog).order_by(models.RunLog.datetime.desc()).limit(48)
    return render_template('runlog.html', entries = entries)


@app.route('/newuser', methods=['GET', 'POST'])
def newuser():
    form = NewUserForm(request.form)
    if request.method == 'POST' and form.validate():
        user = models.User(form.boxuseremail.data, form.mitrend_user.data, "True", form.password.data)
        db.session.add(user)
        db.session.commit()
    return render_template('newuser.html', title = 'New User Information', form=form)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
