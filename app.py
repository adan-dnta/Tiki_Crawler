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
TIKI_URL = 'https://tiki.vn/'

def delete():
  cur.execute("DELETE FROM categories;")

def create_main_categories():
  query = ''' CREATE TABLE IF NOT EXISTS categories
              (id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(255), url TEXT, parent_id  INT, create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
          '''
  try:
    cur.execute(query)
  except Exception as err:
    print('ERROR BY CREATE TABLE', err)  

def select_all():
  return cur.execute("SELECT * FROM categories;").fetchall()


class Category:
  def __init__(self, cat_id, name, url, parent_id):
    self.cat_id = cat_id
    self.name = name
    self.url = url
    self.parent_id = parent_id
  
  def __repr__(self):
    return "ID: {}, Name: {}, URL: {}, Parent_id: {}".format(self.cat_id, self.name, self.url, self.parent_id)
  
  def save_into_db(self):
    query = '''
            INSERT INTO categories (name, url, parent_id)
            VALUES (?,?,?);
            '''
    val = (self.name, self.url, self.parent_id)
    try: 
      cur.execute(query, val)
      conn.commit()
      self.cat_id = cur.lastrowid
      conn.commit()
    except Exception as err:
      print('ERROR BY INSERT', err)

def get_url(url):
  #time.sleep(1)
  try:
    response = requests.get(url).text
    response = BeautifulSoup(response, 'html.parser')
    return response
  except Exception as err:
      print('ERROR BY REQUEST', err)

def get_main_categories(save_db = False):
  soup = get_url(TIKI_URL)
  result = []
  try:
    for a in soup.find_all('a', {'class':'MenuItem__MenuLink-tii3xq-1 efuIbv'}):
      cat_id = None
      name = a.find('span', {'class':'text'}).text
      url = a['href']
      parent_id = None

      cat = Category(cat_id, name, url, parent_id)
      if save_db:
        cat.save_into_db()
      result.append(cat)
  except Exception as err:
      print('ERROR BY GET MAIN CATEGORIES', err)
  return result

def get_sub_categories(category, save_db = False):
  soup = get_url(category.url)
  result = []
  try:
    for div in soup.find_all('div', {'class':'list-group-item is-child'}):
      sub_id = None
      sub_name = re.sub(' ', '', div.a.text)
      sub_url = 'https://tiki.vn' + div.a['href']
      sub_parent_id = category.cat_id

      sub = Category(sub_id, sub_name, sub_url, sub_parent_id)
      if save_db:
        sub.save_into_db()
      result.append(sub)
  except Exception as err:
    print('ERROR BY GET SUB CATEGORIES', err)
  return result

def get_all_categories(main_categories):
  de = deque(main_categories)
  count = 0

  while de:
    parent_cat = de.popleft()
    sub_cat = get_sub_categories(parent_cat, save_db = True)
    # print(sub_cat)
    de.extend(sub_cat)
    count += 1
    if count % 100 == 0:
      print(count, 'times')

def select_url():
  return cur.execute("SELECT url FROM categories WHERE parent_id > 600;").fetchall()

""" def get_content():
  urls = select_url()
  list_items = []
  for url in urls:
    soup = get_url(url)
    try:
      d = {'Name':'', 'Price':'', 'Image':''}
      for div in soup.find_all('div', {'class':'product-item'}):
        d['Name'] = div.find('p', {'class':'title'}).text
        d['Price'] = div.find('span', {'class':'final-price'}).text
        d['Image'] = div.img['src']
        list_items.append(d)  
    except Exception as err:
        print('ERROR BY GET CONTENT', err)
  return list_items """

def get_content():
    soup = get_url('https://tiki.vn/may-rua-chen/c3864?src=c.4221.hamburger_menu_fly_out_banner%27,)%27&_lc=Vk4wMzkwMjEwMDM%3D')
    list_items=[]
    try:
      for div in soup.find_all('div', {'class':'product-item'}):
        d = {'Name':'', 'Price':'', 'Image':''}
        d['Name'] = div.img['title']
        d['Price'] = div.find('span', {'class':'final-price'}).text
        d['Image'] = div.img['src']
        list_items.append(d)  
    except:
       pass
    return list_items

create_main_categories()  
main_categories = get_main_categories(save_db=True)

get_all_categories(main_categories[:2])
data = get_content()
print(data)

@app.route('/')
def index():
    return render_template('home.html', data = data)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)
 