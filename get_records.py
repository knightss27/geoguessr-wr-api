from lxml import html
import requests
import string
import json
from pprint import pprint
import re
from main import Map
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
        record['move_type'] = 'nmpz'
        title = title.replace('nmpz', '')
    elif 'nm' in title:
        record['move_type'] = 'nm'
        title = title.replace('nm', '')
    
    record['ncnc'] = False
    if 'ncnc' in title:
        record['ncnc'] = True
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
        ).dict()

def get_owner(text: str):
    owner = re.sub(r'[^A-Za-z_]', '', text) # I would like to keep numbers, but there are a few records with 4th/5th in front of the username.
    owner = sanitize(owner)
    return owner

def get_record_video(row):
    link = row.xpath('./a')
    if len(link) > 0:
        href = link[0].xpath('./@href')[0]
        return href

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
                record['video'] = get_record_video(row[4]) if row[4].text_content() != "" else "none"

            print(record)
            x = requests.post('http://localhost:8000/add', json=record, headers={"Content-Type": "application/json"})
            print(x.text)
            # records[names[0].text_content()] = ['test']
    
    # pprint(rows)

get_records()

