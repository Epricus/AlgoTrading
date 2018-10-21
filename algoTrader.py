import os
import pandas as pd
import matplotlib.pyplot as plt
import requests
import json
import numpy as np

import datetime


def gs_factors(tickerId, startDate, endDate):
    if type(tickerId) != str or type(startDate) != str or type(endDate) != str:
        raise "Invalid input type(s), must be strings"

    auth_data = {
        'grant_type'    : 'client_credentials',
        'client_id'     : '01cb40c6847c405fba0dcb9a505ff87a',
        'client_secret' : '7da91ebc0b75187c43c116b5a04dd610dce08e8222bbb2d86b84ca463163ecf8',
        'scope'         : 'read_product_data read_financial_data read_content'
    }
    # create Session instance
    session = requests.Session()
    # make a POST to retrieve access_token
    auth_request = session.post('https://idfs.gs.com/as/token.oauth2', data = auth_data)
    access_token_dict = json.loads(auth_request.text)
    access_token = access_token_dict['access_token']
    # update session headers
    session.headers.update({'Authorization':'Bearer '+ access_token})
    request_url = "https://api.marquee.gs.com/v1/data/USCANFPP_MINI/query"
    request_query = {
                    "where": {
                        "ticker": [tickerId]
                    },
                    "startDate": startDate,
                    "endDate": endDate
               }
    request = session.post(url=request_url, json=request_query)
    results = json.loads(request.text)

    return results


def gs_df(aDict):
    alist = aDict['data']
    compiledDict = {}
    for dicts in alist:
        compiledDict[dicts["date"]] = [dicts['financialReturnsScore']
        , dicts['growthScore'], dicts['multipleScore'], dicts['integratedScore']]
    gs_df = pd.DataFrame.from_dict(compiledDict, orient='index', columns=['Financial Returns Score'
        , 'Growth Score', 'Multiple Score', 'Integrated Score'])
    #creates a data frame where the dates are keys and the financial returns score,
    #growth score, multiple score, and integrated score are the values respectively

    return gs_df

def get_rolling_mean(df, window):
    #return rolling mean of given values, using specified window size
    #Important -- window size is the last x indexes that is used in the calculation
    return df.rolling(window=window).mean()

def get_rolling_std(df, window):
    return df.rolling(window=window).std()

def get_bollinger_bands(rm, rstd):
    #returns upper and lower bb
    upper_band = rm + rstd*2
    lower_band = rm - rstd*2
    return upper_band, lower_band

def plot_data_gs(df, title="Stock Data"):
    ax = df.plot(title=title, fontsize=12)
    ax.set_xlabel("Date")
    if "Price" in df.columns.values.tolist():
        ax.set_ylabel("Price")
    else:
        ax.set_ylabel("Score")
    plt.show()


def get_price_data(tickerId):
    request_url = "https://api.iextrading.com/1.0/stock/" +tickerId+"/chart/6m"
    request = requests.get(request_url)
    results = json.loads(request.text)
    compiledDict = {}
    for adict in results:
        compiledDict[adict['date']] = adict['close']
    price_df = pd.DataFrame.from_dict(compiledDict, orient='index', columns=["Price"])
    return price_df



def main():

    tickerId = input("What is the ticker ID of the stock you are interested in? ")
    now = datetime.datetime.now()
    endDate = str(now)[:10]

    startDate = (datetime.date.today() - datetime.timedelta(6*365/12)).isoformat()






    df = get_price_data(tickerId)
    rm = get_rolling_mean(df, window = 20)
    rst = get_rolling_std(df, window=20)

    upper_band, lower_band = get_bollinger_bands(rm, rst)

    ax = df["Price"].plot(title="Bollinger Bands", label = tickerId)
    rm.plot(label ='rolling mean', ax= ax)
    lower_band.plot(label="lower band", ax=ax)
    upper_band.plot(label="upper band", ax=ax)
    plt.show()
    gs_df(results)

    plot_data_gs(results)
    if results['financialReturnsScore'][-1] > .6 and results['growthScore'][-1] and results['multipleScore'][-1] and  results['integratedScore'][-1] < .3:
        print("BUY")







if __name__== "__main__":
  main()