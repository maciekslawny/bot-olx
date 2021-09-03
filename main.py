from flask import Flask, redirect, url_for, render_template, request
from search import olx_search, searching_function_loop, send_msg
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "hello"

@app.route("/")
def main():
  connectDB = sqlite3.connect('search_phrases.db')
  cDB = connectDB.cursor()
  cDB.execute("SELECT rowid, * FROM pharses")
  searches_list = cDB.fetchall()
  connectDB.close()
  return render_template("index.html", searches_list = searches_list)

@app.route("/add", methods = ["POST", "GET"])
def add_pcharse():  
  if request.method == "POST":
    connectDB = sqlite3.connect('search_phrases.db')
    cDB = connectDB.cursor()
    phrase = request.form["phrase"]
    min_price = request.form["min_price"]
    max_price = request.form["max_price"]
    category = request.form["category"]
    user = request.form["user"]
    print(category)
    city = request.form["city"]
    max_distance = request.form["max_distance"]
    search_amount = 0
    cDB.execute(f"SELECT * FROM pharses WHERE phrase = '{phrase}'")
    same_items = cDB.fetchall()
    while len(same_items)>0:
      phrase = f'{phrase} '
      cDB.execute(f"SELECT * FROM pharses WHERE phrase = '{phrase}'")
      same_items = cDB.fetchall()
    cDB.execute("INSERT INTO pharses VALUES (?,?,?,?,?,?,?, ?)", (phrase, min_price, max_price, category, city, max_distance, search_amount, user))
    connectDB.commit()
    connectDB.close()
    print(phrase, min_price, max_price, category, city, max_distance)
    send_msg(f'Dodano nowe wyszukiwanie: {phrase}', user)
  return redirect(url_for("main"))


@app.route("/delete/<item_id>")
def delete(item_id):
  print(item_id)
  connectDB = sqlite3.connect('search_phrases.db')
  cDB = connectDB.cursor()
  cDB.execute(f"SELECT * FROM pharses WHERE ROWID = '{item_id}'")
  item_name = cDB.fetchall()[0][0]
  
  try:
    os.remove(f"{item_name}.db")
  except:
    pass
  cDB.execute(f"DELETE FROM pharses WHERE ROWID = '{item_id}'")
  
  connectDB.commit()
  connectDB.close()
  return redirect(url_for("main"))

@app.route("/start")
def start():
  searching_function_loop()
  return redirect(url_for("main"))

if __name__ == "__main__":
  app.run(debug=True)