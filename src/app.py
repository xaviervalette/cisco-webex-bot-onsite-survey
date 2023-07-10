from flask import Flask, request, abort
import yaml
import json
from functions import *
import datetime

"""
VARIABLE ASSIGNEMENT
"""
# Open the config.yml file and load its contents into the 'config' variable
with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)

# Webex card
with open('ressources/surveyCard.json', 'r') as json_file:
    surveyCard = json.load(json_file)
with open('ressources/resultCard.json', 'r') as json_file:
    resultCard = json.load(json_file)

"""
HANDLE WEBHOOKS
"""
deleteAllWebhooks(config["botToken"])
sendCardWebhookUrl = config["baseWebhookUrl"]+config["sendCardWebhookPath"]
getCardSubmissionUrl = config["baseWebhookUrl"]+config["getCardSubmissionPath"]
getDetailUrl = config["baseWebhookUrl"]+"details"

response = createWebhook("sendCard", sendCardWebhookUrl, "messages", "", config["botToken"])
response = createWebhook("getDetail", getDetailUrl, "attachmentActions", "", config["botToken"])
status_code = 0
while status_code != 200:
    response, status_code = createWebhook("getCardSubmission", getCardSubmissionUrl, "attachmentActions", "", config["botToken"])

initaliseDB(config["botToken"])

print("\nWebhooks creation output: "+str(status_code)+"\n")

app = Flask(__name__)

"""
LISTENING ON /webhook/getcardsubmission RESSOURCE FOR HTTP POST (WEBHOOKS)
"""
@app.route(config["getCardSubmissionPath"], methods=['POST'])
def webhookGet():

    if request.method == 'POST':

        #GET INPUTS FROM WEBEX
        my_date = datetime.date.today()
        _, weekNum, _ = my_date.isocalendar()
        data = request.json
        attachement = getAttachement(config["botToken"], data["data"]["id"])
        
        # READ DATABASE
        with open('data/answers.json', 'r') as openfile:
            previousWeeksAllRooms = json.load(openfile)
        
        previousWeeks = previousWeeksAllRooms[data["data"]["roomId"]]["roomResults"]
        # REMOVE USERNAME FROM WEEK
        username = getUsernameFromUserid(config["botToken"], attachement["personId"])
        for day in previousWeeks[weekNum-1]["days"]:
            newLine = [s for s in previousWeeks[weekNum-1]["days"][day] if s != username]
            previousWeeks[weekNum-1]["days"][day] = newLine
        
        # ADD USERNAME IN WEEK
        for day in attachement["inputs"]:
            if attachement["inputs"][day] == "true":
                previousWeeks[weekNum-1]["days"][day].append(username)
        
        previousWeeksAllRooms[data["data"]["roomId"]]["roomResults"]=previousWeeks

        # UPDATE DATABASE
        with open("data/answers.json", "w") as outfile:
            json.dump(previousWeeksAllRooms, outfile, indent=4)

        # SEND RESULT BACK TO USER
        listDays = []
        listDays = getListDays()
        populateResultCard(resultCard, previousWeeks, weekNum, getRoomSize(config["botToken"], data["data"]["roomId"]), listDays)
        sendCardToPersonId(config["botToken"], data["data"]["personId"], resultCard)

        return 'success', 200

    # ELSE RETURN A HTTP 400 STATUS CODE
    else:
        abort(400)

"""
LISTENING ON LOCALHOST:42101 FOR HTTP POST (WEBHOOKS)
"""
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=42101)
