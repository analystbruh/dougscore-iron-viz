import scrape
import clean

url = 'https://docs.google.com/spreadsheets/u/0/d/e/2PACX-1vSYuGzOjstKqwnsG8TP2gdnTzddtVH0qgJMVGuE82DAxEk6IKWrrfAf7ittqigfIiVkkFk7qF7bgij8/pubhtml/sheet?headers=false&gid=0'
df_scrape = scrape.scrape(url)
df_cars = scrape.car_data(df_scrape)
df_final = clean.clean_cols(df_cars, clean.key)
df_final.to_csv('dougscore.csv')