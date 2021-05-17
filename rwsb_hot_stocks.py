"""
Getting most discussed stocks from r/wallstreetbets hot
"""

import json
import os
import re
import time
from collections import ChainMap, Counter
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
SECRET = os.getenv("SECRET")
data = {
    "grant_type": "password",
    "username": os.getenv("username"),
    "password": os.getenv("password"),
}

headers = {"User-Agent": "wsb_API/0.0.1"}
auth = requests.auth.HTTPBasicAuth(CLIENT_ID, SECRET)


def get_data(auth, data, headers):
    """
    Create access to Reddit API and load data from recent threads in r/wsb/hot
    auth:
        HTTP Authentication with Client_ID and Secret
    data:
        Access to Reddit via username and password
    headers:
        Extra information about the request
    return:
        GET response
    """
    res = requests.post(
        "https://www.reddit.com/api/v1/access_token",
        auth=auth,
        data=data,
        headers=headers,
    )

    TOKEN = res.json()["access_token"]
    headers["Authorization"] = f"bearer {TOKEN}"

    response = requests.get(
        "https://oauth.reddit.com/r/wallstreetbets/hot",
        headers=headers
    )

    return response


wsb_hot = get_data(auth, data, headers)

df = pd.DataFrame()
for post in wsb_hot.json()["data"]["children"]:
    df = df.append(
        {
            "subreddit": post["data"]["subreddit"],
            "title": post["data"]["title"],
            "selftext": post["data"]["selftext"],
        },
        ignore_index=True,
    )


def extract_sym(series):  # Should work also with 2 Character stock symbols
    """
    Extracts all word with 3 or more capital letters
    params :series:
        pd.Series
    return:
        list of stock symbols
    """
    symbols = []
    for i in series:
        symbols.append(re.findall("[A-Z]{3,}", i))

    return symbols


df["sym_title"] = extract_sym(df.title)
df["sym_text"] = extract_sym(df.selftext)

df["stocks"] = df["sym_title"] + df["sym_text"]


def get_stocks_with_count(series):
    """
    Count all mentioned stocks
    params: Series
        p.Series
    return:
        dict with stock symbol and total count
    """
    j = 0

    counter_list = []
    dict_list = []
    for i in series:
        counter_list.append(Counter(series.loc[j]).items())
        for i in counter_list:
            dict_list.append(dict(counter_list[j]))
        j += 1
    return d


stocks_counter = get_stocks_with_count(df.stocks)

# this json is from stocks_with_symbol.py
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
    while True:
        print(datetime.now())
        data_wrangling(stocks_counter)
        time.sleep(300)
