from lxml import html
import requests
import string
import json
from pprint import pprint
import re
from main import Category, Style, Name, Map, Record
from pydantic import HttpUrl

def sanitize(text: str):
    text = text.lower()
    text = text.replace(' ', '_')
    text = text.replace('.', '_')
    text = re.sub(r'(\')|(\()|(\))', '', text)
    text = re.sub(r'(nm)|(non-moving)', 'nm', text)
    return text


def get_record_base(row):
    title = sanitize(row.text_content())
    record = {}

    # print(title)

    if 'nmpz' in title:
        record['name'] = 'nmpz'
        title = title.replace('nmpz', '')
    elif 'nm' in title:
        record['name'] = 'nm'
        title = title.replace('nm', '')
    elif 'ncnc' in title:
        record['name'] = 'ncnc'
        title = title.replace('ncnc', '')

    if 'streaks' in title or 'streak' in title:
        # print('found streaks')
        record['style'] = 'streaks'
        title = re.sub(r'(streaks)|(streak)', '', title)
    elif 'hedge' in title:
        # print('found hedge')
        record['style'] = 'hedge'
        title = re.sub(r'(hedge)', '', title)
    
    return record

def get_map_info(row):
    link = row.xpath('./a')
    if len(link) > 0:
        href = link[0].xpath('./@href')[0]
        return Map(
            name=sanitize(link[0].text_content()),
            link=href,
            region='null'
        )

def get_owner(text: str):
    owner = re.sub(r'[^A-Za-z0-9_]', '', text)
    owner = sanitize(owner)
    return owner

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
        if len(row) > 0 and row[0].text_content() != "" and row[0].text_content() != "Style of Challenge":
            record_holders = row[1].text_content()
            record_holders = record_holders.split('&')
            for holder in record_holders:
                record = get_record_base(row[0])
                record['category'] = 'solo'
                record['owner'] = get_owner(holder)
                record['map'] = get_map_info(row[2])
                record['score'] = sanitize(row[3].text_content())
                record['video'] = row[4].text_content() if row[4].text_content() != "" else 'None'
                #TODO: write a get_record_video function to parse multiples etc.
                pprint(record)


            # requests.post('http://localhost:8000/add', data={
            #     category: ''
            # })
            # records[names[0].text_content()] = ['test']
    
    # pprint(rows)

get_records()

