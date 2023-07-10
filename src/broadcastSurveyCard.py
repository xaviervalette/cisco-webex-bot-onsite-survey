from functions import *
import yaml

with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)

with open('ressources/surveyCard.json', 'r') as json_file:
    surveyCard = json.load(json_file)

broadcastSurveyCard(config["botToken"], surveyCard)