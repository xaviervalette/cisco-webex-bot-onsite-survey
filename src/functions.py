import json
import requests

baseUrl = "https://webexapis.com/v1/"

def populateResultCard(resultCard, database, weekNumber):
    resultCardEdited = resultCard
    for day in resultCardEdited["content"]["body"][1]["items"]:
        day["columns"][1]["items"][0]["text"] = ', '.join(database[weekNumber-1]["days"][day["columns"][0]["items"][0]["id"]])
        day["columns"][0]["items"][1]["width"] = str(int(1+100*len(database[weekNumber-1]["days"][day["columns"][0]["items"][0]["id"]])/10))+"px"
    return resultCardEdited

def initaliseDB():
    weeks = []
    for week in range(1, 54):
        weeks.append({"week":week, "days":{"lundi":[], "mardi":[], "mercredi":[], "jeudi":[], "vendredi":[]}})
    with open("data/answers.json", "w") as outfile:
        json.dump(weeks, outfile, indent=4)
    return weeks

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

# SEND WEBEX IM MESSAGE 

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



# SEND WEBEX CARD

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



# CREATE WEBHOOK
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



# LIST WEBHOOK
def listWebhook(token):
    url = f"{baseUrl}/webhooks"

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.request("GET", url, headers=headers)
    return response.json()



# DELETE WEBHOOK
def deleteWebhook(token, webhookId):
    url = f"{baseUrl}/webhooks/{webhookId}"

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.request("DELETE", url, headers=headers)



# GET ATTACHEMENT
def getAttachement(token, attachementId):
    url = f"{baseUrl}/attachment/actions/{attachementId}"

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.request("GET", url, headers=headers)
    return response.json()



# DELETE ALL WEBHOOKS
def deleteAllWebhooks(token):
    response = listWebhook(token)
    for webhook in response["items"]:
        webhookId = webhook["id"]
        deleteWebhook(token, webhookId)




# CHECK IF THE ORDER WAS SHIPPED TO CUSTOMER DIRECTLY 
def shippedToCustomer(order):
    output = {}
    # Check if shipped to customer or not based on the party name 
    if (order.party == order.shiptoparty):
        return output
    else:
        output["orderWebId"] = order.orderID
        output["salesOrderNum"] = order.salesordernum
        output["orderName"] = order.orderName
        output["detectionCriterias"] = []
        # If the shipment was not shipped directly to customer, investigate more
        # Check if the end customer and the partner locations are within the same country   
        if (order.partyCountry == order.shiptopartyCountry):
            
            # Check if the end customer and the partner locations are within the same city   
            if (order.partyCity == order.shiptopartyCity ):
                #Same country and city
                output["detectionCriterias"].append({"name": "Incorrect Destination", "description": "Order not directly shipped to customer", 
                "details": {"customerName": order.party , "customerAddress": order.partyCountry + ", " + order.partyCity , 
                "shippedTo": order.shiptoparty, "address": order.shiptopartyCountry + ", " + order.shiptopartyCity}})
            else:
                #Same country but different city
                output["detectionCriterias"].append({"name": "Incorrect Destination", "description": "Order not directly shipped to customer", 
                "details": {"customerName": order.party , "customerAddress": order.partyCountry + ", " + order.partyCity , 
                "shippedTo": order.shiptoparty, "address": order.shiptopartyCountry + ", " + order.shiptopartyCity}})

        else:
            #Different country
            output["detectionCriterias"].append({"name": "Incorrect Destination", "description": "Order not directly shipped to customer", 
            "details": {"customerName": order.party , "customerAddress": order.partyCountry, 
            "shippedTo": order.shiptoparty, "address": order.shiptopartyCountry}})
            
        return output



def getCustomerCountryCode(order):
    countryCode =""
    # A list of the countries and their codes (Can add more later)
    countryList = countriesList()

    # Check the customer country and get its suffix 
    for country in countryList:
        if (order.partyCountry.lower() == country["country"]):
            countryCode = country["code"]
            return countryCode


def checkItems(order, output):
    incorrectItems = []
    countryCodes = ["NA", "UK","EU","BR","AR","AU","CN","IN","JP","KR","TW"]
    itemsWithCountryCode = []
    customerCountryCode = getCustomerCountryCode(order)

    # Check for items that include a country suffix at the end of their SKU
    for item in order.orderItems:
        for code in countryCodes:
            if (item["sku"][-2:] == code):
                itemsWithCountryCode.append(item)

    # Check for items that have different suffix than the customer country suffix (for example UK when it should be NA for US)
    for itemC in itemsWithCountryCode:
        if (itemC["sku"][-2:] != customerCountryCode):
            incorrectItems.append({"itemSKU": itemC["sku"], "itemDescription": itemC["description"]})

    if (incorrectItems):
        output["detectionCriterias"].append({"name": "Ordered Incorrect Items", "description": "Some ordered items include a different suffix than the end customer country suffix", 
        "details": {"customerCountry": order.partyCountry, "customerCountrySuffix": customerCountryCode,
            "incorrectItems": incorrectItems}})

    return output


def countriesList():
    countryList = []
    countries = {
        "NA": ["United States", "Canada", "Mexico", "Colombia", "Chile"],
        "UK": ["United Kingdom", "Saudi Arabia", "Qatar", "Kuwait", "Singapore", "Hong Kong", "Malaysia"],
        "EU": ["European Economic Area", "Switzerland", "Turkey", "Russia", "Ukraine", "Israel", "United Arab Emirates",
                "Egypt", "South Africa", "Indonesia", "Philippines", "Vietnam", "Thailand"],
        "BR": ["Brazil"],
        "AR": ["Argentina"],
        "AU": ["Australia", "New Zealand"],
        "CN": ["China"],
        "IN": ["India"],
        "JP": ["Japan"],
        "KR": ["Korea"],
        "TW": ["Taiwan"],
    }
    for key, value in countries.items():
        for country in value:
            countryList.append({"country":country.lower(), "code": key})
    return countryList


# This function access CCW API and returns the Order details
def dropShippingDetection(orderId, clientId, clientSecret, username, password):
    report = {}

    accessToken = ccwquery.get_access_token(clientId,clientSecret,username,password)
    orderText = ccwquery.get_order_details(accessToken, str(orderId))
    order=ccwparser.CCWOrderParser(orderText)
    # Check if the shipment got shipped to the customer directly or through partner
    output = shippedToCustomer(order)
    # Check incorrect items only if the order was not directly shipped to customer
    if (output):
        output2 = checkItems(order, output)
        report = output2
    else:
        report = output

    return report


# This function creates the structure of the Webex Card 
def getDetailCard(report, workingPath):

    with open(f'{workingPath}/SRC/responseCard.json', 'r') as json_file:
        cardResponse= json.load(json_file)
    
    with open(f'{workingPath}/SRC/responseCardItem.json', 'r') as json_file:
        cardResponseItem = json.load(json_file)

    if "detectionCriterias" in report:
                
        # If the card contains one criteria 
        if len(report["detectionCriterias"]) == 1:
            cardResponse["content"]["body"][0]["columns"][0]["items"][1]["text"] += str(report["orderWebId"])
            cardResponse["content"]["body"][0]["columns"][0]["items"][2]["text"] += report["detectionCriterias"][0]['description']
            for k,v in report["detectionCriterias"][0]["details"].items():
                cardResponse["content"]["body"][0]["columns"][0]["items"][3]["text"] +=  k + " : " + v + "\n"
            detailCard = cardResponse

        # If the card contains two detections criterias
        else: 

            cardResponseItem["content"]["body"][0]["columns"][0]["items"][1]["text"] += str(report["orderWebId"])
            cardResponseItem["content"]["body"][0]["columns"][0]["items"][2]["text"] += report["detectionCriterias"][0]['description']
 
            for k,v in report["detectionCriterias"][0]["details"].items():

                cardResponseItem["content"]["body"][0]["columns"][0]["items"][3]["text"] +=  k + " : " + v + "\n"

            cardResponseItem["content"]["body"][0]["columns"][0]["items"][4]["text"] += report["detectionCriterias"][1]['name']
            cardResponseItem["content"]["body"][0]["columns"][0]["items"][5]["text"] += report["detectionCriterias"][1]['description']
            cardResponseItem["content"]["body"][0]["columns"][0]["items"][6]["text"] += str(report["detectionCriterias"][1]['details']['customerCountry'])
            cardResponseItem["content"]["body"][0]["columns"][0]["items"][7]["text"] += str(report["detectionCriterias"][1]['details']['customerCountrySuffix'])

            for i in report["detectionCriterias"][1]['details']["incorrectItems"]:
                for k,v in i.items():
                    cardResponseItem["content"]["body"][0]["columns"][0]["items"][8]["text"] +=  k + " : " + v + "\n"
                cardResponseItem["content"]["body"][0]["columns"][0]["items"][8]["text"] += "\n"
            detailCard = cardResponseItem
    else:
        print("No detection criteria")
    return detailCard



# PROCESS ORDERS DROPSHIPPING DETECTION AND SEND BACK A TABLE REPORT TO THE CUSTOMER
def sendTableReport(orderIds, clientId, clientSecret, username, password, data, workingPath, token):
    # CARD
    with open(f'{workingPath}/SRC/rowSeparator.json', 'r') as json_file:
        rowSeparator = json.load(json_file)
    with open(f'{workingPath}/SRC/rowButton.json', 'r') as json_file:
        rowButton = json.load(json_file)
    with open(f'{workingPath}/SRC/columnCard.json', 'r') as json_file:
        columnCard = json.load(json_file)

    noDropShipping =[]
    histReport = []

    for orderId in orderIds:
        try:
            # GET DROPSHIPPING REPORT
            report = dropShippingDetection(orderId, clientId, clientSecret, username, password)
            if (report):
                if(report["orderWebId"] in histReport):
                    print("already in report")
                else:
                    histReport.append(report["orderWebId"])
                    detailCard = {}
                    detailCard = getDetailCard(report, workingPath)

                    # ROW STRUCTURE
                    with open(f'{workingPath}/SRC/row.json', 'r') as json_file:
                        row = json.load(json_file)

                    # ROW
                    row["columns"][0]["items"][0]["text"] += str(report["orderWebId"])
                    row["columns"][1]["items"][0]["text"] += report["detectionCriterias"][-1]['description']
                    # END ROW

                    # ADD ROW TO CARD
                    columnCard["content"]["body"].append(row)

                    with open(f'{workingPath}/SRC/rowButton.json', 'r') as json_file:
                        rowButton = json.load(json_file)
                    rowButton["columns"][0]["items"][0]["actions"][0]["url"] = f"https://apps.cisco.com/qtc/viewstat/open.order?flow=nextgen&orderId={report['salesOrderNum']}"
                    rowButton["columns"][0]["items"][0]["actions"][1]["card"]["body"] = detailCard["content"]["body"]

                    columnCard["content"]["body"].append(rowButton)
                    columnCard["content"]["body"].append(rowSeparator)
            else:
                noDropShipping.append(orderId)
        except:
            print("Nothing detected")
            noDropShipping.append(orderId)

    print("\n\n")

    print(noDropShipping)
    if(len(orderIds) != len(noDropShipping)):
        sendCardToPersonId(token, data["data"]["personId"], columnCard)
    else:
        message = "No potential drop shipping was detected for order/s: " + ", ".join(noDropShipping)
        #sendMessageToPersonId(token, data["data"]["personId"], message) 

    if (noDropShipping):
        message = "No potential drop shipping was detected for order/s: " + ", ".join(noDropShipping)
        sendMessageToPersonId(token, data["data"]["personId"], message) 

