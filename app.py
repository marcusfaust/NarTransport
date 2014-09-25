import os
import requests
from flask import Flask, render_template, redirect, url_for, request
from forms import NewUserForm
from flask_sslify import SSLify
from models import db, RefreshToken, RunLog, User
import json



app = Flask(__name__)
app.config.from_object('config')
if 'DYNO' in os.environ: # only trigger SSLify if the app is running on Heroku
    sslify = SSLify(app)

db.app = app
db.init_app(app)

from NarTransport import BoxSession

class BoxSession:

    box_api_baseurl = "https://api.box.com/2.0"
    box_token_baseurl = "https://app.box.com/api/oauth2/token"
    box_client_id = os.environ.get('BOX_CLIENT_ID')
    box_client_secret = os.environ.get('BOX_CLIENT_SECRET')
    box_root = os.environ.get('BOX_ROOT')

    def __init__(self):
        self.refresh_token = RefreshToken.query.filter_by(id=1).first()

    def initUser(self, boxemail):

        box_folders_url = self.box_api_baseurl + "/folders"
        box_collab_url = self.box_api_baseurl + "/collaborations"

        #Create User Root Folder
        params = {"name": boxemail, "parent": {"id": self.box_root}}
        headers = {"Authorization": "Bearer " + self.getAccessToken()}
        r = requests.post(box_folders_url, data=json.dumps(params), headers=headers)
        results = r.json()
        user_root = str(results['id'])

        #Create NarTransport-Incoming Folder
        params = {"name": "NarTransport-Incoming", "parent": {"id": user_root}}
        headers = {"Authorization": "Bearer " + self.getAccessToken()}
        r = requests.post(box_folders_url, data=json.dumps(params), headers=headers)
        results = r.json()
        user_incoming = str(results['id'])

        #Add Collaboration
        params = {"item": {"id": user_incoming, "type": 'folder'}, "accessible_by": {"type": 'user', "login": boxemail}, "role": 'editor'}
        headers = {"Authorization": "Bearer " + self.getAccessToken()}
        r = requests.post(box_collab_url, data=json.dumps(params), headers=headers)
        results = r.json()


        #Store Incoming Id
        User.query.filter_by(boxuser=boxemail).update(dict(incoming_folder_id=user_incoming))
        db.session.commit()

        #Create NarTransport-Archive Folder
        params = {"name": "NarTransport-Archive", "parent": {"id": user_root}}
        headers = {"Authorization": "Bearer " + self.getAccessToken()}
        r = requests.post(box_folders_url, data=json.dumps(params), headers=headers)
        results = r.json()
        user_archive = str(results['id'])

        #Add Collaboration
        params = {"item": {"id": user_archive, "type": 'folder'}, "accessible_by": {"type": 'user', "login": boxemail}, "role": 'editor'}
        headers = {"Authorization": "Bearer " + self.getAccessToken()}
        r = requests.post(box_collab_url, data=json.dumps(params), headers=headers)
        results = r.json()

        #Store Archive Id
        User.query.filter_by(boxuser=boxemail).update(dict(archive_folder_id=user_archive))
        db.session.commit()




    def getAccessToken(self):

        params = {"grant_type": "refresh_token", \
                  "client_id": self.box_client_id, \
                  "client_secret": self.box_client_secret, \
                  "refresh_token": str(self.refresh_token.token)}

        r = requests.post(self.box_token_baseurl, data=params)
        results = r.json()
        rtoken = results['refresh_token']
        self.refresh_token.token = rtoken
        atoken = results['access_token']

        # Store refresh_token
        RefreshToken.query.filter_by(id=1).update(dict(token=rtoken))
        db.session.commit()

        return atoken

    def getFolderContents(self, folderID, atoken):

        box_folders_url = self.box_api_baseurl + "/folders/" + folderID + "/items"
        headers = {"Authorization": "Bearer " + atoken}
        params = {"fields": "name"}
        r = requests.get(box_folders_url, params=params, headers=headers)
        results = r.json()

        return results

    def getFoldersFromContents(self, contents):

        folders = []
        for x in contents['entries']:
            if x['type'] == 'folder':
                folders.append(x)

        return folders

    def getFilesFromContents(self, contents):

        files = []
        for x in contents['entries']:
            if x['type'] == 'file':
                files.append(x)

        return files

    def renameFolder(self, folderID, newName, atoken):

        box_folder_url = self.box_api_baseurl + "/folders/" + folderID
        headers = {"Authorization": "Bearer " + atoken}
        params = {"name": newName}
        r = requests.put(box_folder_url, data=json.dumps(params), headers=headers)
        return r.json()

    def moveFolder(self, folderID, parentID, atoken):

        box_folder_url = self.box_api_baseurl + "/folders/" + folderID
        headers = {"Authorization": "Bearer " + atoken}
        params = {"parent": {"id": parentID}}
        r = requests.put(box_folder_url, data=json.dumps(params), headers=headers)
        results = r.json()

        return r.json()

    def getZipFilesInFolder(self, folderID):
        pass

    def downloadFile(self, fileNAME, fileID, atoken):

        box_file_url = self.box_api_baseurl + "/files/" + fileID + "/content"
        headers = {"Authorization": "Bearer " + atoken}

        print "Begin Download of " + fileNAME
        with open(fileNAME, 'wb') as file:
            r = requests.get(box_file_url, headers=headers, stream=True, timeout=3600)
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
                    file.flush()

        print "Download Complete of " + fileNAME

app_boxsession = BoxSession()
print "hello"

@app.route('/')
def index():
    return redirect(url_for('runlog'))


@app.route('/runlog')
def runlog():
    entries = db.session.query(RunLog).order_by(RunLog.datetime.desc()).limit(48)
    return render_template('runlog.html', entries = entries)


@app.route('/newuser', methods=['GET', 'POST'])
def newuser():
    form = NewUserForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(form.boxuseremail.data, form.mitrend_user.data, "True", form.password.data)
        db.session.add(user)
        db.session.commit()
        app_boxsession.initUser(form.boxuseremail.data)

    return render_template('newuser.html', title = 'New User Information', form=form)








if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
