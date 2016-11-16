import numpy as np
from datetime import timedelta


def indicatrice_function(current, expected):
    if current == expected:
        return 1
    return 0.01


def absoluteGradeFun(forecastValue, finalPrice):
    if forecastValue == finalPrice:
        return 1

    if forecastValue < finalPrice:
        return forecastValue/finalPrice
    return finalPrice/forecastValue


def getRealPrice(pred, prices):

    horizon = pred['HORIZON']
    crtMnth = pred['MONTH']
    forecastMonth = crtMnth+horizon

    try:
        line = prices.loc[forecastMonth]
    except:
        return -1, 0

    if len(line) == 0:
        line = prices.loc[crtMnth+horizon:crtMnth+horizon+3]
        goodLine = line.head(1)
        forecastMonth = goodLine.index.item()
    else:
        goodLine = line
    if len(line) == 0:
        return -1, 0

    return goodLine['PRC'].item(), forecastMonth


def gauss_function(x, a, x0, sigma):
    return a*np.exp(-(x-x0)**2/(2*sigma**2))


def limitValue(value, minA, maxA):
        value = max(minA, value)
        value = min(maxA, value)
        return value


def getPriceFromHorizon(init_date, horizon, prices):
    start_date = init_date + timedelta(days=horizon*30-31)
    end_date = init_date + timedelta(days=horizon*30)
    mask = (prices['DATE'] > start_date) & (prices['DATE'] <= end_date)
    return prices.loc[mask]


def getMergedGrades(allGrades, newGrades):

    if allGrades is None:
        return newGrades
    else:
        return allGrades.append(newGrades)

def grade(preds, prices, i):

    currentPred = preds.loc[i]

    value, date = getRealPrice(currentPred, prices)
    if value == -1:
        return -1, 0

    pred = currentPred['VALUE']
    finalGrade = absoluteGradeFun(pred, value)
    return finalGrade, date
