from requests import get
from bs4 import BeautifulSoup
import sqlite3
import threading
import requests

def send_msg(text, user):
  token = '1901737419:AAHaDsUkEQTZEPOC0RUKYqIhHmQrPJJFAic'
  url_req = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={user}&text={text}'
  results = requests.get(url_req)
  print(results.json())
  
def olx_search(word, min_price=0, max_price=99999999, category = '', city = '', distance = 0, search_amount=0, user=''):
  try:
    min_price = int(min_price)
  except:
    min_price = 0

  try:
    max_price = int(max_price)
  except:
    max_price = 99999999

  connectDB = sqlite3.connect(f'{word}.db')
  cDB = connectDB.cursor()
  cDB.execute(f"""CREATE TABLE IF NOT EXISTS tasks (
          name text,
          price INTEGER,
          link text
      )""")

  if not category and not city:
    URL = f'https://www.olx.pl/oferty/q-{word}/?search%5Bfilter_float_price%3Afrom%5D={min_price}&search%5Bfilter_float_price%3Ato%5D={max_price}%3Fpage%3D5&page=1'

  if category and not city:
    URL = f'https://www.olx.pl/{category}/q-{word}/?search%5Bfilter_float_price%3Afrom%5D={min_price}&search%5Bfilter_float_price%3Ato%5D={max_price}%3Fpage%3D5&page=1'

  if category and city:
    URL = f'https://www.olx.pl/{category}/{city}/q-{word}/?search%5Bfilter_float_price%3Afrom%5D={min_price}&search%5Bfilter_float_price%3Ato%5D={max_price}&search%5Bdist%5D={distance}&page=1'

  if not category and city:
    URL = f'https://www.olx.pl/{city}/q-{word}/?search%5Bfilter_float_price%3Afrom%5D={min_price}&search%5Bfilter_float_price%3Ato%5D={max_price}&search%5Bdist%5D={distance}&page=1'
  page = get(URL).content 
  bs = BeautifulSoup(page, 'html.parser')

  try:
    pages_amount = int(bs.find(attrs={"data-cy" : "page-link-last"}).get_text())
    print('test pages_amount', pages_amount)
  except:
    pages_amount = 1

  # Sprawdza czy już skanowało 10 razy

  if search_amount<4:

    for page_number in range(1, pages_amount+1):
      print('numer strony: ', page_number)

      if not category and not city:
        URL = f'https://www.olx.pl/oferty/q-{word}/?search%5Bfilter_float_price%3Afrom%5D={min_price}&search%5Bfilter_float_price%3Ato%5D={max_price}%3Fpage%3D5&page={page_number}'

      if category and not city:
        URL = f'https://www.olx.pl/{category}/q-{word}/?search%5Bfilter_float_price%3Afrom%5D={min_price}&search%5Bfilter_float_price%3Ato%5D={max_price}%3Fpage%3D5&page={page_number}'

      if category and city:
        URL = f'https://www.olx.pl/{category}/{city}/q-{word}/?search%5Bfilter_float_price%3Afrom%5D={min_price}&search%5Bfilter_float_price%3Ato%5D={max_price}&search%5Bdist%5D={distance}&page={page_number}'

      if not category and city:
        URL = f'https://www.olx.pl/{city}/q-{word}/?search%5Bfilter_float_price%3Afrom%5D={min_price}&search%5Bfilter_float_price%3Ato%5D={max_price}&search%5Bdist%5D={distance}&page={page_number}'


      print(URL)
      page = get(URL).content 
      bs = BeautifulSoup(page, 'html.parser')
      try:
        empty_list = bs.find(class_ = 'emptynew').get_text()
        #.find('span')
        print('Brak wyszukań')
        connectDB.close()
        return
      except:
        pass


      offer_list = bs.find('table', id="offers_table").find_all(class_ = 'offer-wrapper')

      for offer in offer_list:
        offer_name = offer.find(class_ = 'margintop5').find('strong').get_text().replace("'", "").replace('"', '')
        try:
          offer_link = offer.find(href=True)['href']
          #offer.find('a', class_="detailsLink")
          print(offer_link)

        except:
          offer_link = ''
          print('link problem')
        try:
          offer_price = offer.find(class_ = 'price').find('strong').get_text()
        except:
          offer_price = 0
        try:
          offer_price = offer_price.replace('zł', '').replace(' ', '').replace(',', '.')
          offer_price = int(offer_price)
        except:
          pass
        cDB.execute(f"SELECT * FROM tasks WHERE name='{offer_name}' AND price='{offer_price}'")
        offerts_list = cDB.fetchall()

        if len(offerts_list) == 0:
          cDB.execute("INSERT INTO tasks VALUES (?,?,?)", (offer_name, offer_price, offer_link))
          connectDB.commit()
          print('Nowa oferta:', offer_price, 'zł', offer_name, offer_link)
          
        elif len(offerts_list)>0:
          print('Oferta juz istniała: ', offer_price, 'zł', offer_name)
          pass

  # Jeśli było skanowane więcej niz 10 razy
  elif search_amount >= 4:
    for page_number in range(1, 2):
      print('numer strony: ', page_number)

      if not category and not city:
        URL = f'https://www.olx.pl/oferty/q-{word}/?search%5Bfilter_float_price%3Afrom%5D={min_price}&search%5Bfilter_float_price%3Ato%5D={max_price}%3Fpage%3D5&page={page_number}'

      if category and not city:
        URL = f'https://www.olx.pl/{category}/q-{word}/?search%5Bfilter_float_price%3Afrom%5D={min_price}&search%5Bfilter_float_price%3Ato%5D={max_price}%3Fpage%3D5&page={page_number}'

      if category and city:
        URL = f'https://www.olx.pl/{category}/{city}/q-{word}/?search%5Bfilter_float_price%3Afrom%5D={min_price}&search%5Bfilter_float_price%3Ato%5D={max_price}&search%5Bdist%5D={distance}&page={page_number}'

      if not category and city:
        URL = f'https://www.olx.pl/{city}/q-{word}/?search%5Bfilter_float_price%3Afrom%5D={min_price}&search%5Bfilter_float_price%3Ato%5D={max_price}&search%5Bdist%5D={distance}&page={page_number}'

      print(URL)
      page = get(URL).content 
      bs = BeautifulSoup(page, 'html.parser')
      try:
        empty_list = bs.find(class_ = 'emptynew').get_text()
        print('Brak wyszukań')
        connectDB.close()
        return
      except:
        pass

      offer_list = bs.find('table', id="offers_table").find_all(class_ = 'offer-wrapper')

      for offer in offer_list:
        offer_name = offer.find(class_ = 'margintop5').find('strong').get_text().replace("'", "").replace('"', '')
        try:
          offer_price = offer.find(class_ = 'price').find('strong').get_text()
        except:
          offer_price = 0
        try:
          offer_link = offer.find(href=True)['href']
          print(offer_link)
        except:
          offer_link = ''
          print('link problem')
        try:
          offer_price = offer_price.replace('zł', '').replace(' ', '').replace(',', '.')
          offer_price = int(offer_price)
        except:
          pass
        cDB.execute(f"SELECT * FROM tasks WHERE name='{offer_name}' AND price='{offer_price}'")
        offerts_list = cDB.fetchall()

        if len(offerts_list) == 0:
          cDB.execute("INSERT INTO tasks VALUES (?,?,?)", (offer_name, offer_price, offer_link))
          connectDB.commit()
          print('Nowa oferta:', offer_price, 'zł', offer_name, offer_link)
          send_msg(f'Nowa oferta: {offer_name}, CENA: {offer_price} pln, LINK: {offer_link}', user)

        elif len(offerts_list)>0:
          print('Oferta juz istniała: ', offer_price, 'zł', offer_name)
          pass
  connectDB.close()


def searching_function_loop():
  threading.Timer(60.0, searching_function_loop).start()
  connectDB = sqlite3.connect('search_phrases.db')
  cDB = connectDB.cursor()
  cDB.execute("SELECT rowid, * FROM pharses")
  searches_list = cDB.fetchall()
  
  for search in searches_list:
    olx_search(search[1], min_price=search[2], max_price=search[3], category=search[4], city=search[5], distance=search[6], search_amount=search[7], user=search[8])
    
    new_number = search[7]+1
    cDB.execute(f"""
    UPDATE pharses
    SET search_amount = '{new_number}'
    WHERE rowid = {search[0]};
    """) 
    connectDB.commit()
    print('ilość wyszukań: ', search[7]+1)
  connectDB.close()


'''
def search_phrases_db():

  connectDB = sqlite3.connect(f'search_phrases.db')
  cDB = connectDB.cursor()

  cDB.execute(f"""CREATE TABLE IF NOT EXISTS pharses(
          phrase text,
          min_price INTEGER,
          max_price INTEGER,
          category text,
          city text,
          max_distance INTEGER,
          search_amount INTEGER,
          user text
      )""")

  connectDB.close()

search_phrases_db()
'''