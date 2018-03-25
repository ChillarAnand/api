import pickle
import os

import hug
import requests
from bs4 import BeautifulSoup


def get_air_news(date, time):
    date = date.replace('-', '/')

    if time == '9AM':
        time = '9:46:53 AM'
    elif time == '9PM':
        time = '9:46:53 PM'
    elif time == '1PM':
        time = '4:46:53 PM'

    category = '{} {}'.format(date, time)

    url = 'http://www.newsonair.com/showArchive.asp'
    data = {"table": "tmp_full_news", "category": category}

    response = requests.post(url, data=data)
    data = response.text

    return data


def extract_text(html, child='li'):
    soup = BeautifulSoup(html, 'html.parser')
    text = [element.text for element in soup.find_all(child)]
    return text


def parse_news(data):
    data = data.split('THE HEADLINES')[1]
    blocks = data.split('[]&lt;&gt;&lt;&gt;&lt;&gt;[]')

    headlines = extract_text(blocks[0])
    content = [extract_text(block, child='p') for block in blocks[1:]]

    news = {'headlines': headlines, 'news': content}
    return news


@hug.get('/airnewsarchives')
def happy_birthday(date, time):

    localfile ='{}-{}.pkl'.format(date, time)

    if os.path.exists(localfile):
        with open(localfile, 'rb') as fh:
            data = pickle.load(fh)
    else:
        try:
            data = get_air_news(date, time)
            data = parse_news(data)
        except Exception as e:
            data = f'Unable to retrieve {localfile}'
            print(data)

        with open(localfile, 'wb') as fh:
            pickle.dump(data, fh)

    return data
