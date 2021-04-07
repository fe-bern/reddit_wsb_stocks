"""
Getting most discussed stocks from r/wsb hot
"""

import os
from collections import Counter, ChainMap
import json
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv


def get_data():
    """
    Create access to Reddit API and load data from recent threads in r/wsb/hot
    return:
        GET response
    """
    load_dotenv()
    CLIENT_ID = os.getenv("CLIENT_ID")
    SECRET = os.getenv("SECRET")
    data = {"grant_type": "password",
            "username": os.getenv("username"),
            "password": os.getenv("password"),}

    headers = {"User-Agent": "wsb_API/0.0.1"}
    auth = requests.auth.HTTPBasicAuth(CLIENT_ID, SECRET)
    res = requests.post("https://www.reddit.com/api/v1/access_token",
                        auth=auth,
                        data=data,
                        headers=headers,)

    TOKEN = res.json()["access_token"]
    headers["Authorization"] = f"bearer {TOKEN}"

    wsb_hot = requests.get("https://oauth.reddit.com/r/wallstreetbets/hot",
                            headers=headers)

    return wsb_hot


wsb_hot = get_data()

df = pd.DataFrame()
for post in wsb_hot.json()["data"]["children"]:
    df = df.append({"subreddit": post["data"]["subreddit"],
                    "title": post["data"]["title"],
                    "selftext": post["data"]["selftext"],},
                    ignore_index=True,)


def extract_sym(Series):
    """
    Extracts all word with 3 or more capital letters !!! Should work also with
                                                    2 Character stock symbols
        pass
    params :Series:
        pd.Series
    return:
        list of stock symbols
    """
    symbols = []
    for i in Series:
        symbols.append(re.findall("[A-Z]{3,}", i))

    return symbols


df["sym_title"] = extract_sym(df.title)
df["sym_text"] = extract_sym(df.selftext)

df["stocks"] = df["sym_title"] + df["sym_text"]


def get_stocks_with_count(Series):
    """
    Count all mentioned stocks
    params: Series
        p.Series
    return:
        dict with stock symbol and total count
    """
    j = 0

    c = []
    d = []
    for i in Series:
        c.append(Counter(Series.loc[j]).items())
        for i in c:
            d.append(dict(c[j]))
        j += 1
    return d


d = get_stocks_with_count(df.stocks)

# from stocks_with_symbol.py
with open("data/stocks_symbol.json") as json_file:
    stocks_dict = json.load(json_file)


def data_wrangling(dict_stock):
    """
    Prep for final df
    params: dict_stock
        dictionary with symbols and count
    return:
        final df
    """
    df_stocks = dict(ChainMap(*dict_stock))
    df_stocks = pd.Series(df_stocks).to_frame()
    df_stocks["Stocks_Name"] = df_stocks.index.map(stocks_dict)
    df_stocks.dropna(inplace=True)
    df_stocks = df_stocks.rename(columns={0: "Count"})
    df_stocks.sort_values(by=["Count"], ascending=False, inplace=True)
    print(df_stocks)
    return df_stocks


if __name__ == "__main__":
    data_wrangling(d)
