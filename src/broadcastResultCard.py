from functions import *
import yaml

with open('data/answers.json', 'r') as openfile:
    previousWeeks = json.load(openfile)

with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)

with open('ressources/resultCard.json', 'r') as json_file:
    resultCard = json.load(json_file)

broadcastResultCard(config["botToken"], resultCard)