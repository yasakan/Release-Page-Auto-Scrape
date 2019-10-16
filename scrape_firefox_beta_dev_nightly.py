import requests
from bs4 import BeautifulSoup
import json
import re
import datetime
import pymsteams

def scrape(urls):
    articles_dict = {}

    for url in urls:
        response = requests.get(urls[url])
        soup = BeautifulSoup(response.text, 'html.parser')

        version = soup.find(class_='c-release-version').getText().strip()
        product = soup.find(class_='c-release-product').getText().strip()
        product_date = soup.find(class_='c-release-date').getText().strip()

        articles_dict[product] = {'product_name': product, 'version': version, 'product_date': product_date, 'url': urls[url]}

    return articles_dict

def analyze_dict(articles_dict):
    copy_dict = articles_dict.copy()
    for article in articles_dict:
        product_name = article
        product_date = articles_dict[product_name]['product_date']
        product_date_formatted = datetime.datetime.strptime(product_date, '%B %d, %Y')
        
        now = datetime.datetime.now()
        dt = now - product_date_formatted
        if dt > datetime.timedelta(days=1):
            del copy_dict[product_name]
        
    return copy_dict

def post_teams(articles_dict):
    url = 'Your Incoming Webhook URL'

    for product in articles_dict:
        myTeamsMessage = pymsteams.connectorcard(url)
        myTeamsMessage.title("【Browser】" + product + "【Firefox】")

        message = "Version: {0}<br>Updated At: {1}".format(articles_dict[product]['version'], articles_dict[product]['product_date'])
        myTeamsMessage.addLinkButton("Jump to Firefox Release Note.", articles_dict[product]['url'])
        myTeamsMessage.text(message)

        myTeamsMessage.send()
        return

def main(request):
    urls = {'nightly': 'https://www.mozilla.org/ja/firefox/nightly/notes/', 'beta': 'https://www.mozilla.org/ja/firefox/beta/notes/', 'developer edition': 'https://www.mozilla.org/ja/firefox/developer/notes/'}

    articles_dict = scrape(urls)
    analyzed_dict = analyze_dict(articles_dict)
    if len(analyzed_dict) > 0:
        post_teams(analyzed_dict)
    return json.dumps(analyzed_dict, indent=2)