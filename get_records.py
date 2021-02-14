from lxml import html
import requests
import string
import json
from pprint import pprint
import re

def sanitize(text: str):
    text = text.lower()
    text = text.replace(' ', '-')
    text = re.sub(r'(\')|(\()|(\))', '', text)
    text = re.sub(r'(nm)|(non-moving)', 'nm', text)
    return text


def get_record_base(text: str):
    title = text;
    record = {}
    if 'nm' in title:
        record['name'] = 'nm'
        title = title.replace('nm', '')
    elif 'nmpz' in title:
        record['name'] = 'nmpz'
        title = title.replace('nmpz', '')
    elif 'ncnc' in title:
        record['name'] = 'ncnc'
        title = title.replace('ncnc', '')

    if 'streaks' or 'streak' in title:
        record['category'] = 'streaks'
        title = re.sub(r'(streaks)|(streak)', '', title)

    
    
    return record


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
    for row in solo_streaks_rows:
        names = row.xpath('./td')
        if len(row) > 0 and row[0].text_content() != "":
            print(sanitize(row[0].text_content()))
            record = {
                'category': sanitize(row[0].text_content())
            }

            # print(record)

            # requests.post('http://localhost:8000/add', data={
            #     category: ''
            # })
            # records[names[0].text_content()] = ['test']
    
    # pprint(rows)

get_records()

