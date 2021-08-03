"""
Functions to gather review year to determnine age of vehicle and add it to
the dataset. Cleans dataset by removing information that is no longer
necessary.
"""

import pandas as pd
import requests
from key import key
from urllib.parse import unquote

def video_year(link, key):
    link2 = unquote(link)
    id = link2.split('v=')[1].split('&')[0]
    url = f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={id}&key={key}'
    r = requests.get(url)
    data = r.json()
    year = data['items'][0]['snippet']['publishedAt'].split('-')[0]
    return year

def clean_cols(df, key):
    print('cleaning up...')
    df = df.dropna(subset=['drive']).reset_index()
    df['video_year'] = df['Links'].apply(video_year, args=(key,))
    df['age'] = df['video_year'].astype('int') - df['Year'].astype('int')
    df['age'] = df['age'].map(lambda x: x if x >= 0 else 0)
    df['transmission'] = df['transmission'].map(lambda type: type.split(' ')[0])
    columns = [
        'Year',
        'Make',
        'Model',
        'DOUGSCORE',
        'Vehicle Country',
        'cylinders',
        'displacement',
        'drive',
        'transmission',
        'age'
    ]

    def drive_replace(description):
        if 'all' in description.lower():
            return 'All Wheel Drive'
        elif '4' in description.lower():
            return '4 Wheel Drive'
        elif 'front' in description.lower():
            return 'Front Wheel Drive'
        elif 'rear' in description.lower():
            return 'Rear Wheel Drive'
        else:
            return 'No Info'

    df['drive'] = df['drive'].map(drive_replace)
    return df[columns]

if __name__=="__main__":
    df = pd.read_csv('output/embellished.csv')
    df = clean_cols(df, key)
    print(df.head())
    df.to_csv('output/embellished_clean.csv', index=False)