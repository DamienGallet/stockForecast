import numpy as np
import pandas as pd
import driver as drv
from utilities import *
import interface as xit
import ploting_utilities
import math

MONTH_BEG = 1150
MONTH_END = 1450


def getPredsOfDate(preds, monthBeg, monthEnd, company):
    maskGradesMonth = ((preds['MONTH'] >= monthBeg)
                      & (preds['MONTH'] <= monthEnd))
    try:
        return preds.loc[maskGradesMonth]
    except:
        return []

def getPriceOfDate(prices, monthBeg, monthEnd, company):
    maskGradesMonth = ((prices.index >= monthBeg)
                      & (prices.index <= monthEnd))
    try:
        val = prices.loc[maskGradesMonth]['PRC'].values[0]
        return val
    except:
        return 0


def shortForecast(prices, predsP, company):

    forecast = pd.DataFrame(columns=['MONTH','VARIATION','FORECAST','STD'],
                            index=['MONTH'])

    # month is the month of the forecast
    for month in range(MONTH_BEG,MONTH_END):

        preds = getPredsOfDate(predsP, month-2, month-2, company)
        price = getPriceOfDate(prices, month-2,month-2, company)

        if price is None or price == 0 or len(preds) == 0:
            continue

        standardDeviation = preds['VALUE'].std()
        mean = preds['VALUE'].mean()

        variation = mean-price
        forecastV = price + variation

        forecast.loc[month] = [month,variation,forecastV,standardDeviation]
    forecast.fillna(0)
    return forecast


def plotShortTerm(prices, forecast,company):

    datesF = list(forecast.index.values)[1:]
    datesP = list(prices.index.values)

    valuesF = list(forecast['FORECAST'].values)[1:]
    valuesP = list(prices['PRC'].values)

    variation = list(forecast['VARIATION'].values)
    print(forecast)

    ploting_utilities.plots2D([datesP,datesF],
                              [valuesP,valuesF],
                              [None,variation],
                              [False,True],
                              company)


def computeAndPlotShort(prices, preds, company):
    forecast = shortForecast(prices, preds, company)
    plotShortTerm(prices,forecast,company)

