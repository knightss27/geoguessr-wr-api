from lxml import html
import requests
import string
import json
from pprint import pprint

def get_records():
    records = []
    page = requests.get('https://geotips.net/wp-json/wp/v2/pages/114')
    page = json.loads(page.content)
    tree = html.fromstring(page['content']['rendered'])
    
    solo_streaks_rows = tree.xpath("//div[contains(@data-id, '807df07')]//tr")
    assisted_streaks_rows = tree.xpath("//div[contains(@data-id, 'ed954fa')]//tr")
    speedrun_rows = tree.xpath("//div[contains(@data-id, '029820e')]//tr")
    no_moving_rows = tree.xpath("//div[contains(@data-id, 'ef1f000')]//tr")
    

    records = {}
    for row in no_moving_rows:
        names = row.xpath('./td')
        if len(row) > 0:
            print(row[0].text_content())
            # records[names[0].text_content()] = ['test']
    
    # pprint(rows)

get_records()

