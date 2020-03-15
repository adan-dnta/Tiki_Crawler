from bs4 import BeautifulSoup
import requests
import re
from collections import deque
import time

import sqlite3
conn = sqlite3.connect('tiki.db')
cur = conn.cursor()

from flask import Flask, render_template
app = Flask(__name__)

def select_url():
  return cur.execute('''SELECT p.url FROM categories AS p
                    LEFT JOIN categories AS s
                    ON p.id = s.parent_id
                    WHERE s.name is Null
                    ;
                    ''').fetchall()

def get_url(url):
  # time.sleep(1)
  try:
    response = requests.get(url).text
    response = BeautifulSoup(response, 'html.parser')
    return response
  except Exception as err:
      print('ERROR BY REQUEST', err)

def get_content(save_db = False):
  urls = select_url()
  list_items=[]
  id = 1
  for url in urls:
    soup = get_url(url[0])
    try:
      for div in soup.find_all('div', {'class':'product-item'}):
        d = {'Id':'', 'Name':'', 'Price':'', 'Image':''}
        d['Id'] = id
        id += 1
        d['Name'] = div.a['title']
        d['Price'] = re.sub('-\d+%','',div.find('span', {'class':'final-price'}).text)
        d['Image'] = div.img['src']
        list_items.append(d)
        
    except:
       pass
  return list_items

# get content from each url to data
data = get_content(save_db = True)


@app.route('/')
def index():
    return render_template('home.html', data = data)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)
 