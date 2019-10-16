import requests
from bs4 import BeautifulSoup
import json
import re
import datetime
import pymsteams

def scrape():
    url = 'https://chromereleases.googleblog.com'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.findAll(class_='post')
    
    articles_dict = {}
    for article in articles:
        product_name = article.find(class_='title').find('a').getText().strip()
        product_date = article.find(class_='publishdate').getText().strip()
        url = article.find(class_='title').find('a').get('href').strip()
        if not product_name in articles_dict:
            articles_dict[product_name] = {'product_name': product_name, 'product_date': product_date, 'url': url}

    return articles_dict

def analyze_dict(articles_dict):
    copy_dict = articles_dict.copy()
    for article in articles_dict:
        product_name = article
        product_date = articles_dict[product_name]['product_date']
        product_date_formatted = datetime.datetime.strptime(product_date, '%A, %B %d, %Y')
        
        now = datetime.datetime.now()
        dt = now - product_date_formatted
        if dt > datetime.timedelta(days=1):
            del copy_dict[product_name]
        
    return copy_dict

def post_teams(articles_dict):
    url = 'Your Incoming Webhook URL'

    for product in articles_dict:
        myTeamsMessage = pymsteams.connectorcard(url)
        myTeamsMessage.title("【Browser】" + product + "【Chrome】")

        message = "Title: {0}<br>Updated At: {1}".format(articles_dict[product]['product_name'], articles_dict[product]['product_date'])
        myTeamsMessage.text(message)
        myTeamsMessage.addLinkButton("Jump to Google Blog.", articles_dict[product]['url'])
        myTeamsMessage.send()

def main(event, context):
    articles_dict = scrape()
    analyzed_dict = analyze_dict(articles_dict)
    if len(analyzed_dict) > 0:
        post_teams(analyzed_dict)
