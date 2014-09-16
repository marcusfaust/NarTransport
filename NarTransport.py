__author__ = 'marcusfaust'

import os
import requests
from requests.auth import HTTPBasicAuth


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


if __name__ == '__main__':

    # Construct MiTrend Session Object
    session1 = MitrendSession()

    # Create new MiTrend Assessment
    session1.new_assessment("test1234")

    # Upload zipped NAR file to MiTrend
    session1.upload_file("/tmp/nar.zip", "VNX")

    # Submit MiTrend Assessment
    session1.submit()

    print "hello"