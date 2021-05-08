"""
Help script for collecting stocks with their corresponding ticker symbol
"""

import json

import requests
from bs4 import BeautifulSoup


stocks = requests.get("https://stockanalysis.com/stocks/")
stocks = BeautifulSoup(stocks.text, features="lxml")

stocks_clean = []
for li in stocks.findAll("li"):
    for a in li.find("a"):
        stocks_clean.append(a)


# manually checked
del stocks_clean[0:12]
del stocks_clean[-17:]


stocks_dict = []
for stock in stocks_clean:
    stocks_dict.append(stock.split(" - "))

for i in stocks_dict:
    if len(i) >= 3:
        i[1] = i[1] + " " + i[2]  # not good for i with len 4
        i.pop()

stocks_dict = dict(stocks_dict)


with open("data/stocks_symbol.json", "a") as jsonfile:
    json.dump(stocks_dict, jsonfile)
