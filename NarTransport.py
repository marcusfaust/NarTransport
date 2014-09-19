__author__ = 'marcusfaust'

import os
import requests
from requests.auth import HTTPBasicAuth
from app import db
import models


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
        r = requests.post(upload_url, auth=self.auth, data=params, files=files)

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

    def __init__(self):
        self.refresh_token = models.RefreshToken.query.filter_by(id=1).first()

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
        r = requests.get(box_folders_url, headers=headers)
        results = r.json()

        return results


if __name__ == '__main__':

    box_incoming_folder_id = os.environ.get('BOX_INCOMING_FOLDER_ID')
    box_archive_folder_id = os.environ.get('BOX_ARCHIVE_FOLDER_ID')

    # Construct Box Session Object
    boxsession = BoxSession()

    #Refresh Access Token
    access_token = boxsession.getAccessToken()

    #Obtain Contents of Incoming Folder
    incoming_contents = boxsession.getFolderContents(box_incoming_folder_id, access_token)
    print "hello"

    # Construct MiTrend Session Object
    #session1 = MitrendSession()

    # Create new MiTrend Assessment
    #session1.new_assessment("test1234")

    # Upload zipped NAR file to MiTrend
    #session1.upload_file("/tmp/nar.zip", "VNX")

    # Submit MiTrend Assessment
    #session1.submit()
