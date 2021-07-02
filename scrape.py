"""
Functions to automatically gather and clean the dougscore data.
"""
import pandas as pd
from bs4 import BeautifulSoup as soup
import requests

def scrape(url):
    """
    Takes url as a string, gets html, gathers links to youtube videos,
    converts table to dataframe, appends links from <a> tags
    and returns final dataframe.
    """
    print('scraping google sheet...')
    try:
        r = requests.get(url)
        mysoup = soup(r.text, 'lxml')
        test = mysoup.prettify()
        with open('test.html','w') as file: file.write(test)
        tds = mysoup.findAll('td', {'class': ['s15', 's18']})
        anchors = [ td.find('a') for td in tds ]
        hrefs = [ anchor['href'] if anchor is not None else None for anchor in anchors ]
        dfs = pd.read_html(r.text)
        if len(dfs) > 0:
            df = dfs[0]
            html_table = df.to_html()
            headers = df.iloc[[2],4:]
            headers = headers.loc[[2]].values.tolist()[0]
            df = df.iloc[4:,1:]
            df = df.dropna(how='all')
            df.columns = ['Year', 'Make', 'Model'] + headers
            df['Links'] = hrefs
            df = df.rename(columns={'Video Link': 'Video Duration MM:SS'})
            df = df.dropna(how='any')
            # df.to_csv('output/dougie.csv', index=False)
        else:
            df = pd.DataFrame({'error': 0})
        return df
    except Exception as e:
        print('failed', e)
        return e

def car_data(df):
    """
    gets vehicle data such as cylinders and displacements
    then appends to the dougscore data
    """
    print('getting vehicle data...')
    def vehicle_id(vehicle):
        print('vehicle: ', vehicle.name)
        url = f"https://www.fueleconomy.gov/ws/rest/vehicle/menu/options?year={vehicle['Year']}&make={vehicle['Make']}&model={vehicle['Model']}"
        r = requests.get(url)
        s = soup(r.text,'lxml')
        value = s.find('value')
        id = value.text if value else None
        return vehicle_info(id)

    def vehicle_info(id):
        url = f"https://www.fueleconomy.gov/ws/rest/vehicle/{id}"
        r = requests.get(url)
        s = soup(r.text,'lxml')
        targets = [
            'cylinders',
            'displ',
            'drive',
            'trany'
        ]
        data = [ s.find(target).text if s.find(target) else None for target in targets ]
        return data

    new_columns = ['cylinders', 'displacement', 'drive', 'transmission']
    df2 = df[['Year', 'Make', 'Model']].apply(vehicle_id, axis=1, result_type='expand')
    df2.columns = new_columns
    df3 = df.join(df2)
    return df3

if __name__=="__main__":
    #for testing
    url = 'https://docs.google.com/spreadsheets/u/0/d/e/2PACX-1vSYuGzOjstKqwnsG8TP2gdnTzddtVH0qgJMVGuE82DAxEk6IKWrrfAf7ittqigfIiVkkFk7qF7bgij8/pubhtml/sheet?headers=false&gid=0'
    df = scrape(url)
    df2 = car_data(df)
    print(df2.head())
    df2.to_csv('output/embellished.csv', index=False)

