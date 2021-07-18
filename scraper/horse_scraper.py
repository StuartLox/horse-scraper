import requests
import pandas 
from bs4 import BeautifulSoup
import urllib
import re
import pandas as pd
import datetime


def get_opensea_horses():
    zed_page = requests.get('https://opensea.io/assets/zed-run-official?search[sortAscending]=false&search[sortBy]=LISTING_DATE')
    soup = BeautifulSoup(zed_page.content, 'html.parser')
    zed_horses = [i.get_text() for i in soup.find_all(class_='AssetCardFooter--name')]
    zed_prices = [i.get_text() for i in soup.find_all(class_='AssetCardFooter--price-amount')]

    return [{'Name': name, 'Price': price.strip()} for price, name in zip(zed_prices, zed_horses)]


def _know_my_horse_lookup(horse_name):
    base_url = 'https://knowyourhorses.com/horses'
    r = requests.get(base_url, params={'search': horse_name})
    return r.content


def _extract_page_data(content):
    soup = BeautifulSoup(content, 'html.parser')

    # Extract key attributes from content
    race_attr = soup.find(class_='card-body d-flex flex-wrap').find_all(class_='attribute')

    n_races = re.findall(r'(?<=races )(.*)(?=\n)', race_attr[0].text)[0]
    win_rate = re.findall(r'(?<=Win % )(.*)(?=%)', race_attr[1].text)[0]
    datetime = race_attr[0].find('time').get_text()

    return {'# Races': n_races, 'Win Rate': win_rate, 'Last Race Date': datetime}

def know_my_horse_lookup(horse_obj):
    name = horse_obj['Name']
    content = _know_my_horse_lookup(name)
    
    try:
        horse_data = _extract_page_data(content)
        horse.update(horse_data)
        return horse

    except Exception as er:
        print(f'No horse data for {name}')


def enrich_horse_data(horses):
    final = []
    for single_horse in horses:
        complete_horse_obj = know_my_horse_lookup(single_horse)
        if complete_horse_obj: 
            final.append(complete_horse_obj)
    return pd.DataFrame(final)


def main():
    horses = get_opensea_horses()

    horse_df = enrich_horse_data(horses)
    dtime = datetime.datetime.now().strftime('%Y%m%d_%H%M')
    horse_df.to_csv('horses_{dtime}.csv', index=False)


if __name__ == "__main__":
    main()