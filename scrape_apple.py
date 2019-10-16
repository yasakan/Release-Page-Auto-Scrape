import requests
from bs4 import BeautifulSoup
import json
import re
import datetime
import pymsteams

def scrape():
    pattern = '\(.+\)'

    url = 'https://developer.apple.com/news/releases/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.findAll('article')
    
    articles_dict = {}
    for article in articles:
        product_name = article.find("a").find("h2").getText()
        product_date = article.find(class_="article-date").getText()
        articles_dict[re.sub(pattern, '', product_name).strip()] = {'product_name': product_name, 'product_date': product_date, 'url': url}

    return articles_dict

def analyze_json(articles_dict):
    copy_dict = articles_dict.copy()
    for article in articles_dict:
        product_name = article
        product_date = articles_dict[product_name]['product_date']
        product_date_formatted = datetime.datetime.strptime(product_date, '%B %d, %Y')
        
        now = datetime.datetime.now()
        dt = now - product_date_formatted
        if dt >= datetime.timedelta(hours=24):
            del copy_dict[product_name]
        
    return copy_dict

def post_teams(articles_dict):
    url = 'Your Incoming Webhook URL'

    for product in articles_dict:
        myTeamsMessage = pymsteams.connectorcard(url)
        myTeamsMessage.title("【Apple】" + product)

        message = "Product: {0}<br>Updated At: {1}<br>[Web]({2})".format(articles_dict[product]['product_name'], articles_dict[product]['product_date'], articles_dict[product]['url'])
        myTeamsMessage.text(message)
        myTeamsMessage.send()
        
def main(event, context):
    articles_dict = scrape()
    analyzed_dict = analyze_json(articles_dict)
    if len(analyzed_dict) > 0:
        post_teams(analyzed_dict)
