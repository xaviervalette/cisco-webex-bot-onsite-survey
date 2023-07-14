import json
import requests
import locale
from datetime import date, datetime, timedelta

baseUrl = "https://webexapis.com/v1/"

# Get week number
def getWeekNum():
    my_date = date.today()
    _, weekNum, _ = my_date.isocalendar()
    return weekNum

# Broadcast survey card to all rooms
def broadcastSurveyCard(token, surveyCard):
    listDays = []
    listDays = getListDays()
    with open('data/answers.json', 'r') as openfile:
        previousWeeks = json.load(openfile)
    updateDB(token, previousWeeks)
    populateSurveyCard(surveyCard, listDays)
    for roomId, _ in previousWeeks.items():
        sendCardToRoomId(token,roomId,surveyCard)

# Broadcast result card to all rooms
def broadcastResultCard(token, resultCard):
    listDays = []
    listDays = getListDays()

    my_date = date.today()
    _, weekNum, _ = my_date.isocalendar()

    with open('data/answers.json', 'r') as openfile:
        previousWeeks = json.load(openfile)
    updateDB(token, previousWeeks)
    for roomId, _ in previousWeeks.items():
        resultCardEdited = populateResultCard(resultCard, previousWeeks[roomId]["roomResults"], weekNum, getRoomSize(token, roomId), listDays)
        sendCardToRoomId(token,roomId,resultCardEdited)

# Get the size of a room (number of members)
def getRoomSize(token, roomId):
    url = f'https://webexapis.com/v1/memberships?roomId={roomId}'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data={})
    output = response.json()

    return len(output["items"])-1

# Get the list of room IDs where the bot is a member
def getRoomsIdBot(token):
    url = f'https://webexapis.com/v1/rooms?type=group'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data={})
    output = response.json()

    roomsId = []
    for room in output["items"]:
        roomsId.append(room["id"])

    return roomsId

# Get the list of room IDs where the bot is a member
def getRoomName(token, roomId):
    url = f'https://webexapis.com/v1/rooms/{roomId}'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data={})
    output = response.json()

    roomName = output["title"]
    return roomName

# Populate the result card with data
def populateResultCard(resultCard, database, weekNumber, roomSize, listDays):
    resultCardEdited = resultCard
    i=0
    for day in resultCardEdited["content"]["body"][1]["items"]:

        # PROGRESS BAR                      
        day["columns"][0]["items"][1]["columns"][0]["width"] = int(100*len(database[weekNumber-1]["days"][day["columns"][0]["items"][0]["id"]])/roomSize)
        day["columns"][0]["items"][1]["columns"][1]["width"] = int(100-day["columns"][0]["items"][1]["columns"][0]["width"])
        day["columns"][0]["items"][0]["text"] = listDays[i]
        
        # HANDLE EXCEPTION
        if (day["columns"][0]["items"][1]["columns"][0]["width"]==0):
            day["columns"][0]["items"][1]["columns"][0]["width"]=1
            day["columns"][0]["items"][1]["columns"][1]["width"]=99
        elif (day["columns"][0]["items"][1]["columns"][1]["width"]==1):
            day["columns"][0]["items"][1]["columns"][0]["width"]=99
            day["columns"][0]["items"][1]["columns"][0]["width"]=1
        i=i+1

    # NAMES
    i=0
    for day in resultCardEdited["content"]["body"][2]["actions"][0]["card"]["body"][0]["items"]:
        day["items"][1]["text"]=', '.join(database[weekNumber-1]["days"][day["items"][0]["text"].lower()])  
        #day["items"][0]["text"]=listDays[i]
        i=i+1  

    return resultCardEdited

# Get the list of days in French
def getListDays():
    listDays = []
    # Get the current date
    current_date = datetime.now().date()

    # Find the next Monday
    days_ahead = (0 - current_date.weekday()) % 7
    next_monday = current_date + timedelta(days=days_ahead)

    # Define a list of weekdays
    weekdays = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi']

    # Iterate over the next seven days starting from next Monday
    for i in range(5):
        # Calculate the date for the current day
        next_date = next_monday + timedelta(days=i)
        
        # Get the weekday index (0-6) for the current day
        weekday_index = next_date.weekday()
        
        # Get the weekday name from the weekdays list
        weekday_name = weekdays[weekday_index]
        
        # Format the date as "weekday day/month"
        formatted_date = next_date.strftime(f"{weekday_name} %d/%m")
        
        # Print the formatted date

        listDays.append(formatted_date)

    return listDays

# Populate the survey card with data
def populateSurveyCard(surveyCard, listDays):
    surveyCardEdited = surveyCard
    i=0
    for day in surveyCardEdited["content"]["body"][1]["items"]:
        # NAMES
        day["title"]=listDays[i]
        i=i+1

    return surveyCardEdited

# Initialize the database
def initaliseDB(token):
    roomsId = getRoomsIdBot(token)
    rooms = {}
    roomsResultsPerWeek = []
    for week in range(1, 54):
        roomsResultsPerWeek.append({"week":week, "days":{"lundi":[], "mardi":[], "mercredi":[], "jeudi":[], "vendredi":[]}})
    for roomId in roomsId:
        #rooms.append({"roomId":roomId, "roomResults":roomsResultsPerWeek})
        rooms[roomId]={"roomResults":roomsResultsPerWeek}
    with open("data/answers.json", "w") as outfile:
        json.dump(rooms, outfile, indent=4)
    return rooms

# Update the database
def updateDB(token, previousWeeks):
    roomsId = getRoomsIdBot(token)
    rooms = {}
    currentRoomsId = []
    for roomId, _ in previousWeeks.items() :
        currentRoomsId.append(roomId)
    roomsResultsPerWeek = []
    for week in range(1, 54):
        roomsResultsPerWeek.append({"week":week, "days":{"lundi":[], "mardi":[], "mercredi":[], "jeudi":[], "vendredi":[]}})
    
    for roomId in roomsId:
        if str(roomId) in currentRoomsId:
            rooms[roomId]=previousWeeks[roomId]
        else:
            rooms[roomId]={"roomResults":roomsResultsPerWeek}

    with open("data/answers.json", "w") as outfile:
        json.dump(rooms, outfile, indent=4)

# Get the username from a user ID
def getUsernameFromUserid(token, userId):
    url = f'https://webexapis.com/v1/people/{userId}'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data={})
    output = response.json()
    return output["displayName"]

# Send a message to a room ID
def sendMessageToRoomId(token, roomId, message):
    url = f"{baseUrl}/messages"

    payload = json.dumps({
        "roomId": roomId,
        "text": message
    })

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()

# Send a message to a person ID
def sendMessageToPersonId(token, personId, message):

    url = f"{baseUrl}/messages"

    payload = json.dumps({
        "toPersonId": personId,
        "text": message
    })

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()

# Send a card to a person ID
def sendCardToPersonId(token, personId, card):
    url = f"{baseUrl}/messages"

    payload = json.dumps({
        "toPersonId": personId,
        "markdown": "[Tell us about yourself](https://www.example.com/form/book-vacation). We just need a few more details to get you booked for the trip of a lifetime!",
        "attachments": card
    })

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()

# Send a card to a room ID
def sendCardToRoomId(token, roomId, card):
    url = f"{baseUrl}/messages"

    payload = json.dumps(
        {
            "roomId": roomId,
            "markdown": "[Tell us about yourself](https://www.example.com/form/book-vacation). We just need a few more details to get you booked for the trip of a lifetime!",
            "attachments": card
        })

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()

# Create a webhook
def createWebhook(name, targetUrl, ressource, filter, token):
    url = f"{baseUrl}/webhooks"

    payload = json.dumps({
        "name": name,
        "targetUrl": targetUrl,
        "resource": ressource,
        "event": "created"
    })

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json(), response.status_code

# List webhooks
def listWebhook(token):
    url = f"{baseUrl}/webhooks"

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.request("GET", url, headers=headers)
    return response.json()

# Delete a webhook
def deleteWebhook(token, webhookId):
    url = f"{baseUrl}/webhooks/{webhookId}"

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.request("DELETE", url, headers=headers)

# Get an attachment
def getAttachement(token, attachementId):
    url = f"{baseUrl}/attachment/actions/{attachementId}"

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.request("GET", url, headers=headers)
    return response.json()

# Delete all webhooks
def deleteAllWebhooks(token):
    response = listWebhook(token)
    for webhook in response["items"]:
        webhookId = webhook["id"]
        deleteWebhook(token, webhookId)    