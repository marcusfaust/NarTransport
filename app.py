import os
from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
import models

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/runlog')
def runlog():
    entries = models.RunLog.query.all()
    return render_template('runlog.html', entries = entries)



if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
