import requests
from bs4 import BeautifulSoup
import json
import pandas as pd


ALL_COLLECTIONS_URL = "https://api.opensea.io/api/v1/collections?offset=0&limit="
headers = {"Accept": "application/json"}
COLLECTION_URL = "https://api.opensea.io/api/v1/collection/"
description_keys = ['name', 'medium_username', 'telegram_url', 'twitter_username', "discord_url",'instagram_username',
                    'wiki_url', 'description']

stats_keys = ['floor_price','average_price','market_cap']


def getUrl(type):
    if type == "24h":
        return "https://opensea.io/rankings?sortBy=one_day_volume"

    elif type == "7d":
        return "https://opensea.io/rankings?sortBy=seven_day_volume"

    elif type == "30d":
        return "https://opensea.io/rankings?sortBy=thirty_day_volume"

    elif type == "total":
        return "https://opensea.io/rankings?sortBy=total_volume"
    else:
        raise ValueError('Invalid type provided. Expected: 24h,7d,30d,total. Got: ${type}')


def process_all(limit):
    if limit > 1E10:
        raise ValueError('collections requested exceeds limit')

    url = ALL_COLLECTIONS_URL + str(limit)

    response = requests.request("GET", url, headers=headers)

    print(response.text)


def get_collection(slug):
    url = COLLECTION_URL + slug

    response = requests.request("GET", url)
    data = response.json()["collection"]
    result = {}
    payment_tokens = data['payment_tokens']
    token_symbols = ''
    for token in payment_tokens:
        token_symbols += token['symbol'] + " "

    for key in description_keys:
        result[key] = data[key]

    result['payment_tokens'] = token_symbols
    stats = data['stats']
    for key in stats_keys:
        result[key] = stats[key]
    return result


def get_top_collections(type):
    url = getUrl(type)
    html = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})

    soup = BeautifulSoup(html.text)
    data = json.loads(soup.find(id='__NEXT_DATA__').get_text())
    collections = data['props']['relayCache'][0][1]['json']['data']['rankings']['edges']
    result = []
    for col in collections:
        slug = col['node']['slug']
        #floorprice = col['node']['statsV2']['floorPrice']
        result.append(slug)

    return result


def process():
    top_collections = get_top_collections("7d")
    rows_list = []
    for slug in top_collections:
        print ('... processing :' + slug)
        values = get_collection(slug)
        rows_list.append(values)
        print(values)

    df = pd.DataFrame(rows_list)
    df.to_csv('/home/badr/projects/opensea/opensea_top_collections.csv')




if __name__ == "__main__":
    process()
