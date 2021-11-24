import os
import requests
import config
import asyncio
from bs4 import BeautifulSoup as BS

passport_file_name = "test.json"

def main():
    response = requests.get(config.url)
    soup = BS(response.content, 'html.parser')
    items = soup.findAll('div', class_='resource-list__item-container-title')
    for item in items:
        if (item == items[1]):
            passport_url = item.find('a').get('href')
            break
    passport_url = "https://data.gov.ua" + str(passport_url)
    response = requests.get(passport_url)
    soup = BS(response.content, 'html.parser')
    items = soup.findAll('p', class_='dataset-details')
    update_date = items[0].get_text()
    write_new_date(update_date)

    print("\nurl = " + str(passport_url))

def check_last_update(update_date):
    with open("last_update.txt", 'r',encoding='latin-1') as file:
        result = file.readline()
        if(str(update_date) == result):
            return True
        else:
            return False

if __name__ == '__main__':
    main()
