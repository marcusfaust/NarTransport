__author__ = 'marcusfaust'

import os
import requests
import json
import time
from datetime import datetime
from requests.auth import HTTPBasicAuth
from models import db, RefreshToken, RunLog, User



class MitrendSession:

    def __init__(self):
        self.baseurl = "https://beta.mitrend.com/api/assessments"
        self.assessment_id = ""
        self.upload_url = self.baseurl + "/" + self.assessment_id + "/files"
        self.submit_url = self.baseurl + "/" + self.assessment_id + "/submit"
        self.auth = HTTPBasicAuth(os.environ.get("MITREND_USER"), os.environ.get("MITREND_PASS"))

        pass

    def new_assessment(self, assessment_name):
        params = {"assessment_name": assessment_name}
        r = requests.post(self.baseurl, auth=self.auth, data=params)
        results = r.json()
        self.assessment_id = results["id"]

    def upload_file(self, filepath, device_type):
        upload_url = self.upload_url = self.baseurl + "/" + str(self.assessment_id) + "/files"
        fileobj = open(filepath, 'rb')
        params = {"device_name": device_type, "file": "nar.zip"}
        files = {"file": fileobj}

        print "Mitrend Upload of " + filepath + " Started."

        r = requests.post(upload_url, auth=self.auth, data=params, files=files)

        print "Mitrend Upload of " + filepath + " Complete."
        return r.text

    def submit(self):
        submit_url = self.submit_url = self.baseurl + "/" + str(self.assessment_id) + "/submit"
        r = requests.post(submit_url, auth=self.auth)

        return r.text


class BoxSession:

    box_api_baseurl = "https://api.box.com/2.0/"
    box_token_baseurl = "https://app.box.com/api/oauth2/token"
    box_client_id = os.environ.get('BOX_CLIENT_ID')
    box_client_secret = os.environ.get('BOX_CLIENT_SECRET')
    box_root = os.environ.get('BOX_ROOT')

    def __init__(self):
        self.refresh_token = RefreshToken.query.filter_by(id=1).first()

    def initUser(self, boxemail):

        #Create User Root Folder
        box_folders_url = self.box_api_baseurl + "/folders"
        params = {"name": boxemail, "parent": {"id", self.box_root}}
        headers = {"Authorization": "Bearer " + self.getAccessToken()}
        r = requests.get(box_folders_url, params=params, headers=headers)
        results = r.json()
        user_root = results['id']

        #Create NarTransport-Incoming Folder
        params = {"name": "NarTransport-Incoming", "parent": {"id", user_root}}
        headers = {"Authorization": "Bearer " + self.getAccessToken()}
        r = requests.get(box_folders_url, params=params, headers=headers)
        results = r.json()
        user_incoming = results['id']

        #Store Incoming Id
        models.User.query.filter_by(boxuser=boxemail).update(dict(incoming_folder_id=user_incoming))
        db.session.commit()

        #Create NarTransport-Archive Folder
        params = {"name": "NarTransport-Archive", "parent": {"id", user_root}}
        headers = {"Authorization": "Bearer " + self.getAccessToken()}
        r = requests.get(box_folders_url, params=params, headers=headers)
        results = r.json()
        user_archive = results['id']

        #Store Archive Id
        models.User.query.filter_by(boxuser=boxemail).update(dict(archive_folder_id=user_archive))
        db.session.commit()




    def getAccessToken(self):

        params = {"grant_type": "refresh_token", \
                  "client_id": self.box_client_id, \
                  "client_secret": self.box_client_secret, \
                  "refresh_token": str(self.refresh_token.token)}

        r = requests.post(self.box_token_baseurl, data=params)
        results = r.json()
        rtoken = results['refresh_token']
        atoken = results['access_token']

        # Store refresh_token
        models.RefreshToken.query.filter_by(id=1).update(dict(token=rtoken))
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


if __name__ == '__main__':

    start = time.time()
    start_datetime = datetime.now()
    nars_found = False
    box_incoming_folder_id = os.environ.get('BOX_INCOMING_FOLDER_ID')
    box_archive_folder_id = os.environ.get('BOX_ARCHIVE_FOLDER_ID')
    incoming_contents = {}
    incoming_folders = []

    # Construct Box Session Object
    boxsession = BoxSession()

    # Construct MiTrend Session Object
    mitrendsession = MitrendSession()

    #Refresh Access Token
    access_token = boxsession.getAccessToken()

    #Obtain Contents of Incoming Folder and Extract Out Folders
    incoming_contents = boxsession.getFolderContents(box_incoming_folder_id, access_token)
    incoming_folders = boxsession.getFoldersFromContents(incoming_contents)

    #For Every ZIP File in Subfolders, Download ZIP and Create Assessment
    if incoming_folders:
        for folder in incoming_folders:

            folder_contents = boxsession.getFolderContents(folder['id'], access_token)
            folder_files = boxsession.getFilesFromContents(folder_contents)

            #Download each file - hopefully zip file
            if folder_files:
                for zfile in folder_files:

                    #Grab file from Box.net
                    boxsession.downloadFile(zfile['name'], zfile['id'], access_token)

                    #Attempt to create a Mitrends Assessment
                    mitrendsession.new_assessment(folder['name'])

                    #Upload downloaded file
                    mitrendsession.upload_file(zfile['name'], "VNX")

                    #Submit Mitrend Assessment
                    mitrendsession.submit()

                    #Delete file locally
                    os.remove(zfile['name'])
                    if not nars_found:
                        nars_found = True

                #Append Datetime to Folder Name
                #folderWithDate = folder['name'] + "_" + datetime.now().isoformat()
                boxsession.renameFolder(folder['id'], (folder['name'] + "_" + datetime.now().isoformat()), access_token)

                #Move Folder to Archive Folder
                boxsession.moveFolder(folder['id'], box_archive_folder_id, access_token)
            else:
                print "Folder is empty"
    else:
        print "No New Folders"

    duration = time.time() - start

    #Add Entry in RunLog
    entry = models.RunLog(start_datetime, nars_found, duration)
    db.session.add(entry)
    db.session.commit()