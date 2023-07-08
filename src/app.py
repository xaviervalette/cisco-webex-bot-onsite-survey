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
response, status_code = createWebhook("getCardSubmission", getCardSubmissionUrl, "attachmentActions", "", config["botToken"])

#sendCardToRoomId(config["botToken"], config["destinationRoomId"], surveyCard)
#sendCardToRoomId(config["botToken"], config["destinationRoomId"], resultCard)
sendCardToPersonId(config["botToken"], "Y2lzY29zcGFyazovL3VzL1BFT1BMRS82YThjZmMxNy0yYjU1LTRmN2YtYWY5Ny1mYWM1M2I0ZjFlZjU", resultCard)

initaliseDB()

print("\nWebhooks creation output: "+str(status_code)+"\n")

app = Flask(__name__)

"""
LISTENING ON /webhook/sendCard RESSOURCE FOR HTTP POST (WEBHOOKS)
"""
@app.route(config["sendCardWebhookPath"], methods=['POST'])
def webhookSend():

    # IF THE REQUEST IF POST THEN SEND THE MESSAGE
    if request.method == 'POST':
        #GET END USER INPUTS FROM WEBEX
        data = request.json
        print(data)
        print(f"Webex IM received from {data['data']['personEmail']}")
        return 'success', 200

    # ELSE RETURN A HTTP 400 STATUS CODE
    else:
        abort(400)


"""
LISTENING ON /webhook/getcardsubmission RESSOURCE FOR HTTP POST (WEBHOOKS)
"""
@app.route(config["getCardSubmissionPath"], methods=['POST'])
def webhookGet():

    if request.method == 'POST':

        #GET END USER INPUTS FROM WEBEX
        my_date = datetime.date.today()
        _, weekNum, _ = my_date.isocalendar()  # Using isocalendar() function
        data = request.json
        attachement = getAttachement(config["botToken"], data["data"]["id"])
        
        # Opening JSON file
        with open('data/answers.json', 'r') as openfile:
            previousWeeks = json.load(openfile)
        username = getUsernameFromUserid(config["botToken"], attachement["personId"])
        team = {"username":username, "isAtUlteam":attachement["inputs"]}
        i=0
        #Check if team member already submitted
        teamMemberAlreadySubmitThisWeek = False
        for teamMember in previousWeeks[weekNum-1]["team"]:
            if username == teamMember["username"]:
                teamMemberAlreadySubmitThisWeek=True
            else:
                i=i+1
        
        print(teamMemberAlreadySubmitThisWeek)
        if teamMemberAlreadySubmitThisWeek == True:
            previousWeeks[weekNum-1]["team"][i] = team
        else:
            previousWeeks[weekNum-1]["team"].append(team)

        with open("data/answers.json", "w") as outfile:
            json.dump(previousWeeks, outfile, indent=4)

        return 'success', 200

    # ELSE RETURN A HTTP 400 STATUS CODE
    else:
        abort(400)

@app.route("/sendSurvey", methods=['POST'])
def sendSurvey():
    if request.method == "POST":
        populateResultCard(resultCard)
        sendCardToRoomId(config["botToken"], config["destinationRoomId"], resultCard)

"""
LISTENING ON LOCALHOST:42101 FOR HTTP POST (WEBHOOKS)
"""
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=42101)
